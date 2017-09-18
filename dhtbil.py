#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# Copyright (c) 2017 Milis İşletim Sistemi
# Author: milisarge
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

import os
import time
import sys
from urllib.parse import urlparse
import json
import subprocess
import hashlib
import socket
import uuid 
import base64, json
from opendht import *
import opendht as dht
import threading, time
from random import randint

class Dht():
   
   def __init__(self,port=None,bs=None):
      self.sunucu_isim="milisia-dht"
      if bs is None:
         self.sunucu="bootstrap.ring.cx:4222"
      else:
         self.sunucu=bs
      self.id = Identity()
      self.id.generate()
      self.node = DhtRunner()
      if port is None:
         port=randint(60000,65000)
      
      self.node.run(self.id, port=port)
      bss=self.sunucu.split(":")[0]
      bsp=self.sunucu.split(":")[1]
      self.node.bootstrap(bss,bsp)

   def hash_al(self,anahtar):
      sha1 = hashlib.sha1()
      sha1.update(anahtar.encode())
      anahtar_hash=sha1.hexdigest()
      return anahtar_hash
		
   def kayit_edildi(self):
      time.sleep(10)
      print ("--------")
		
   def sunucuya_kayit(self,deger,anahtar=None,gorev_bitince="sonlan"):
      #ahash=self.hash_al(anahtar)
      if anahtar is None:
         anahtar=self.sunucu_isim
      time.sleep(1)
      sonuc=self.node.put(dht.InfoHash.get(anahtar),dht.Value(deger.encode()))
      #dht dugumunu durdurmak için
      if gorev_bitince == "sonlan":
          self.node=None
      return sonuc

   def sunucular(self,anahtar=None):
      liste=[]
      #arama saniyesi
      arasn=10
      print ("(%s) altında %s saniye arama yapılacak!" % (self.sunucu,arasn))
      if anahtar is None:
         anahtar=self.sunucu_isim
         bitis = 1
      while bitis > 0:
         bitis += 1
         veriler=(self.node.get(InfoHash.get(anahtar)))
         for veri in veriler:
            sunbilgi=(veri.data).decode('ascii')
            if sunbilgi not in liste:
               liste.append(sunbilgi)
               print (len(liste)," adet kayıt bulundu.",sunbilgi)
         time.sleep(1)
         if bitis == arasn:
            print ("dht sunucu tarama sonlandırıldı.")
            break
      return liste
		
   def ara(self,anahtar=None,arasn=1):
      liste=[]
      #arama saniyesi
      print ("(%s) altında %s saniye arama yapılacak!" % (self.sunucu,arasn))
      if anahtar is None:
         anahtar="arama"
      bitis = 1
      while bitis > 0:
         bitis += 1
         veriler=(self.node.get(InfoHash.get(anahtar)))
         for veri in veriler:
            bilgi=(veri.data).decode('utf-8')
            if bilgi not in liste:
               liste.append(bilgi)
               print (len(liste)," adet kayıt bulundu.",bilgi)
         time.sleep(1)
         if bitis == arasn:
            print ("dht sunucu tarama sonlandırıldı.")
            break
      return liste
   
   def icerik_ara(self,anahtar=None,arasn=1):
      sonuc=""
      #arama saniyesi
      print ("(%s) altında %s saniye %s araması yapılacak!" % (self.sunucu,arasn,"bildirim içeriği"))
      if anahtar is None:
         anahtar="arama"
      bitis = 1
      while bitis > 0:
         bitis += 1
         veriler=(self.node.get(InfoHash.get(anahtar)))
         if veriler:
            veri=veriler[0]
            sonuc=(veri.data).decode('utf-8')
            print ("adet kayıt bulundu.",sonuc)
            return sonuc
         time.sleep(1)
         if bitis == arasn:
            print ("dht sunucu tarama sonlandırıldı.")
            break
            
   def mliste_al(self):
      liste=[]
      for mesajd in os.listdir(MESAJ_DIZINI):
         dosya=os.path.basename(mesajd)
         liste.append(dosya)
      return liste
      
   def bildirim_ara(self,anahtar=None,arasn=1):
      mliste=self.mliste_al()
      liste=[]
      #arama saniyesi
      print ("(%s) altında %s saniye %s araması yapılacak!" % (self.sunucu,arasn,"yeni bildirim"))
      if anahtar is None:
         anahtar="arama"
      bitis = 1
      while bitis > 0:
         bitis += 1
         bildirimler=(self.node.get(InfoHash.get(anahtar)))
         for bildirim in bildirimler:
            b_isim=(bildirim.data).decode('ascii')
            if b_isim not in mliste:
               liste.append(b_isim)  
         time.sleep(1)
         if bitis == arasn:
            print ("dht sunucu tarama sonlandırıldı.")
            break
      return liste

