import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

def create_card(product):
    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    if product[7]:
        pixmap = QPixmap(f"resources/{product[7]}")
    else:
        pixmap = QPixmap("resources/picture.png")
        
    if pixmap.isNull():
        pixmap = QPixmap("resources/picture.png")
        
    image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    text_layout = QVBoxLayout()
    
    manufacturer = product[3] if product[3] else "Неизвестно"
    name = product[1]
    name_label = QLabel(f"{manufacturer} | {name}")
    name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
    text_layout.addWidget(name_label)

    category = product[2] if product[2] else "Без категории"
    category_label = QLabel(f"Категория: {category}")
    text_layout.addWidget(category_label)

    quantity = product[8]
    quantity_label = QLabel(f"Количество: {quantity} шт.")
    text_layout.addWidget(quantity_label)

    composition = product[5] if product[5] else "Не указан"
    composition_label = QLabel(f"Состав: {composition}")
    text_layout.addWidget(composition_label)

    card_layout.addLayout(text_layout)

    price = product[6]
    price_label = QLabel(f"{price} ₽")
    price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #70B2AF;")
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    card.setStyleSheet("background-color: #D2F6E7; border-radius: 10px; margin: 5px;")
    
    return card


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мир аудиотехники — Каталог")
        self.resize(800, 600)
        
        self.setWindowIcon(QIcon("resources/icon.ico"))

        self.db = Database()

        central_widget = QWidget()
        main_layout = QVBoxLayout()

        header_layout = QVBoxLayout()
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png").scaledToWidth(300, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setScaledContents(False)
        logo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo)

        title = QLabel("Мир аудиотехники — Каталог")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        main_layout.addLayout(header_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        products = self.db.get_products()
        for product in products:
            card = create_card(product)
            scroll_layout.addWidget(card)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        central_widget.setLayout(main_layout)
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

    def closeEvent(self, event):
        self.db.close_all()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())