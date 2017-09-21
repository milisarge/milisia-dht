from PyQt5.QtWidgets import QVBoxLayout ,QHBoxLayout, QWidget, QTextEdit, QLabel, QSpacerItem, QSizePolicy, QCheckBox


class OzelListeMaddesi(QWidget):
    def __init__(self,ebeveyn=None):
        super(OzelListeMaddesi,self).__init__(ebeveyn)
        self.ebeveyn = ebeveyn
        kutu = QVBoxLayout()
        self.setLayout(kutu)

        self.mesaj_tipi = QLabel()
        kutu.addWidget(self.mesaj_tipi)

        self.mesaj = QTextEdit()
        self.mesaj.setReadOnly(True)
        kutu.addWidget(self.mesaj)

        self.alt_kutu = QHBoxLayout()
        kutu.addLayout(self.alt_kutu)
        self.tarih = QLabel()
        self.alt_kutu.addWidget(self.tarih)
        self.alt_kutu.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.mesaj.setFixedHeight(125)

    def okuyucu(self):
        self.mesaj.setFixedSize(250,125)
        self.okunma = QCheckBox()
        self.okunma.clicked.connect(self.okunma_degistir)
        self.alt_kutu.addWidget(self.okunma)

    def mesaj_id_ekle(self,mesaj_id):
        self.mesaj_id = mesaj_id

    def mesaj_tipi_ekle(self,mesaj_tipi):
        self.mesaj_tipi.setText("<b>Mesaj Tipi : </b>"+mesaj_tipi)

    def mesaj_ekle(self,mesaj):
        self.mesaj.setText(str(mesaj))

    def tarih_ekle(self,tarih):
        self.tarih.setText("<b>"+tarih+"</b>")

    def okunma_degistir(self,okunma):
        if okunma == "okunmadi":
            self.okunma.setText("okunmadı")
        elif okunma == "okundu" or self.okunma.isChecked() == True:
            self.okunma.setText("okundu")
            self.okunma.setChecked(True)
            self.okunma.setDisabled(True)
            self.ebeveyn.okunmus_mesajlar.append(self.mesaj_id)