#meshnet ağı aktiv olursa kayıt yapılacak.
HOST = "::ffff:127.0.0.1"
PORT = 9009
MESAJ_DIZINI="./mesajlar/"
SMESAJ_DIZINI="./smesajlar/"
BILDIRIM_SURE=10000
os.makedirs(MESAJ_DIZINI, exist_ok=True)
os.makedirs(SMESAJ_DIZINI, exist_ok=True)

#none olursa öntanımlı bootstrap.ring.cx i kullanır
dhtsunucu=None #"192.168.43.207:4222"
kimlik=str(uuid.UUID(int=uuid.getnode()))
kimlik=kimlik.split("-")[4]
		
def ilet(baslik="dht-ileti",message="",sure=3000):
  subprocess.Popen(['notify-send',"--expire-time="+str(sure),baslik, message])
  return

def dht_kayit_islemi():
  while 1:
      anahtar="milbis-kayit"
      #meshnet için yerel sunucu kaydında
      #bilgi=str(HOST)+":"+str(PORT)
      bilgi=kimlik
      #sunucu dht ye kayıt edilecek.
      #dhtkyt=Dht(bs=dhtsunucu)
      dhtkyt=Dht()
      # 5e0f45714af94cf735f51ffba0648a0e77ff4297 milbis-kayit
      # bildirim istemcisini milbis-kayit anahtarıyla dht kaydını yapıyoruz.
      if dhtkyt.sunucuya_kayit(bilgi,anahtar):
          print("Sunucu milbis-dht",anahtar,":",kimlik,dhtkyt.sunucu,"'a kaydı yapıldı.")
      time.sleep(20)
   
def smesajlar_besleme():
  while 1:
     anahtar="milbis-bildirim"
     dhtbes=Dht()
     mesajlar=os.listdir(SMESAJ_DIZINI)
     print ("beslenecekler",mesajlar)
     for mesajd in mesajlar:
         dosya=os.path.basename(mesajd)
         if dhtbes.sunucuya_kayit(dosya,anahtar,"devam"):
             icerik=open(SMESAJ_DIZINI+dosya).read()
             if dhtbes.sunucuya_kayit(icerik,dosya,"devam"):
                 print(dosya,"besleme yapıldı.")
     print ("besleme 20sn uyumada")
     time.sleep(20)
              
#periyodik dht sunucu kaydı için thread tanımlama
dhtkayit = threading.Thread(name='dht_kayit_islemi', target=dht_kayit_islemi)
dhtkayit.setDaemon(True)
dhtkayit.start()

#smesajlar altındaki mesajların beslenmesi
dhtkayit2 = threading.Thread(name='smesajlar_besleme', target=smesajlar_besleme)
dhtkayit2.setDaemon(True)
dhtkayit2.start()

#milisia sunucuları bulmak için (milisia-sunucu) anahtarıyla.
#dht2=Dht(bs=dhtsunucu)
#sunucular=dht2.sunucular()

while True: 
   #bildirim kontrolu yapılacak.
   dht2=Dht(bs=dhtsunucu)
   dht3=Dht(bs=dhtsunucu)
   # 8c798d6f0867e8cbdb7f565e9e95388796ef1542 milbis-bildirim
   bildirimler=dht2.bildirim_ara("milbis-bildirim",arasn=3)
   bildirimler=set(bildirimler)
   if len(bildirimler) > 0:
      for bildirim in bildirimler:
         print (bildirim,"icerik aranıyor")
         bildirim_icerik=dht3.icerik_ara(bildirim,arasn=3)
         if bildirim_icerik :
             open(MESAJ_DIZINI+bildirim,"w").write(bildirim_icerik) 
             ilet("ileti",bildirim_icerik,BILDIRIM_SURE)
             print (bildirim,"icerik bulundu--->",bildirim_icerik)
         else:	
             print (bildirim,"icerik bulunamadı!")
   time.sleep(1) 	
   print(".")

