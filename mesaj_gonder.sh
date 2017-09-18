#! /bin/sh
mesaj_tip="$1"
mesaj_icerik="$2"
if [ "$1" = "-b" ];then
	mesaj_tip="bilgi"
elif [ "$1" = "-s" ];then
	mesaj_tip="sistem"
else
	echo "mesaj tipi yanlış!";echo "mesaj_gonder.sh  -b|-s  mesaj_icerik";exit 0
fi
zaman=`date +%m-%d-%y.%H:%M:%S`
mesaj="$1"
gdosya=$(mktemp)
echo "mesaj_tipi : ${mesaj_tip}" > $gdosya
echo "mesaj_icerik : ${mesaj_icerik}" >> $gdosya
echo "tarih : $zaman" >> $gdosya
ydosya=$(md5sum $gdosya | cut -d' ' -f1)
cp -rf $gdosya ./smesajlar/$ydosya
