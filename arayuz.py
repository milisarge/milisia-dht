#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2017 Milis İşletim Sistemi
# Author: sonakinci41
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QApplication, QListView,
                             QDesktopWidget, QSystemTrayIcon, QMenu, QAction, qApp)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QSettings, QTimer
from PyQt5.QtGui import QIcon
import os, yaml, sys, subprocess
from ui import listemadddesi, ayarlarui, gonder


class Okuyucu(QDialog):
    MESAJ_DIZINI = "./mesajlar/"
    BILDIRIM_SUREC= os.getcwd()+"/"+"bildirim"
    BILDIRIM_SUREC_KAPAT= "killall -9 "+os.getcwd()+"/"+"bildirim"
    def __init__(self, ebeveyn=None):
        super(Okuyucu, self).__init__(ebeveyn)
        kutu = QVBoxLayout()
        self.setLayout(kutu)
        kutu.setContentsMargins(0, 0, 0, 0)

        self.sistem_cekmecesi = QSystemTrayIcon(self)
        self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim.png"))
        self.sistem_cekmecesi.activated.connect(self.sistem_cekmecesi_tiklandi)
        self.sistem_cekmecesi.show()

        self.menu_cekmece = QMenu(self)
        self.mesaj_oku_aksiyon = QAction("Mesaj Oku", self, statusTip="MesajOku", triggered=self.mesaj_oku_fonk)
        self.mesaj_gonder_aksiyon = QAction("Mesaj Gönder", self, statusTip="MesajGonder",
                                            triggered=self.mesaj_gonder_fonk)
        self.ayarlar_aksiyon = QAction("Ayarlar", self, statusTip="Ayarlar", triggered=self.ayarlar_fonk)
        self.kapat_aksiyon = QAction("Kapat", self, statusTip="Kapat", triggered=self.kapat_fonk)
        self.menu_cekmece.addAction(self.mesaj_oku_aksiyon)
        self.menu_cekmece.addAction(self.mesaj_gonder_aksiyon)
        self.menu_cekmece.addAction(self.ayarlar_aksiyon)
        self.menu_cekmece.addAction(self.kapat_aksiyon)
        self.sistem_cekmecesi.setContextMenu(self.menu_cekmece)
        self.sistem_cekmecesi.showMessage("Çalıştı", "Milis Bildirim Başarıyla Çalıştırıldı",
                                          QSystemTrayIcon.MessageIcon(1), 5000)

        self.mesaj_liste = QListWidget()
        self.mesaj_liste.setSelectionMode(QListView.ExtendedSelection)
        kutu.addWidget(self.mesaj_liste)

        self.setFixedWidth(285)
        s = QDesktopWidget().screenGeometry(0)
        self.setFixedHeight(s.height())
        self.setWindowFlags(Qt.Popup)
        self.move(s.width() - 285, 0)

        ################################
        self.settings = QSettings()
        self.okunmus_mesajlar = self.settings.value("liste", [], str) or []
        self.tum_mesajlar = os.listdir(self.MESAJ_DIZINI)
        self.varolan_mesajlar = []
        try:
            self.gecersizleri_goster = int(self.settings.value("gecersizleri_goster"))
            self.anonimleri_goster = int(self.settings.value("anonimleri_goster"))
        except:
            self.gecersizleri_goster = 1
            self.anonimleri_goster = 1
        ################################
        self.tum_mesajlar_fonk()
        self.dosya_izleyici = QFileSystemWatcher()
        self.dosya_izleyici.addPath(self.MESAJ_DIZINI)
        self.dosya_izleyici.directoryChanged.connect(self.tum_mesajlar_fonk)
        #################################
        # Bildirim çalıştırılıyor       #
        #################################
        zamanlayici = QTimer(self)
        zamanlayici.setInterval(6000)
        zamanlayici.timeout.connect(self.bildirim_calistir)
        zamanlayici.start()


    def mesaj_gonder_fonk(self):
        pencere_gonder = gonder.Gonderici(self)
        pencere_gonder.show()

    def closeEvent(self, event):
        self.settings.setValue('liste', self.okunmus_mesajlar)
        self.settings.sync()

    def ayarlar_fonk(self):
        ayarlar_pencere = ayarlarui.Ayarlar(self)
        ayarlar_pencere.show()

    def kapat_fonk(self):
        os.system(self.BILDIRIM_SUREC_KAPAT)
        qApp.quit()

    def sistem_cekmecesi_tiklandi(self, value):
        if value == self.sistem_cekmecesi.DoubleClick:
            self.mesaj_oku_fonk()

    def mesaj_oku_fonk(self):
        self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim.png"))
        self.show()

    def bildirim_calistir(self):
        print("######################")
        print(self.surec_kontrol())
        if not self.surec_kontrol():
            subprocess.Popen([self.BILDIRIM_SUREC])


    def surec_kontrol(self):
        _surec = os.popen("ps -Af").read()
        surec_adet = _surec.count(self.BILDIRIM_SUREC)
        if surec_adet > 0:
            return True
        return False
    
    def imza_kontrol(self, konum, dosya):
        sgd = "/tmp/" + dosya + ".cikti"
        dogrulama = "/tmp/" + dosya + ".dogrula"
        os.system("rm -rf " + sgd)
        os.system("rm -rf " + dogrulama)
        os.system("gpg --output " + sgd + " " + konum + dosya)
        os.system("gpg --status-fd 1 --no-default-keyring --verify " + konum + dosya + " > " + dogrulama)
        yol = konum + dosya
        gonderen = "anonim"
        gonderen_onay = "geçersiz"
        with open(dogrulama) as f:
            satirlar = f.readlines()
        durum = False
        if os.path.isfile(sgd):
            yol = sgd
            durum = True
            for satir in satirlar:
                if "ERRSIG" in satir:
                    gonderen = satir.split()[2]
                    break
                if "GOODSIG" in satir:
                    gonderen = satir.split()[-1]
                    gonderen_onay = "geçerli"
                    break
        os.system("rm -rf " + dogrulama)
        return durum, yol, gonderen, gonderen_onay

    def yaml_oku(self, dosya):
        durum, yol, gonderen, gonderen_onay = self.imza_kontrol(self.MESAJ_DIZINI, dosya)
        with open(yol, 'r') as f:
            okunan = yaml.load(f)
        return okunan, gonderen, gonderen_onay

    def tum_mesajlar_fonk(self):
        self.varolan_mesajlar = self.tum_mesajlar
        self.mesaj_liste.clear()

        duzenli_mesajlar = self.mesajlar_oku_sirala()
        mesajlar = duzenli_mesajlar.keys()
        sirali_mesajlar = list(mesajlar)
        sirali_mesajlar.sort()
        sirali_mesajlar = sirali_mesajlar[::-1]
        if len(sirali_mesajlar) != 0:
            for mesaj in sirali_mesajlar:
                mesaj_ = duzenli_mesajlar[mesaj]
                ozel_widget = listemadddesi.OzelListeMaddesi(self)
                ozel_widget.okuyucu()
                ozel_widget.mesaj_id_ekle(mesaj_[2])
                ozel_widget.mesaj_tipi_ekle(mesaj_[0])
                ozel_widget.mesaj_ekle(mesaj_[1])
                ozel_widget.tarih_ekle(mesaj)
                ozel_widget.gonderen_ekle(mesaj_[3])
                ozel_widget.gonderen_onay_ekle(mesaj_[4])
                if mesaj_[2] in self.okunmus_mesajlar:
                    ozel_widget.okunma_degistir("okundu")
                else:
                    ozel_widget.okunma_degistir("okunmadi")
                ozel_widget_item = QListWidgetItem(self.mesaj_liste)
                ozel_widget_item.setSizeHint(ozel_widget.sizeHint())
                self.mesaj_liste.setItemWidget(ozel_widget_item, ozel_widget)

                if mesaj_[2] not in self.varolan_mesajlar:
                    if mesaj_[0] == "bilgi":
                        icon = 1
                    elif mesaj_[0] == "sistem":
                        icon = 2
                    elif mesaj_[0] == "kritik":
                        icon = 3
                    else:
                        icon = 0
                    self.sistem_cekmecesi.showMessage(mesaj_[0], mesaj_[1],
                                                      QSystemTrayIcon.MessageIcon(icon), 5000)
                    self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim-m.png"))

    def mesajlar_oku_sirala(self):
        duzenli_mesajlar = {}
        mesajlar = os.listdir(self.MESAJ_DIZINI)
        self.tum_mesajlar = mesajlar
        for mesaj in mesajlar:
            okunan, gonderen, gonderen_onay = self.yaml_oku(mesaj)
            if gonderen_onay == "geçersiz" and self.gecersizleri_goster == False:
                pass
            elif gonderen == "anonim" and self.anonimleri_goster == False:
                pass
            else:
                if okunan == None:
                    pass
                try:
                    mesaj_tipi = okunan["mesaj_tipi"]
                except:
                    mesaj_tipi = ""
                try:
                    mesaj_metni = okunan["mesaj"]
                except:
                    mesaj_metni = ""
                try:
                    mesaj_tarihi = okunan["tarih"]
                except:
                    mesaj_tarihi = ""
                if gonderen[0] == "<" and gonderen[-1] == ">":
                    gonderen = gonderen[1:-1]
                duzenli_mesajlar[mesaj_tarihi] = [mesaj_tipi, mesaj_metni, mesaj, gonderen, gonderen_onay]
        return duzenli_mesajlar


if __name__ == "__main__":
    uyg = QApplication(sys.argv)
    okuyucu_pencere = Okuyucu()
    uyg.setOrganizationName('milis-bildirim')
    uyg.setQuitOnLastWindowClosed(False)
    sys.exit(uyg.exec_())
