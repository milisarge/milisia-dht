/*
 * Copyright © 2017 Simon Désaulniers
 * Author: Simon Désaulniers <sim.desaulniers@gmail.com>
 * 		   Milisarge <milisarge@gmail.com>
 *
 * Bu program özgür yazılımdır: 
 * Özgür Yazılım Vakfı(Free Software Foundation) tarafından yayımlanan 
 * GNU Genel Kamu Lisansı’nın sürüm 3 veya
 * isteğinize bağlı olarak daha sonraki sürümlerinin hükümleri altında 
 * yeniden dağıtabilir ve/veya değiştirebilirsiniz.
 * Bu program, yararlı olması umuduyla dağıtılmış olup, programın BİR TEMİNATI YOKTUR; 
 * TİCARETİNİN YAPILABİLİRLİĞİNE VE ÖZEL BİR AMAÇ İÇİN UYGUNLUĞUNA dair bir teminat da vermez. 
 * Ayrıntılar için GNU Genel Kamu Lisansı’na göz atınız.
 * Bu programla birlikte GNU Genel Kamu Lisansı’nın bir kopyasını elde etmiş olmanız gerekir. 
 * Eğer elinize ulaşmadıysa <http://www.gnu.org/licenses/> adresine bakınız. 
*/

#pragma once

#include <cstdint>
#include <string>
#include <memory>

#include <opendht/dhtrunner.h>
#include <opendht/value.h>
#include <opendht/infohash.h>
#include <opendht/rng.h>
#include <opendht/callbacks.h>

namespace Milis {

class Node {
    static const constexpr char* DEFAULT_BOOTSTRAP_NODE = "bootstrap.ring.cx";
    static const constexpr char* DEFAULT_BOOTSTRAP_PORT = "4222";
    static const constexpr char* CONNECTION_FAILURE_MSG = "err.. Failed to connect to the DHT.";
    static const constexpr char* OPERATION_FAILURE_MSG = "err.. DHT operation failed.";

public:
    using PastedCallback = std::function<void(std::vector<dht::Blob>)>;

    Node() {}
    virtual ~Node () {}

    void run(uint16_t port = 0, std::string bootstrap_hostname = DEFAULT_BOOTSTRAP_NODE, std::string bootstrap_port = DEFAULT_BOOTSTRAP_PORT) {
        if (running_)
            return;
        node_.run(port, dht::crypto::generateIdentity(), true);
        node_.bootstrap(bootstrap_hostname, bootstrap_port);
        running_ = true;
    };

    void stop() {
        std::condition_variable cv;
        std::mutex m;
        std::atomic_bool done {false};

        node_.shutdown([&]()
        {
            std::lock_guard<std::mutex> lk(m);
            done = true;
            cv.notify_all();
        });

        // wait for shutdown
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, [&](){ return done.load(); });

        node_.join();
    }

    /**
     * Pastes a blob on the DHT under a given code. If no callback, the function
     * blocks until pasting on the DHT is done.
     *
     * @param blob  The blob to paste.
     * @param cb    A function to execute when paste is done. If empty, the
     *              function will block until done.
     *
     * @return true if success, else false.
     */
    bool put(const std::string& code, dht::Blob&& blob, dht::DoneCallbackSimple&& cb = {});

    /**
     * Recover a blob under a given code.
     *
     * @param code  The code to lookup.
     * @param cb    A function to execute when the pasted blob is retrieved.
     */
    void get(const std::string& code, PastedCallback&& cb);

    /**
     * Recover blob values under a given code. This function blocks until the
     * DHT has satisfied the request.
     *
     * @param code  The code to lookup.
     *
     * @return the blobs.
     */
    std::vector<dht::Blob> get(const std::string& code);

private:

    dht::DhtRunner node_;
    bool running_ {false};

    std::uniform_int_distribution<uint32_t> codeDist_;
    std::mt19937_64 rand_;
};

} /* dpaste */

