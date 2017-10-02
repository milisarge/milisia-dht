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

#include <algorithm>
#include <random>
#include <future>

#include <opendht.h>

#include "node.h"

namespace Milis {


bool Node::put(const std::string& code, dht::Blob&& blob, dht::DoneCallbackSimple&& cb) {
    auto v = std::make_shared<dht::Value>(std::forward<dht::Blob>(blob));

    auto hash = dht::InfoHash::get(code);

    if (cb) {
        node_.put(hash, v, cb);
        return true;
    } else {
        std::mutex mtx;
        std::condition_variable cv;
        std::unique_lock<std::mutex> lk(mtx);
        bool done, success_ {false};
        node_.put(hash, v, [&](bool success) {
            if (not success)
                std::cerr << OPERATION_FAILURE_MSG << std::endl;
            else
                success_ = true;
            {
                std::unique_lock<std::mutex> lk(mtx);
                done = true;
            }
            cv.notify_all();
        });
        cv.wait(lk, [&](){ return done; });
        return success_;
    }
}

void Node::get(const std::string& code, PastedCallback&& pcb) {
    auto blobs = std::make_shared<std::vector<dht::Blob>>();
    node_.get(dht::InfoHash::get(code),
        [blobs](std::shared_ptr<dht::Value> value) {
            blobs->emplace_back(value->data);
            return true;
        },
        [pcb,blobs](bool success) {
            if (not success)
                std::cerr << OPERATION_FAILURE_MSG << std::endl;
            else if (pcb)
                pcb(*blobs);
        });
}

std::vector<dht::Blob> Node::get(const std::string& code) {
    auto values = node_.get(dht::InfoHash::get(code)).get();
    std::vector<dht::Blob> blobs (values.size());
    std::transform(values.begin(), values.end(), blobs.begin(), [] (const decltype(values)::value_type& value) {
        return value->data;
    });
    return blobs;
}

} 

