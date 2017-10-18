from PyQt5.QtWidgets import QDialog,QCheckBox,QVBoxLayout



class Ayarlar(QDialog):
    def __init__(self,ebeveyn=None):
        super(Ayarlar,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        self.setWindowTitle("Milis Bildirim Ayarları")
        kutu = QVBoxLayout()
        self.setLayout(kutu)
        self.gonderen_cb = QCheckBox("Anonim mesajları göster")
        self.gonderen_cb.stateChanged.connect(self.gonderen_cb_degisti)
        kutu.addWidget(self.gonderen_cb)
        self.gonderen_onay_cb = QCheckBox("Onay almamış mesajları göster")
        self.gonderen_onay_cb.stateChanged.connect(self.gonderen_onay_degisti)
        kutu.addWidget(self.gonderen_onay_cb)

    def gonderen_cb_degisti(self):
        if self.gonderen_cb.isChecked():
            self.ebeveyn.anonimleri_goster = 1
        else:
            self.ebeveyn.anonimleri_goster = 0
        self.ebeveyn.settings.setValue("anonimleri_goster",self.ebeveyn.anonimleri_goster)
        self.ebeveyn.settings.sync()
        self.ebeveyn.tum_mesajlar_fonk()

    def gonderen_onay_degisti(self):
        if self.gonderen_onay_cb.isChecked():
            self.ebeveyn.gecersizleri_goster = 1
        else:
            self.ebeveyn.gecersizleri_goster = 0
        self.ebeveyn.settings.setValue("gecersizleri_goster",self.ebeveyn.gecersizleri_goster)
        self.ebeveyn.settings.sync()
        self.ebeveyn.tum_mesajlar_fonk()

    def showEvent(self, event):
        if self.ebeveyn.anonimleri_goster and self.gonderen_cb.isChecked() == False:
            self.gonderen_cb.setChecked(True)
        elif self.ebeveyn.anonimleri_goster == 0 and self.gonderen_cb.isChecked():
            self.gonderen_cb.setChecked(False)
        if self.ebeveyn.gecersizleri_goster and self.gonderen_onay_cb.isChecked() == False:
            self.gonderen_onay_cb.setChecked(True)
        elif self.ebeveyn.gecersizleri_goster == 0 and self.gonderen_onay_cb.isChecked():
            self.gonderen_onay_cb.setChecked(False)
