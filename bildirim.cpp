/*
 * Copyright © 2017 Milis Linux
 * Author: Milisarge <milisarge@gmail.com>
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "node.h"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <utility>
#include <getopt.h>
#include "sha2.h"


static const constexpr char* MESAJLAR = "mesajlar/";
static std::string BILDIRIM_ANAHTAR = "milbis-bildirim";
static std::string AMESAJ_LISTE = "ag.liste";
static std::string YMESAJ_LISTE = "yerel.liste";
static std::string BESLEME_LISTE = "besleme.liste";
static bool KMTBLG = false;
static const constexpr char* SIL = "rm -f ";

bool OTO_BESLEME = true;

bool gonder(Milis::Node& node,std::string& anahtar,std::string icerik){
	dht::Blob blob {icerik.begin(), icerik.end()};
    auto sonuc=node.put(anahtar, std::move(blob));
    return sonuc;
}

void yerel_liste_olustur(){
	std::string komut="";
	komut+=SIL;
	komut+=YMESAJ_LISTE;
	int status=std::system(komut.c_str());	
	komut="ls ";
	komut+=" ";
	komut+=MESAJLAR;
	komut+=" > ";
	komut+=YMESAJ_LISTE;
	if (KMTBLG){
		std::cout << komut.c_str() << " <<<< " << status << std::endl;	
	}
	std::system(komut.c_str());	
	komut="sort -u "+YMESAJ_LISTE;
	komut+=" > /tmp/"+YMESAJ_LISTE;
	std::system(komut.c_str());	
}

void besleme_liste_olustur(){
	std::string komut="";
	if (std::ifstream("/tmp/"+AMESAJ_LISTE))
	{	
		//comm -3 /tmp/yerel.liste /tmp/ag.liste | sed 's/^\t//'
		komut+="comm -3 ";
		komut+="/tmp/"+YMESAJ_LISTE;
		komut+=" ";
		komut+="/tmp/"+AMESAJ_LISTE;
		komut+=" | sed 's/^\t//' > "+BESLEME_LISTE;
		
	}else{	
		komut+="cp  ";
		komut+="/tmp/"+YMESAJ_LISTE;
		komut+=" "+BESLEME_LISTE;
	}
	int status=std::system(komut.c_str());	
	if (KMTBLG){
		std::cout << komut.c_str() << " <<<< " << status << std::endl;	
	}
}	

std::string dosya_icerik_al(std::string& dosya){
	char ch;
	std::fstream icerikStream(MESAJLAR+dosya, std::fstream::in);
	std::stringstream oss;
	while (icerikStream.get(ch))
	{
		oss << ch;
	}
	return oss.str();
}

void ag_mesaj_sirala(){
	std::string komut="";
	komut="sort -u "+AMESAJ_LISTE;
	komut+=" > /tmp/"+AMESAJ_LISTE;
	int status = std::system(komut.c_str());
	if (KMTBLG){
		std::cout << komut.c_str() << " <<<< " << status << std::endl;	
	}
}

void besleme_yap(Milis::Node& node){
	char ch;

	std::fstream icerikStream(BESLEME_LISTE, std::fstream::in);
	//std::cout << "************************************" << std::endl;	
	std::stringstream oss;
	std::string bdosya;
	std::string icerik="";
	while (icerikStream.get(ch))
	{
		if (ch == '\n'){
			std::cout << oss.str() << "\n" << std::endl;
			oss >> bdosya;
			icerik=dosya_icerik_al(bdosya) ;
			if (sha256(icerik) == bdosya){
				std::cout << "içerik doğrulandı-besleme yapılıyor." << std::endl;
				//dosya içeriğinin beslenmesi
				//auto sonuc_ic=gonder(node,bdosya,icerik);
				dht::Blob blob2 {icerik.begin(), icerik.end()};
				auto sonuc_ic=node.put(bdosya, std::move(blob2));
				std::cout << sonuc_ic << ":icerik besleme" << std::endl;
				//dosya isminin beslenmesi
				if(sonuc_ic){
					std::cout << "<<<<dosya içerik besleme yapıldı>>>>" << std::endl;
					//auto sonuc=gonder(node,BILDIRIM_ANAHTAR,bdosya);
					dht::Blob blob {bdosya.begin(), bdosya.end()};
					auto sonuc=node.put(BILDIRIM_ANAHTAR, std::move(blob));
					std::cout << sonuc << ":isim besleme" << std::endl;
					if(sonuc){
						std::cout << "<<<<dosya isim besleme yapıldı>>>>" << std::endl;
					}else{
						std::cout << "<<<<dosya isim besleme olumsuz>>>>" << std::endl;
					}
				}else{
					std::cout << "<<<<dosya içerik  besleme olumsuz>>>>" << std::endl;
				}
				
			}else{
				std::cout << "içerik uyumsuz" << std::endl;
			} 
			//içerik yazdırılmak istenirse
			//std::cout << icerik << std::endl;
			oss.str("");	
			oss.clear();
		}else{
			oss << ch;
		}
		
	}
	//std::cout << "************************************" << std::endl;	

}

void ag_liste_temizle(){
	std::string komut="";
	komut+=SIL;
	komut+=AMESAJ_LISTE;
	int status=std::system(komut.c_str());
	if (KMTBLG){
		std::cout << komut.c_str() << " <<<< " << status << std::endl;	
	}
	komut="";
	komut+=SIL;
	komut+="/tmp/";
	komut+=AMESAJ_LISTE;
	status=std::system(komut.c_str());
	if (KMTBLG){
		std::cout << komut.c_str() << " <<<< " << status << std::endl;	
	}
}	

void icerik_arama(Milis::Node& node,std::string& aranan){
	std::stringstream oss;
	auto values = node.get(aranan);
	if (not values.empty()) {
		std::ofstream ofs(MESAJLAR+aranan);
		auto& b = values.front();
		ofs << std::string(b.begin(), b.end());
		oss << std::string(b.begin(), b.end());
		std::cout << oss.str() << std::endl;
	}else{
		std::cout << aranan << " içerik arama bulunamadı!" << std::endl;
	}
}



void arama(Milis::Node& node,std::string& aranan){
	
	auto values = node.get(aranan);
	if (not values.empty()) {
		std::string komut="";
		//komut+=SIL;
		//komut+=AMESAJ_LISTE;
		//std::system(komut.c_str());
		std::ofstream ofs(AMESAJ_LISTE);
		
		for(int i=0; i < values.size(); i++){
			std::stringstream oss;
			auto& b = values[i];
			oss << std::string(b.begin(), b.end());
			ofs << std::string(b.begin(), b.end());
			ofs << "\n";
			std::string icerik_anahtar=oss.str();
			//ofs << icerik_anahtar;
			std::cout << "bulunan_mesaj_anahtarlar:" << icerik_anahtar << std::endl;
			if (std::ifstream(MESAJLAR+icerik_anahtar))
			{
				std::cout << icerik_anahtar << " zaten dosya mevcut!" << std::endl;
			}else{
				std::cout << icerik_anahtar << " Mesaj dosyası içerik oluşturulacak." << std::endl;
			    icerik_arama(node,icerik_anahtar);
			}
		}
	}else{
		std::cout << aranan << " anahtar arama bulunamadı!" << std::endl;
	}

}


//Main
int main(int argc, char *argv[]) {
    std::string aranan,anahtar,deger;
    int beklenecek_sn;
    beklenecek_sn=10;
    int m_dizin= system("mkdir -p mesajlar");
    if (m_dizin){return 0;}
    //std::cout << dht::InfoHash::get(BILDIRIM_ANAHTAR) << std::endl; 
    std::cout << "aranan=" << BILDIRIM_ANAHTAR <<  ": " << dht::InfoHash::get(BILDIRIM_ANAHTAR) << std::endl; 
    
    Milis::Node node;
    node.run();
    Milis::Node nodeB;
    nodeB.run();
    while(true){
		std::cout << "aranan hash:" << BILDIRIM_ANAHTAR << std::endl;
		ag_liste_temizle();
		arama(node,BILDIRIM_ANAHTAR);
		// besleme
		if (OTO_BESLEME){
			//std::cout << "otobesleme yapılacak" << std::endl;
			yerel_liste_olustur();
			ag_mesaj_sirala();
			besleme_liste_olustur();
			besleme_yap(nodeB);
			
			//gonder(node,anahtar,deger);
		}else{
			std::cout << "otobesleme yok" << std::endl;
		}
		//uyutma
		std::cout << beklenecek_sn << " sn uyuyor...................." << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(beklenecek_sn));
	}
	node.stop();
	nodeB.stop();

    return 0;
}

