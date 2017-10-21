# Milisia Ağı Birebir(P2P) DHT Tabanlı Haberleşme 

* Kademlia DHT kütüphanesi(<a href=https://github.com/savoirfairelinux/opendht>opendht</a>) kullanılarak durdurulamayan,uygulamayı kullananlar tarafından sürekli beslenebilen mesajlaşma altyapısı oluşturulmuştur.
* Bunun ilk etapta Milis Linux için toplu iletimde bulunabilen bildirim sistemi olarak kullanılması öngörülmüştür.
* Bildirimler anonim gönderilebildiği gibi imzalı olarak ta gönderilebilinir.
* Bildirim oluşturulan kullanıcı tarafından ilk beslemesi yapılıp ağa kayıt edilir.
* Beslenmekte olan bildirimler uygulamayı açan her ilk kullanıcıya ulaşmaktadır.
* Bildirimi alan kullanıcılar şayet bildirimin ağdaki beslemesi kesilmişse bildirimi besleyebilmektedirler.
* Bildirimler anonim,imzalı geçersiz,imzalı geçerli olmak üzere 3 tipten oluşur.
* Bildirim tipleri Arayüz ayarlarından alımı ve beslemesi filtrelenebilinir.

## Gerekli Kütüphaneler

* Opendht
* Python3-Qt5

## Çalıştırma
 
 ./arayuz.py
 
 
