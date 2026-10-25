import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мир аудиотехники — Каталог")
        self.resize(800, 600)
        
        self.setWindowIcon(QIcon("resources/icon.ico"))

        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.addStretch()

        logo = QLabel()
        pixmap = QPixmap("resources/logo.png").scaledToWidth(400, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setScaledContents(False)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Мир аудиотехники — Каталог")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-top: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #000000;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())