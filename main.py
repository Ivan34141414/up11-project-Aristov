import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QMessageBox, QComboBox, QLineEdit
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from audio_discount import calculate_price_audio as calculate_price 

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(message)s')

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

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

    total_quantity = product[7]
    quantity_label = QLabel(f"Количество: {total_quantity} шт.")
    text_layout.addWidget(quantity_label)

    composition = product[4] if product[4] else "Не указан"
    composition_label = QLabel(f"Состав: {composition}")
    text_layout.addWidget(composition_label)


    # Если товара нет на складе - голубая подсветка и текст «Нет в наличии»
    if total_quantity == 0:
        out_of_stock_label = QLabel("Нет в наличии")
        out_of_stock_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        text_layout.addWidget(out_of_stock_label)

    card_layout.addLayout(text_layout)

    product_id = product[0]
    base_price = float(product[5])
    
    new_price = calculate_price(product_id, base_price)
    if isinstance(new_price, tuple):
        new_price = new_price[0]
    elif new_price is None:
        new_price = base_price

    discount_percent = calculate_discount(base_price, new_price)

    price_layout = QVBoxLayout()
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    old_price_label = QLabel(f"<s>{base_price} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px;")
    
    new_price_label = QLabel(f"{new_price} ₽")
    new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px;")
    
    discount_label = QLabel(f"-{int(discount_percent)}%")
    if discount_percent > 30:
        discount_label.setStyleSheet("color: #FF8C00; font-weight: bold; font-size: 14px;")
    else:
        discount_label.setStyleSheet("color: #2E8B57; font-weight: bold; font-size: 14px;")

    if discount_percent > 0:
        price_layout.addWidget(old_price_label)
        price_layout.addWidget(new_price_label)
        price_layout.addWidget(discount_label)
    else:
        old_price_label.hide()
        discount_label.hide()
        price_layout.addWidget(new_price_label)

    if total_quantity == 0:
        order_btn = QPushButton("Оформить")
        order_btn.setEnabled(False)
        order_btn.setStyleSheet("background-color: #cccccc; color: gray; padding: 5px; border-radius: 5px;")
        price_layout.addWidget(order_btn)

    card_layout.addLayout(price_layout)
    card.setLayout(card_layout)

    if total_quantity == 0:
        bg_color = "#ADD8E6"
    elif total_quantity <= 3:
        bg_color = "#ff8080"
    else:
        bg_color = "#D2F6E7"
        
    card.setObjectName("ProductCard")
    card.setStyleSheet(f"""
        QWidget#ProductCard {{
            background-color: {bg_color};
            border-radius: 10px;
            margin: 5px;
            border: 2px solid transparent;
        }}
        QWidget#ProductCard:hover {{
            border: 2px solid #70B2AF;
            background-color: #E6FFF5;
        }}
    """)
    
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name="Гость"):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.setWindowTitle("Мир аудиотехники — Каталог")
        self.resize(850, 650)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        self.db = Database()

        self.setup_ui()
        self.setup_role_interface()
        self.load_products()

    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #D2F6E7; border-radius: 10px;")
        header_layout = QHBoxLayout(header_widget)
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png").scaledToWidth(150, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setScaledContents(False)
        logo.setStyleSheet("background-color: transparent;")
        header_layout.addWidget(logo)
        
        header_layout.addStretch()
        
        role_name = "Гость"
        # Администратор (role_id = 1) видит все кнопки
        if self.role_id == 1:
            role_name = "Администратор"
        elif self.role_id == 2:
            role_name = "Менеджер"
        elif self.role_id == 3:
            role_name = "Клиент"
            
        self.name_label = QLabel(f"ФИО: {self.full_name} ({role_name})")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; background-color: transparent;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #ff8080; padding: 5px; border-radius: 5px; font-weight: bold;")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        main_layout.addWidget(header_widget)

        button_layout = QHBoxLayout()
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")

        button_style = "background-color: #70B2AF; color: white; font-family: Calibri; padding: 8px; border-radius: 5px; font-weight: bold;"
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)

        button_layout.addStretch()
        button_layout.addWidget(self.order_button)
        button_layout.addWidget(self.manager_button)
        button_layout.addWidget(self.admin_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или описанию...")
        self.search_input.textChanged.connect(self.load_products)
        search_layout.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        self.filter_combo.addItems(self.db.get_categories())
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        search_layout.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        search_layout.addWidget(self.sort_combo)

        main_layout.addWidget(self.search_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

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

    def load_products(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search = self.search_input.text()
        category = self.filter_combo.currentText()
        sort_order = self.sort_combo.currentText()

        products = self.db.get_products(search, category, sort_order)

        if not products:
            no_results = QLabel("Товары не найдены")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("font-size: 18px; color: gray; margin-top: 20px;")
            self.scroll_layout.addWidget(no_results)
            return

        for product in products:
            card = create_card(product)
            self.scroll_layout.addWidget(card)

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
            self.order_button.hide()
            self.search_widget.show()
        elif self.role_id == 2:
            self.admin_button.hide()
            self.manager_button.show()
            self.order_button.hide()
            self.search_widget.show()
        elif self.role_id == 3:
            self.admin_button.hide()
            self.manager_button.hide()
            self.order_button.show()
            self.search_widget.show()
        else:
            self.admin_button.hide()
            self.manager_button.hide()
            self.order_button.hide()
            self.search_widget.hide()

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