#! /bin/sh
mesaj="$1"
gdosya=$(mktemp)
echo $mesaj > $gdosya
ydosya=$(md5sum $gdosya | cut -d' ' -f1)
cp -rf $gdosya ./smesajlar/$ydosya
