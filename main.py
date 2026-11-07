import sys
import os
import logging
from decimal import Decimal, ROUND_HALF_UP
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QMessageBox, QComboBox, QLineEdit, QStackedWidget
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s')
logging.getLogger("psycopg.pool").setLevel(logging.ERROR)

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

def create_card(product, db):
    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    image_path_from_db = product[7]
    
    if image_path_from_db:
        full_path = os.path.join("resources", image_path_from_db)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
        else:
            pixmap = QPixmap("resources/picture.png")
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
    text_layout.addWidget(QLabel(f"Категория: {category}"))
    
    material = product[4] if product[4] else "Не указан"
    text_layout.addWidget(QLabel(f"Состав: {material}"))
    
    total_quantity = product[8]
    text_layout.addWidget(QLabel(f"Количество: {total_quantity} шт."))
    card_layout.addLayout(text_layout)

    product_id = product[0]
    base_price = float(product[6])
    orders_count = product[9]
    
    if orders_count == 0:
        new_price_dec = Decimal(str(base_price)) * Decimal('0.75')
        new_price = float(new_price_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    else:
        new_price = base_price

    discount_percent = calculate_discount(base_price, new_price)

    price_layout = QVBoxLayout()
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    if discount_percent > 0:
        old_price_label = QLabel(f"<s>{base_price} ₽</s>")
        old_price_label.setStyleSheet("color: red; font-size: 14px;")
        price_layout.addWidget(old_price_label)
    
    new_price_label = QLabel(f"{new_price} ₽")
    if discount_percent > 15:
        new_price_label.setStyleSheet("font-size: 18px; color: #2E8B57; font-weight: bold;")
    else:
        new_price_label.setStyleSheet("font-size: 18px; color: black; font-weight: bold;")
    price_layout.addWidget(new_price_label)

    if discount_percent > 0:
        discount_label = QLabel(f"-{int(discount_percent)}%")
        discount_label.setStyleSheet("color: #2E8B57; font-weight: bold; font-size: 14px;")
        price_layout.addWidget(discount_label)

    order_btn = QPushButton("Оформить")
    if total_quantity == 0:
        order_btn.setEnabled(False)
        order_btn.setText("Нет в наличии")
        order_btn.setStyleSheet("background-color: #cccccc; color: gray; padding: 5px; border-radius: 5px;")
    else:
        order_btn.setStyleSheet("background-color: #70B2AF; color: white; padding: 5px; border-radius: 5px; font-weight: bold;")
    
    price_layout.addWidget(order_btn)
    card_layout.addLayout(price_layout)
    card.setLayout(card_layout)

    if total_quantity == 0:
        bg_color = "#ADD8E6"
    elif total_quantity <= 3:
        bg_color = "#FF8080"
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
        }}
    """)
    return card

class MainWindow(QMainWindow):
    def __init__(self, db, role_id=None, full_name="Гость"):
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.full_name = full_name
        self.setWindowTitle("Мир аудиотехники — Каталог")
        self.resize(850, 650)
        self.setWindowIcon(QIcon("resources/icon.ico"))

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
        
        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet("background-color: #70B2AF; color: white; padding: 5px; border-radius: 5px;")
        self.back_button.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_button)

        role_name = "Гость"
        if self.role_id == 1: role_name = "Администратор"
        elif self.role_id == 2: role_name = "Менеджер"
        elif self.role_id == 3: role_name = "Клиент"
            
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

        self.order_button.clicked.connect(self.confirm_order)

        button_style = "background-color: #70B2AF; color: white; font-family: Calibri; padding: 8px; border-radius: 5px; font-weight: bold;"
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)

        self.manager_button.clicked.connect(lambda: self.switch_page(2))
        self.admin_button.clicked.connect(lambda: self.switch_page(2))

        button_layout.addStretch()
        button_layout.addWidget(self.order_button)
        button_layout.addWidget(self.manager_button)
        button_layout.addWidget(self.admin_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.stacked_widget = QStackedWidget()

        self.catalog_page = QWidget()
        catalog_layout = QVBoxLayout(self.catalog_page)
        
        search_layout = QHBoxLayout()
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
        catalog_layout.addLayout(search_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        catalog_layout.addWidget(self.scroll_area)

        self.product_page = QWidget()
        product_layout = QVBoxLayout(self.product_page)
        product_layout.addWidget(QLabel("Здесь будет карточка товара", alignment=Qt.AlignCenter))

        self.orders_page = QWidget()
        orders_layout = QVBoxLayout(self.orders_page)
        orders_layout.addWidget(QLabel("Здесь будет список заказов", alignment=Qt.AlignCenter))

        self.stacked_widget.addWidget(self.catalog_page)
        self.stacked_widget.addWidget(self.product_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.setCurrentIndex(0)

        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; font-family: Calibri; }
            QLabel { color: #000000; }
        """)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.setWindowTitle("Мир аудиотехники — Каталог")
        elif index == 1:
            self.setWindowTitle("Мир аудиотехники — Карточка товара")
        elif index == 2:
            self.setWindowTitle("Мир аудиотехники — Заказы")

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)

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
            card = create_card(product, self.db)
            self.scroll_layout.addWidget(card)

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

    def confirm_order(self):
        QMessageBox.information(self, "Информация", "Заказ успешно оформлен")

    def delete_order(self):
        reply = QMessageBox.warning(self, "Предупреждение", "Вы уверены, что хотите удалить заказ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Информация", "Заказ удален")

    def logout(self):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    from login_window import LoginWindow
    app = QApplication(sys.argv)
    db = Database()
    app.aboutToQuit.connect(db.close_all)
    window = LoginWindow(db)
    window.show()
    sys.exit(app.exec())