#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# Copyright (c) 2017 Milis İşletim Sistemi
# Author: sonakinci41
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QListWidget,QListWidgetItem, QApplication, QListView,
                             QDesktopWidget, QSystemTrayIcon, QMenu, QAction,qApp)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QSettings
from PyQt5.QtGui import QIcon
import os, yaml, sys
from ui import listemadddesi, ayarlarui, gonder


class Okuyucu(QDialog):
    def __init__(self,ebeveyn=None):
        super(Okuyucu,self).__init__(ebeveyn)
        kutu = QVBoxLayout()
        self.setLayout(kutu)
        kutu.setContentsMargins(0,0,0,0)

        self.sistem_cekmecesi = QSystemTrayIcon(self)
        self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim.png"))
        self.sistem_cekmecesi.activated.connect(self.sistem_cekmecesi_tiklandi)
        self.sistem_cekmecesi.show()

        self.menu_cekmece = QMenu(self)
        self.mesaj_oku_aksiyon = QAction("Mesaj Oku",self,statusTip="MesajOku",triggered=self.mesaj_oku_fonk)
        self.mesaj_gonder_aksiyon = QAction("Mesaj Gönder",self,statusTip="MesajGonder",triggered=self.mesaj_gonder_fonk)
        self.ayarlar_aksiyon = QAction("Ayarlar",self,statusTip="Ayarlar",triggered=self.ayarlar_fonk)
        self.kapat_aksiyon = QAction("Kapat",self,statusTip="Kapat",triggered=self.kapat_fonk)
        self.menu_cekmece.addAction(self.mesaj_oku_aksiyon)
        self.menu_cekmece.addAction(self.mesaj_gonder_aksiyon)
        self.menu_cekmece.addAction(self.ayarlar_aksiyon)
        self.menu_cekmece.addAction(self.kapat_aksiyon)
        self.sistem_cekmecesi.setContextMenu(self.menu_cekmece)
        self.sistem_cekmecesi.showMessage("Çalştı","Milis Bildirim Başarıyla Çalıştırıldı",QSystemTrayIcon.MessageIcon(1),5000)

        self.mesaj_liste = QListWidget()
        self.mesaj_liste.setSelectionMode(QListView.ExtendedSelection)
        kutu.addWidget(self.mesaj_liste)

        self.setFixedWidth(285)
        s = QDesktopWidget().screenGeometry(0)
        self.setFixedHeight(s.height())
        self.setWindowFlags(Qt.Popup)
        self.move(s.width()-285,0)

        ################################
        self.settings = QSettings()
        self.okunmus_mesajlar = self.settings.value("liste", [], str) or []
        self.tum_mesajlar = os.listdir("./mesajlar")
        self.varolan_mesajlar = []
        ################################
        self.tum_mesajlar_fonk()
        self.dosya_izleyici = QFileSystemWatcher()
        self.dosya_izleyici.addPath("./mesajlar")
        self.dosya_izleyici.directoryChanged.connect(self.tum_mesajlar_fonk)

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
        qApp.quit()

    def sistem_cekmecesi_tiklandi(self,value):
        if value == self.sistem_cekmecesi.DoubleClick:
            self.mesaj_oku_fonk()

    def mesaj_oku_fonk(self):
        self.sistem_cekmecesi.setIcon(QIcon("./icons/milis-bildirim.png"))
        self.show()

    def yaml_oku(self,url):
        with open(url, 'r') as f:
            okunan = yaml.load(f)
        return okunan

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
                if mesaj_[2] in self.okunmus_mesajlar:
                    ozel_widget.okunma_degistir("okundu")
                else:
                    ozel_widget.okunma_degistir("okunmadi")
                ozel_widget_item = QListWidgetItem(self.mesaj_liste)
                ozel_widget_item.setSizeHint(ozel_widget.sizeHint())
                self.mesaj_liste.setItemWidget(ozel_widget_item,ozel_widget)

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
        mesajlar = os.listdir("./mesajlar")
        self.tum_mesajlar = mesajlar
        for mesaj in mesajlar:
            okunan = self.yaml_oku("./mesajlar/"+mesaj)
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
            duzenli_mesajlar[mesaj_tarihi]=[mesaj_tipi,mesaj_metni,mesaj]
        return duzenli_mesajlar

if __name__ == "__main__":
    uyg = QApplication(sys.argv)
    okuyucu_pencere = Okuyucu()
    uyg.setOrganizationName('milis-bildirim')
    uyg.setQuitOnLastWindowClosed(False)
    sys.exit(uyg.exec_())
