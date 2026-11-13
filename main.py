import sys
import os
import logging
import uuid
import shutil
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, 
                               QWidget, QScrollArea, QPushButton, QMessageBox, QComboBox, 
                               QLineEdit, QDialog, QFormLayout, QSpinBox, QFileDialog,
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QStackedWidget)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QStandardPaths
from database import Database
import psycopg

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s')
logging.getLogger("psycopg.pool").setLevel(logging.ERROR)

def resource_path(relative):
    path = os.path.abspath(relative)
    return path

def load_product_pixmap(image_path, fallback="resources/picture.png"):
    pixmap = QPixmap(resource_path(image_path)) if image_path else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(resource_path(fallback))
    if pixmap.isNull():
        pixmap = QPixmap(160, 120)
        pixmap.fill(Qt.GlobalColor.lightGray)
    return pixmap

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100

def create_card(product, db, main_window):
    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    image_path_from_db = product[7]
    
    if image_path_from_db:
        full_path = os.path.join("resources", image_path_from_db)
        pixmap = load_product_pixmap(full_path)
    else:
        pixmap = load_product_pixmap(None)
        
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

    order_btn = QPushButton("Подробнее")
    if total_quantity == 0:
        order_btn.setEnabled(False)
        order_btn.setText("Нет в наличии")
        order_btn.setStyleSheet("background-color: #cccccc; color: gray; padding: 5px; border-radius: 5px;")
    else:
        order_btn.setStyleSheet("background-color: #70B2AF; color: white; padding: 5px; border-radius: 5px; font-weight: bold;")
        order_btn.clicked.connect(lambda checked=False, pid=product_id: main_window.open_product_card(pid))
    
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

