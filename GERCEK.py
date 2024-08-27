import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
    QFrame,
    QProgressBar,
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QProcess
import paramiko

from drone_data import DroneData


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AEROKOU_YKI 0.74.1")
        self.resize(1200, 800)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #212121;
                color: #ffffff;
            }
            QTabWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #383838;
                color: #ffffff;
                padding: 10px 20px;
                border: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4f4f4f;
            }
            QWidget {
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QPushButton, QLabel {
                background-color: #383838;
                color: #ffffff;
                border: 1px solid #505050;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #434343;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QFrame {
                background-color: #1c1c1c;
                border: 3px solid #505050; /* Çerçeveleri daha kalın ve belirgin hale getir */
            }
            QPushButton#acil_durdur_butonu {
                background-color: #c62828; /* Kırmızı acil durum butonu */
                color: white;
                font-size: 18pt;  /* Buton yazı boyutunu büyüt */
                padding: 15px 20px; /* Buton boyutunu büyüt */
            }
            QPushButton#acil_durdur_butonu:hover {
                background-color: #b71c1c;
            }
            QPushButton#gorev_baslat_butonu {
                background-color: #4CAF50; /* Yeşil görev başlat butonu */
                color: white;
            }
            QPushButton#gorev_baslat_butonu:hover {
                background-color: #45a049;
            }
            QTextEdit#notlar_alani {
                font-family: monospace;
            }
            QPushButton#dosya_sec_butonu { /* Dosya Seç butonu için stil */
                font-size: 14pt;
                padding: 10px 15px;
            }
            QPushButton#gorev_baslat_butonu { /* Görev Başlat butonu için stil */
                font-size: 14pt;
                padding: 10px 15px;
            }
            QLabel#veri_etiketi { /* Veri etiketi için stil */
                font-size: 12pt;  /* Yazı boyutunu ayarlayın */
                color: #FFCC00; /* Örnek: Altın sarısı */
            }
        """
        )

        # Ana Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Sekme Widget'ı ---
        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # --- Anasayfa Sekmesi ---
        self.anasayfa_widget = QWidget()
        self.tab_widget.addTab(self.anasayfa_widget, "Anasayfa")
        anasayfa_layout = QVBoxLayout(self.anasayfa_widget)

        # --- Logo Kısmı ---
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        anasayfa_layout.addLayout(logo_layout)

        self.takim_logo = QLabel(self)
        self.set_logo(self.takim_logo, "aerokou.png")  # Replace with your actual logo file
        logo_layout.addWidget(self.takim_logo)

        self.universite_logo = QLabel(self)
        self.set_logo(self.universite_logo, "kou.png")  # Replace with your actual logo file
        logo_layout.addWidget(self.universite_logo)

        # --- İçerik Kısmı ---
        content_layout = QHBoxLayout()
        anasayfa_layout.addLayout(content_layout)

        # --- Sol Kısım ---
        sol_kisim = QVBoxLayout()
        content_layout.addLayout(sol_kisim, stretch=2)

        # --- Drone Data Thread ---
        self.drone_data_thread = DroneData()
        self.drone_data_thread.data_updated.connect(self.update_drone_data)
        self.drone_data_thread.start()

        # --- İHA Bağlantı Durumları ---
        self.feniks_label = self.create_drone_status_widget("Feniks", False)
        self.alaca_label = self.create_drone_status_widget("Alaca", False)
        self.korfez_label = self.create_drone_status_widget("Korfez", False)

        drone_status_layout = QHBoxLayout()
        drone_status_layout.setAlignment(Qt.AlignCenter)
        drone_status_layout.addWidget(self.feniks_label)
        drone_status_layout.addWidget(self.alaca_label)
        drone_status_layout.addWidget(self.korfez_label)
        sol_kisim.addLayout(drone_status_layout)

        # --- SSH Bağlantı Bilgileri (Anasayfa Sekmesi) ---
        ssh_layout = QHBoxLayout()
        sol_kisim.addLayout(ssh_layout)

        ssh_layout.addWidget(QLabel("IP:"))
        self.ip_edit = QLineEdit()
        ssh_layout.addWidget(self.ip_edit)

        ssh_layout.addWidget(QLabel("Kullanıcı Adı:"))
        self.username_edit = QLineEdit()
        ssh_layout.addWidget(self.username_edit)

        ssh_layout.addWidget(QLabel("Parola:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        ssh_layout.addWidget(self.password_edit)

        ssh_layout.addWidget(QLabel("Port:"))
        self.port_edit = QLineEdit("22")
        ssh_layout.addWidget(self.port_edit)

        self.baglan_butonu = QPushButton("Bağlan")
        self.baglan_butonu.clicked.connect(self.ssh_baglan)
        ssh_layout.addWidget(self.baglan_butonu)

        # --- Paramiko Terminali (Anasayfa Sekmesi) ---
        terminal_frame = QFrame()
        terminal_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        terminal_frame.setStyleSheet("background-color: #2a2a2a;")
        terminal_layout = QVBoxLayout(terminal_frame)
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        terminal_layout.addWidget(self.terminal)
        sol_kisim.addWidget(terminal_frame)

        # Terminali küçültmek için maksimum yükseklik sınırlayalım
        terminal_frame.setMaximumHeight(150)

        # --- Komut Girişi ve Gönderme (Anasayfa Sekmesi) ---
        komut_layout = QHBoxLayout()
        sol_kisim.addLayout(komut_layout)

        self.komut_girisi = QLineEdit()
        komut_layout.addWidget(self.komut_girisi)
        self.komut_girisi.returnPressed.connect(self.ssh_komut_gonder)

        self.komut_gonder_butonu = QPushButton("Gönder")
        komut_layout.addWidget(self.komut_gonder_butonu)
        self.komut_gonder_butonu.clicked.connect(self.ssh_komut_gonder)
        self.komut_gonder_butonu.setEnabled(False)

        # --- Görev Başlat (Anasayfa Sekmesi) ---
        gorev_baslat_layout = QHBoxLayout()
        sol_kisim.addLayout(gorev_baslat_layout)

        self.dosya_yolu = ""
        self.dosya_sec_butonu = QPushButton("Görev Dosyası Seç")
        self.dosya_sec_butonu.setObjectName("dosya_sec_butonu")
        self.dosya_sec_butonu.clicked.connect(self.dosya_sec)
        gorev_baslat_layout.addWidget(self.dosya_sec_butonu)

        self.gorev_baslat_butonu = QPushButton("Görev Başlat")
        self.gorev_baslat_butonu.setObjectName("gorev_baslat_butonu")
        self.gorev_baslat_butonu.clicked.connect(self.gorev_baslat)
        gorev_baslat_layout.addWidget(self.gorev_baslat_butonu)

        # --- Görev Terminali (Anasayfa Sekmesi) ---
        gorev_terminal_frame = QFrame()
        gorev_terminal_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        gorev_terminal_frame.setStyleSheet("background-color: #2a2a2a;")
        gorev_terminal_layout = QVBoxLayout(gorev_terminal_frame)
        self.gorev_terminali = QTextEdit()
        self.gorev_terminali.setReadOnly(True)
        gorev_terminal_layout.addWidget(self.gorev_terminali)
        sol_kisim.addWidget(gorev_terminal_frame)

        # Görev terminalini küçültmek için maksimum yükseklik sınırlayalım
        gorev_terminal_frame.setMaximumHeight(150)

        # --- Sağ Kısım (Anasayfa Sekmesi) ---
        sag_kisim = QVBoxLayout()
        content_layout.addLayout(sag_kisim, stretch=1)  # Sağ kısım daha dar

        # --- Notlar Alanı (Anasayfa Sekmesi) ---
        notlar_widget = QWidget()
        notlar_widget.setStyleSheet("background-color: #383838; padding: 10px;")
        notlar_layout = QVBoxLayout(notlar_widget)
        sag_kisim.addWidget(notlar_widget)

        # Notlar başlığı
        notlar_baslik = QLabel("<h2>NOTLAR</h2>")
        notlar_layout.addWidget(notlar_baslik)

        # Kaydırmalı Notlar Alanı
        self.notlar_alani = QTextEdit()
        self.notlar_alani.setObjectName("notlar_alani")
        self.notlar_alani.setReadOnly(False)
        notlar_layout.addWidget(self.notlar_alani)

        # Notları txt dosyasından yükle
        self.notlar_dosyasi = "notlar.txt"
        self.notlari_yukle()

        # --- Notları Kaydet Butonu (Anasayfa Sekmesi) ---
        self.notlari_kaydet_butonu = QPushButton("Notları Kaydet")
        self.notlari_kaydet_butonu.clicked.connect(self.notlari_kaydet)
        notlar_layout.addWidget(self.notlari_kaydet_butonu)

        # --- Acil Durum Butonu (Anasayfa Sekmesi) ---
        self.acil_durdur_butonu = QPushButton("ACİL GÖREV İPTAL (RTL)")
        self.acil_durdur_butonu.setObjectName("acil_durdur_butonu")
        self.acil_durdur_butonu.clicked.connect(self.acil_gorev_iptal)
        sag_kisim.addWidget(self.acil_durdur_butonu)

        # --- Diğer Sekmeler ---
        self.feniks_sekmesi = self.create_drone_tab("Feniks")
        self.alaca_sekmesi = self.create_drone_tab("Alaca")
        self.korfez_sekmesi = self.create_drone_tab("Korfez")

        self.tab_widget.addTab(self.feniks_sekmesi, "Feniks")
        self.tab_widget.addTab(self.alaca_sekmesi, "Alaca")
        self.tab_widget.addTab(self.korfez_sekmesi, "Korfez")


        # Sekmeleri ekle
        self.tab_widget.addTab(self.feniks_sekmesi, "Feniks")
        self.tab_widget.addTab(self.alaca_sekmesi, "Alaca")
        self.tab_widget.addTab(self.korfez_sekmesi, "Korfez")

        # SSH Client
        self.ssh_client = None

    def create_drone_status_widget(self, drone_name, is_active, battery_level=0):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_path = "droneaktif.png" if is_active else "dronepasif.png"
        self.set_logo(icon_label, icon_path)
        layout.addWidget(icon_label)

        name_label = QLabel(drone_name)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        progress_bar = QProgressBar()
        progress_bar.setValue(battery_level)
        layout.addWidget(progress_bar)

        return widget

    def create_drone_tab(self, drone_name):
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # İHA Verileri Başlığı - Daha büyük ve ortalanmış
        baslik = QLabel(f"<h1>{drone_name} İHA Verileri</h1>")
        baslik.setAlignment(Qt.AlignCenter)
        layout.addWidget(baslik)

        # Veri Gösterim Alanı - Sayfanın yarısını kaplayacak şekilde
        veri_frame = QFrame()
        veri_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        veri_frame.setStyleSheet("background-color: #2a2a2a;")
        veri_layout = QVBoxLayout(veri_frame)

        # Her sekme için ayrı veri etiketi
        if drone_name == "Feniks":
            self.feniks_veri_etiketi = QLabel("Burada Feniks verileri gözükecek")
            self.feniks_veri_etiketi.setObjectName("veri_etiketi")
            self.feniks_veri_etiketi.setAlignment(Qt.AlignTop)  # Verileri üste hizala
            veri_layout.addWidget(self.feniks_veri_etiketi)
        elif drone_name == "Alaca":
            self.alaca_veri_etiketi = QLabel("Burada Alaca verileri gözükecek")
            self.alaca_veri_etiketi.setObjectName("veri_etiketi")
            self.alaca_veri_etiketi.setAlignment(Qt.AlignTop)  # Verileri üste hizala
            veri_layout.addWidget(self.alaca_veri_etiketi)
        elif drone_name == "Korfez":
            self.korfez_veri_etiketi = QLabel("Burada Korfez verileri gözükecek")
            self.korfez_veri_etiketi.setObjectName("veri_etiketi")
            self.korfez_veri_etiketi.setAlignment(Qt.AlignTop)  # Verileri üste hizala
            veri_layout.addWidget(self.korfez_veri_etiketi)

        layout.addWidget(veri_frame)

        # Veri çerçevesini sayfanın yarısını kaplayacak şekilde ayarlayın
        veri_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return tab_widget

    def update_drone_data(self, *data):
        feniks_name, feniks_active, feniks_battery, alaca_name, alaca_active, alaca_battery, korfez_name, korfez_active, korfez_battery = data

        self.update_drone_status(self.feniks_label, feniks_active, feniks_battery)
        self.update_drone_status(self.alaca_label, alaca_active, alaca_battery)
        self.update_drone_status(self.korfez_label, korfez_active, korfez_battery)

        # Update data labels in respective tabs
        self.feniks_veri_etiketi.setText(feniks_battery)
        # Similarly update alaca_veri_etiketi and korfez_veri_etiketi

    def update_drone_status(self, label_widget, is_active, battery_level=0):
        layout = label_widget.layout()
        icon_label = layout.itemAt(0).widget()
        icon_path = "droneaktif.png" if is_active else "dronepasif.png"
        self.set_logo(icon_label, icon_path)

        progress_bar = layout.itemAt(2).widget()
        try:
            battery_percentage = int(battery_level.split(":")[1].strip("% "))
            progress_bar.setValue(battery_percentage)
        except:
            progress_bar.setValue(0)





    def dosya_sec(self):
        secenekler = QFileDialog.Options()
        dosya_yolu, _ = QFileDialog.getOpenFileName(
            self,
            "Python Dosyası Seç",
            "",
            "Python Dosyaları (*.py)",
            options=secenekler,
        )
        if dosya_yolu:
            self.dosya_yolu = dosya_yolu

    # ... diğer fonksiyonlar ...

    def gorev_baslat(self):
        if self.dosya_yolu:
            try:
                komut = f"python3 {self.dosya_yolu}"
                process = QProcess(self)
                process.readyReadStandardOutput.connect(self.gorev_cikisini_isle)
                process.readyReadStandardError.connect(self.gorev_hatasini_isle)
                process.start(komut)
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Görev başlatılamadı: {str(e)}")
        else:
            QMessageBox.warning(self, "Dosya Seçilmedi", "Lütfen bir Python dosyası seçin.")

    def gorev_cikisini_isle(self):
        cikti = bytes(self.sender().readAllStandardOutput()).decode("utf-8")
        self.gorev_terminali.append(cikti)

    def gorev_hatasini_isle(self):
        hata = bytes(self.sender().readAllStandardError()).decode("utf-8")
        self.gorev_terminali.append(f"<font color='red'>{hata}</font>")

    def ssh_baglan(self):
        ip = self.ip_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        port = int(self.port_edit.text())

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip, port, username, password)
            self.terminal.append(f"{ip} adresine başarıyla bağlanıldı.")
            self.komut_gonder_butonu.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Bağlantı Hatası", f"SSH bağlantısı kurulamadı: {str(e)}")

    def ssh_komut_gonder(self):
        if self.ssh_client and self.ssh_client.get_transport().is_active():
            komut = self.komut_girisi.text()
            self.komut_girisi.clear()
            stdin, stdout, stderr = self.ssh_client.exec_command(komut)
            cikti = stdout.read().decode()
            hata = stderr.read().decode()
            self.terminal.append(f"> {komut}")
            self.terminal.append(cikti)
            if hata:
                self.terminal.append(f"Hata: {hata}")
        else:
            QMessageBox.warning(self, "Bağlantı Yok", "Önce SSH bağlantısı kurmanız gerekiyor.")

    def set_logo(self, label, image_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, image_file)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            label.setPixmap(pixmap)
        else:
            print(f"Hata: Resim yüklenemiyor: {image_path}")

    def acil_gorev_iptal(self):
        # Burada RTL komutu göndere
        onay = QMessageBox.question(
            self,
            "Acil Görev İptal",
            "Emin misiniz? Bu işlem İHA'yı hemen eve döndürecektir.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if onay == QMessageBox.Yes:
            if self.ssh_client and self.ssh_client.get_transport().is_active():
                try:
                    # RTL komutunu buraya ekleyin
                    # Örnek RTL komutu (Drone'unuza göre ayarlamanız gerekebilir):
                    stdin, stdout, stderr = self.ssh_client.exec_command("rtl")
                    cikti = stdout.read().decode()
                    hata = stderr.read().decode()
                    self.terminal.append(f"> rtl")
                    self.terminal.append(cikti)
                    if hata:
                        self.terminal.append(f"Hata: {hata}")
                except Exception as e:
                    QMessageBox.warning(
                        self, "Hata", f"RTL komutu gönderilemedi: {str(e)}"
                    )
            else:
                QMessageBox.warning(
                    self, "Bağlantı Yok", "Önce SSH bağlantısı kurmanız gerekiyor."
                )

    def notlari_kaydet(self):
        try:
            with open(self.notlar_dosyasi, "w") as f:
                f.write(self.notlar_alani.toPlainText())
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Notlar kaydedilemedi: {str(e)}")

    def notlari_yukle(self):
        try:
            with open(self.notlar_dosyasi, "r") as f:
                self.notlar_alani.setPlainText(f.read())
        except FileNotFoundError:
            pass  # Dosya yoksa bir şey yapmayın
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Notlar yüklenemedi: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
