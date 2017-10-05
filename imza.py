import gnupg
import os
import os.path
import shutil
import codecs
import subprocess

MESAJLAR="./mesajlar/"

def imza_kontrol(konum,dosya):
	print(dosya)
	sgd="/tmp/"+dosya+".cikti"
	dogrulama="/tmp/"+dosya+".dogrula"
	os.system("rm -rf "+sgd)
	os.system("rm -rf "+dogrulama)
	os.system("gpg --output "+sgd +" "+konum+dosya)
	#os.system("gpg2 --status-fd 1 --no-default-keyring --keyring pubring.kbx --trust-model always --verify "+dosya+" > "+dogrulama)
	os.system("gpg --status-fd 1 --no-default-keyring --verify "+konum+dosya+" > "+dogrulama)
	yol=konum+dosya
	gonderen="anonim"
	gonderen_onay="geçersiz"
	with open(dogrulama) as f:
		satirlar = f.readlines()
	durum=False
	#print (yol)
	if os.path.isfile(sgd):
		yol=sgd
		durum=True
		for satir in satirlar:
			if "ERRSIG" in satir:
				gonderen=satir.split()[2]
				break
			if "GOODSIG" in satir:
				gonderen=satir.split()[-1]
				gonderen_onay="geçerli"
				break
	os.system("rm -rf "+dogrulama)
	return durum,yol,gonderen,gonderen_onay
	
durum,icerikyol,gonderen,gonderen_onay=imza_kontrol(MESAJLAR,"7e201c93c2e3a9599bbc907c2e77e0df2d84abb047786dc652e21a5226208514")	

print(durum,icerikyol,gonderen,gonderen_onay)