class ProductCard(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db = parent.db if parent is not None else None
        self.product = {}
        self.setWindowTitle("Карточка товара")
        self.resize(400, 600)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        self.name_label = QLabel("Загрузка...")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        
        self.price_label = QLabel("")
        self.price_label.setStyleSheet("font-size: 16px; color: #2E8B57;")
        
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        
        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self.on_variant_changed)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        
        self.add_button = QPushButton("В корзину")
        self.add_button.clicked.connect(self.add_selected_to_cart)

        self.load_img_btn = QPushButton("Загрузить изображение")
        self.load_img_btn.clicked.connect(self.load_image)
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.load_img_btn)
        layout.addWidget(self.name_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.description_label)
        layout.addWidget(QLabel("Выберите вариант:"))
        layout.addWidget(self.size_combo)
        layout.addWidget(QLabel("Количество:"))
        layout.addWidget(self.quantity_spin)
        layout.addWidget(self.add_button)

    def load_product(self, product_id):
        if not self.db:
            return
        conn = self.db.get_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        query = """
            SELECT p.name, p.price, p.description, p.image_path,
            COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE p.product_id = %s
            GROUP BY p.product_id
        """
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        
        if product is None:
            self.add_button.setEnabled(False)
            QMessageBox.warning(self, "Товар", "Товар не найден")
            cursor.close()
            self.db.release_connection(conn)
            return
            
        name, price, description, image_path, total_quantity = product
        
        self.product = {"name": name, "price": price}
        self.name_label.setText(name)
        self.price_label.setText(f"{price} ₽")
        self.description_label.setText(description or "")
        
        if image_path:
            full_path = os.path.join("resources", image_path)
            self.image_label.setPixmap(load_product_pixmap(full_path).scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.image_label.setPixmap(load_product_pixmap(None).scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        cursor.execute(
            """
            SELECT v.variant_id, v.value, si.quantity 
            FROM stock_items si 
            JOIN variants v ON si.variant_id = v.variant_id 
            WHERE si.product_id = %s 
            ORDER BY v.variant_id
            """, (product_id,)
        )
        
        self.size_combo.clear()
        variants = cursor.fetchall()
        for variant_id, value, quantity in variants:
            self.size_combo.addItem(f"{value} (В наличии: {quantity})", (variant_id, quantity))
            
        cursor.close()
        self.db.release_connection(conn)
        
        self.on_variant_changed()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return
            
        if QPixmap(file_path).isNull():
            QMessageBox.warning(self, "Изображение", "Файл не является изображением")
            return
            
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        target = Path(base) / "images" / (uuid.uuid4().hex + Path(file_path).suffix)
        
        conn = self.db.get_connection()
        if not conn:
            return
            
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target)
            
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET image_path = %s WHERE product_id = %s",
                (str(target), self.product_id)
            )
            if cursor.rowcount != 1:
                raise ValueError("Товар не найден")
            conn.commit()
            cursor.close()
        except (OSError, psycopg.Error, ValueError) as error:
            conn.rollback()
            if target.exists():
                target.unlink()
            QMessageBox.critical(self, "Изображение не сохранено", str(error))
            self.db.release_connection(conn)
            return
        finally:
            self.db.release_connection(conn)
            
        self.image_label.setPixmap(QPixmap(str(target)).scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_variant_changed(self, index=0):
        selected = self.size_combo.currentData()
        available = max(0, int(selected[1])) if selected else 0
        
        if available > 0:
            self.quantity_spin.setRange(1, available)
        else:
            self.quantity_spin.setRange(0, 0)
            
        self.add_button.setEnabled(available > 0)

    def add_selected_to_cart(self):
        selected = self.size_combo.currentData()
        if not selected or self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Остаток", "Нет доступного остатка")
            return
            
        variant_id = selected[0]
        quantity = self.quantity_spin.value()
        name = self.product.get("name", "Неизвестно")
        price = self.product.get("price", 0)
        product_id = self.product_id

        main_window = self.parent()
        if main_window and hasattr(main_window, "add_to_cart"):
            main_window.add_to_cart(product_id, variant_id, name, quantity, price)
            self.accept()

class ValidationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест валидации ввода")
        self.resize(350, 300)
        
        layout = QFormLayout()
        
        self.quantity_input = QLineEdit()
        self.price_input = QLineEdit()
        self.name_input = QLineEdit()
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("ДД.ММ.ГГГГ")
        
        layout.addRow("Количество:", self.quantity_input)
        layout.addRow("Цена:", self.price_input)
        layout.addRow("Наименование:", self.name_input)
        layout.addRow("Дата:", self.date_input)
        
        btn = QPushButton("Проверить")
        btn.clicked.connect(self.check_inputs)
        layout.addRow(btn)
        
        self.setLayout(layout)

    def check_inputs(self):
        qty_text = self.quantity_input.text()
        try:
            quantity = int(qty_text)
            if quantity <= 0:
                QMessageBox.critical(self, "Ошибка", "Количество должно быть положительным")
                return
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите число в поле 'Количество'")
            return

        price_text = self.price_input.text()
        try:
            price = float(price_text)
            if price <= 0:
                QMessageBox.critical(self, "Ошибка", "Цена должна быть положительной")
                return
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите число в поле 'Цена'")
            return

        name = self.name_input.text()
        if not name:
            QMessageBox.critical(self, "Ошибка", "Введите наименование")
            return

        date_str = self.date_input.text()
        try:
            date = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите дату в формате ДД.ММ.ГГГГ")
            return
            
        QMessageBox.information(self, "Успех", "Все данные корректны!")

class MainWindow(QMainWindow):
    def __init__(self, db, role_id=None, full_name="Гость", user_id=None):
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.full_name = full_name
        self.user_id = user_id
        
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
        self.back_button.setStyleSheet("background-color: #70B2AF; color: white; padding: 5px; border-radius: 5px; font-weight: bold;")
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
        self.order_button = QPushButton("Корзина")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        self.test_val_button = QPushButton("Тест валидации")
        self.test_val_button.setStyleSheet("background-color: #FF8C00; color: white; padding: 5px; border-radius: 5px;")
        self.test_val_button.clicked.connect(self.open_validation_test)

        button_style = "background-color: #70B2AF; color: white; font-family: Calibri; padding: 8px; border-radius: 5px; font-weight: bold;"
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)

        self.order_button.clicked.connect(lambda: self.switch_page(2))
        self.manager_button.clicked.connect(lambda: self.switch_page(2))
        self.admin_button.clicked.connect(lambda: self.switch_page(2))

        button_layout.addStretch()
        button_layout.addWidget(self.test_val_button)
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
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Наименование", "Количество", "Цена", "Сумма", "ID"])
        self.cart_table.setColumnHidden(4, True)
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        orders_layout.addWidget(self.cart_table)
        
        self.remove_btn = QPushButton("Удалить выбранное")
        self.remove_btn.setStyleSheet("background-color: #ff8080; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.remove_btn.clicked.connect(self.remove_from_cart)
        orders_layout.addWidget(self.remove_btn)

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
        
    def open_validation_test(self):
        dialog = ValidationDialog()
        dialog.exec()

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.setWindowTitle("Мир аудиотехники — Каталог")
        elif index == 1:
            self.setWindowTitle("Мир аудиотехники — Карточка товара")
        elif index == 2:
            self.setWindowTitle("Мир аудиотехники — Корзина")

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
            card = create_card(product, self.db, self)
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

    def open_product_card(self, product_id):
        card = ProductCard(product_id, self)
        card.exec()

    def add_to_cart(self, product_id, variant_id, name, quantity, price):
        from decimal import Decimal
        if quantity <= 0:
            QMessageBox.warning(self, "Количество", "Выберите количество больше 0")
            return

        price = Decimal(str(price))
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(name))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(str(price)))
        self.cart_table.setItem(row, 3, QTableWidgetItem(str(quantity * price)))

        identity = QTableWidgetItem(str(product_id))
        identity.setData(Qt.ItemDataRole.UserRole, variant_id)
        self.cart_table.setItem(row, 4, identity)
        
        self.switch_page(2)

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            self.cart_table.removeRow(row)

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
    QApplication.setApplicationName("PP02")
    db = Database()
    app.aboutToQuit.connect(db.close_all)
    window = LoginWindow(db)
    window.show()
    sys.exit(app.exec())