import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QMessageBox
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from audio_discount import calculate_price_audio as calculate_price 

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')

def create_card(product):
    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    image_path_from_db = product[6]
    
    if image_path_from_db:
        full_path = os.path.join("resources", image_path_from_db)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
        else:
            logging.warning(f"Файл не найден: {full_path}. Использована заглушка.")
            pixmap = QPixmap("resources/picture.png")
    else:
        logging.warning(f"Путь к изображению равен None для товара: {product[1]}. Использована заглушка.")
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

    quantity = product[7]
    quantity_label = QLabel(f"Количество: {quantity} шт.")
    text_layout.addWidget(quantity_label)

    composition = product[4] if product[4] else "Не указан"
    composition_label = QLabel(f"Состав: {composition}")
    text_layout.addWidget(composition_label)

    card_layout.addLayout(text_layout)

    product_id = product[0]
    base_price = float(product[5])
    
    result = calculate_price(product_id, base_price)
    
    if result is None:
        final_price = base_price
        discount_size = 0
    elif isinstance(result, tuple):
        final_price, discount_size = result
    else:
        final_price = result
        discount_size = base_price - final_price

    if discount_size > 0:
        price_text = f"<s>{base_price} ₽</s> <b>{final_price} ₽</b><br><span style='color:red; font-size:12px;'>Скидка 25%</span>"
    else:
        price_text = f"<b>{final_price} ₽</b>"
        
    price_label = QLabel(price_text)
    price_label.setStyleSheet("font-size: 18px; color: #70B2AF;")
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    
    if quantity <= 3:
        bg_color = "#ff8080"
    else:
        bg_color = "#D2F6E7"
        
    card.setStyleSheet(f"background-color: {bg_color}; border-radius: 10px; margin: 5px;")
    
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name="Гость"):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.setWindowTitle("Мир аудиотехники — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        self.db = Database()

        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png").scaledToWidth(150, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setScaledContents(False)
        header_layout.addWidget(logo)
        
        header_layout.addStretch()
        
        self.name_label = QLabel(f"ФИО: {self.full_name}")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #ff8080; padding: 5px; border-radius: 5px; font-weight: bold;")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addLayout(header_layout)

        button_layout = QHBoxLayout()
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        button_layout.addStretch()
        button_layout.addWidget(self.order_button)
        button_layout.addWidget(self.manager_button)
        button_layout.addWidget(self.admin_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

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

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
            self.order_button.hide()
        elif self.role_id == 2:
            self.admin_button.hide()
            self.manager_button.show()
            self.order_button.hide()
        elif self.role_id == 3:
            self.admin_button.hide()
            self.manager_button.hide()
            self.order_button.show()
        else:
            self.admin_button.hide()
            self.manager_button.hide()
            self.order_button.hide()

    def logout(self):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        self.db.close_all()
        event.accept()

if __name__ == "__main__":
    from login_window import LoginWindow
    app = QApplication(sys.argv)
    db = Database()
    window = LoginWindow(db)
    window.show()
    sys.exit(app.exec())