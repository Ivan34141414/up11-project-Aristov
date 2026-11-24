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
                               QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, 
                               QStackedWidget, QDateEdit)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QStandardPaths, QDate
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


class AddOrderDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.added_items = []
        self.setWindowTitle("Добавить заказ")
        self.resize(400, 550)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.client_combo = QComboBox()
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, CONCAT_WS(' ', last_name, first_name) FROM users WHERE role_id = 3")
                for user in cursor.fetchall():
                    self.client_combo.addItem(user[1], user[0])
                cursor.close()
            finally:
                self.db.release_connection(conn)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Завершён"])
        self.status_combo.setCurrentIndex(0)

        layout.addWidget(QLabel("Клиент:"))
        layout.addWidget(self.client_combo)
        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_combo)

        layout.addWidget(QLabel("Поиск товара:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        layout.addWidget(self.search_input)

        layout.addWidget(QLabel("Товар:"))
        self.product_combo = QComboBox()
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        layout.addWidget(self.product_combo)

        layout.addWidget(QLabel("Размер (Вариант):"))
        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self.on_size_selected)
        layout.addWidget(self.size_combo)

        layout.addWidget(QLabel("Количество:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        layout.addWidget(self.quantity_spin)

        self.add_item_btn = QPushButton("Добавить в заказ")
        self.add_item_btn.clicked.connect(self.add_item_to_order)
        layout.addWidget(self.add_item_btn)

        self.items_label = QLabel("Добавлено позиций: 0")
        layout.addWidget(self.items_label)

        self.save_button = QPushButton("Сохранить заказ")
        self.save_button.clicked.connect(self.save_order)
        layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.load_products()

    def load_products(self):
        search = self.search_input.text().strip()
        conn = self.db.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT product_id, name, price FROM products WHERE name ILIKE %s"
            cursor.execute(query, (f"%{search}%",))
            self.product_combo.clear()
            for row in cursor.fetchall():
                self.product_combo.addItem(f"{row[1]} ({row[2]} руб.)", (row[0], float(row[2])))
            cursor.close()
        except Exception as e:
            print(f"Ошибка поиска: {e}")
        finally:
            self.db.release_connection(conn)

    def on_product_selected(self):
        product_data = self.product_combo.currentData()
        if not product_data:
            self.size_combo.clear()
            return
        product_id = product_data[0]

        conn = self.db.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = """
                SELECT v.variant_id, v.value, si.quantity
                FROM stock_items si
                JOIN variants v ON si.variant_id = v.variant_id
                WHERE si.product_id = %s AND si.quantity > 0
            """
            cursor.execute(query, (product_id,))
            self.size_combo.clear()
            for row in cursor.fetchall():
                self.size_combo.addItem(f"{row[1]} (В наличии: {row[2]})", (row[0], row[2]))
            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки размеров: {e}")
        finally:
            self.db.release_connection(conn)

    def on_size_selected(self):
        variant_data = self.size_combo.currentData()
        if variant_data:
            max_qty = variant_data[1]
            self.quantity_spin.setMaximum(max_qty if max_qty > 0 else 1)
        else:
            self.quantity_spin.setMaximum(1)

    def add_item_to_order(self):
        product_data = self.product_combo.currentData()
        variant_data = self.size_combo.currentData()
        
        if not product_data or not variant_data:
            QMessageBox.warning(self, "Ошибка", "Выберите товар и размер")
            return

        product_id = product_data[0]
        price = product_data[1]
        variant_id = variant_data[0]
        quantity = self.quantity_spin.value()

        if quantity > variant_data[1]:
            QMessageBox.warning(self, "Ошибка", "Недостаточно товара на складе")
            return

        self.added_items.append({
            'product_id': product_id,
            'variant_id': variant_id,
            'quantity': quantity,
            'price': price
        })
        
        self.items_label.setText(f"Добавлено позиций: {len(self.added_items)}")
        QMessageBox.information(self, "Успех", "Товар добавлен в заказ")

    def save_order(self):
        conn = self.db.get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            user_id = self.client_combo.currentData()
            status = self.status_combo.currentText()
            
            cursor.execute(
                "INSERT INTO orders (order_date, user_id, status) VALUES (%s, %s, %s) RETURNING order_id",
                (datetime.now().date(), user_id, status)
            )
            order_id = cursor.fetchone()[0]

            for item in self.added_items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, item['product_id'], item['variant_id'], item['quantity'], item['price'])
                )
                cursor.execute(
                    "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant_id = %s",
                    (item['quantity'], item['product_id'], item['variant_id'])
                )

            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Заказ добавлен")
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
        finally:
            self.db.release_connection(conn)


class EditOrderDialog(QDialog):
    def __init__(self, db, order_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.setWindowTitle("Редактировать заказ")
        self.resize(600, 550)
        self.setup_ui()
        self.load_order_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)

        self.client_combo = QComboBox()
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, CONCAT_WS(' ', last_name, first_name) FROM users WHERE role_id = 3")
                for user in cursor.fetchall():
                    self.client_combo.addItem(user[1], user[0])
                cursor.close()
            finally:
                self.db.release_connection(conn)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Завершён"])

        layout.addWidget(QLabel("Дата:"))
        layout.addWidget(self.date_edit)
        
        self.save_date_btn = QPushButton("Сохранить дату")
        self.save_date_btn.clicked.connect(self.save_date)
        layout.addWidget(self.save_date_btn)

        layout.addWidget(QLabel("Клиент:"))
        layout.addWidget(self.client_combo)
        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_combo)

        self.save_order_btn = QPushButton("Сохранить клиента и статус")
        self.save_order_btn.clicked.connect(self.save_order)
        layout.addWidget(self.save_order_btn)

        layout.addWidget(QLabel("Состав заказа:"))
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Товар", "Кол-во", "Цена", "Сумма"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.items_table)

        self.delete_item_btn = QPushButton("Удалить позицию")
        self.delete_item_btn.clicked.connect(self.remove_item)
        layout.addWidget(self.delete_item_btn)

        self.total_label = QLabel("Итого: 0 ₽")
        layout.addWidget(self.total_label)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    def load_order_data(self):
        if not self.order_id:
            return
        conn = self.db.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT order_date, user_id, status FROM orders WHERE order_id = %s"
            cursor.execute(query, (self.order_id,))
            order = cursor.fetchone()

            if order is None:
                QMessageBox.critical(self, "Ошибка", "Заказ не найден")
                self.reject()
                return

            qdate = QDate(order[0].year, order[0].month, order[0].day)
            self.date_edit.setDate(qdate)

            index = self.client_combo.findData(order[1])
            if index >= 0:
                self.client_combo.setCurrentIndex(index)

            self.status_combo.setCurrentText(order[2] or "Новый")
            cursor.close()
            self.load_items()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.reject()
        finally:
            self.db.release_connection(conn)

    def load_items(self):
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = """
                SELECT oi.order_item_id, COALESCE(p.name, 'Товар удален'), oi.quantity, oi.price, (oi.quantity * oi.price)
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """
            cursor.execute(query, (self.order_id,))
            items = cursor.fetchall()
            self.items_table.setRowCount(len(items))
            for row, item in enumerate(items):
                name_item = QTableWidgetItem(item[1])
                name_item.setData(Qt.ItemDataRole.UserRole, item[0])
                self.items_table.setItem(row, 0, name_item)
                self.items_table.setItem(row, 1, QTableWidgetItem(str(item[2])))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(item[3])))
                self.items_table.setItem(row, 3, QTableWidgetItem(str(item[4])))
            cursor.close()
            self.load_total()
        except Exception as e:
            print(f"Ошибка загрузки состава: {e}")
        finally:
            self.db.release_connection(conn)

    def load_total(self):
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM order_items WHERE order_id = %s", (self.order_id,))
            total = cursor.fetchone()[0]
            self.total_label.setText(f"Итого: {total} ₽")
            cursor.close()
        except Exception as e:
            print(f"Ошибка подсчета суммы: {e}")
        finally:
            self.db.release_connection(conn)

    def save_date(self):
        conn = self.db.get_connection()
        if not conn: return
        try:
            new_date = self.date_edit.date().toString("yyyy-MM-dd")
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET order_date = %s WHERE order_id = %s", (new_date, self.order_id))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Дата обновлена")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def save_order(self):
        conn = self.db.get_connection()
        if not conn: return
        try:
            user_id = self.client_combo.currentData()
            status = self.status_combo.currentText()
            cursor = conn.cursor()
            query = "UPDATE orders SET user_id = %s, status = %s WHERE order_id = %s"
            cursor.execute(query, (user_id, status, self.order_id))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Клиент и статус обновлены")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def remove_item(self):
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите позицию для удаления")
            return
        item = self.items_table.item(row, 0)
        order_item_id = item.data(Qt.ItemDataRole.UserRole)
        if not order_item_id: return

        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM order_items WHERE order_item_id = %s", (order_item_id,))
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", "Позиция удалена")
            self.load_items()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)


class ProductCard(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db = parent.db if parent is not None else None
        self.product = {}
        self.setWindowTitle("Карточка товара")
        self.resize(400, 650)
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
        self.delete_button = QPushButton("Удалить товар")
        self.delete_button.setStyleSheet("background-color: #ff8080; color: white; font-weight: bold; padding: 8px; border-radius: 5px;")
        self.delete_button.clicked.connect(self.delete_product)

        if self.parent() and getattr(self.parent(), 'role_id', None) != 1:
            self.delete_button.hide()

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
        layout.addWidget(self.delete_button)

    def load_product(self, product_id):
        if not self.db: return
        conn = self.db.get_connection()
        if not conn: return
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
            self.delete_button.setEnabled(False)
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
        if not file_path: return
        if QPixmap(file_path).isNull():
            QMessageBox.warning(self, "Изображение", "Файл не является изображением")
            return

        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        target = Path(base) / "images" / (uuid.uuid4().hex + Path(file_path).suffix)

        conn = self.db.get_connection()
        if not conn: return
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

    def delete_product(self):
        reply = QMessageBox.question(self, "Удаление", "Вы уверены, что хотите удалить товар?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM order_items WHERE product_id = %s LIMIT 1", (self.product_id,))
            if cursor.fetchone():
                QMessageBox.critical(self, "Ошибка", "Товар нельзя удалить: он есть в заказах")
                return
            cursor.execute("DELETE FROM stock_items WHERE product_id = %s", (self.product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = %s", (self.product_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Товар удалён")
            if self.parent():
                self.parent().load_products()
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
        finally:
            self.db.release_connection(conn)

    def on_variant_changed(self, index=0):
        selected = self.size_combo.currentData()
        available = max(0, int(selected[1])) if selected else 0
        if available > 0:
            self.quantity_spin.setRange(1, available)
        else:
            self.quantity_spin.setRange(0, 0)
        self.add_button.setEnabled(available > 0)

    def add_selected_to_cart(self):
        main_window = self.parent()
        if main_window and getattr(main_window, 'user_id', None) is None:
            QMessageBox.warning(self, "Ошибка", "Войдите в систему, чтобы добавлять товары в корзину")
            return
        selected = self.size_combo.currentData()
        if not selected or self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Остаток", "Нет доступного остатка")
            return
        variant_id = selected[0]
        quantity = self.quantity_spin.value()
        name = self.product.get("name", "Неизвестно")
        price = self.product.get("price", 0)
        product_id = self.product_id
        if main_window and hasattr(main_window, "add_to_cart"):
            main_window.add_to_cart(product_id, variant_id, name, quantity, price)
            self.accept()


class OrderDetailsDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.db = parent.db if parent is not None else None
        self.setWindowTitle(f"Состав заказа №{order_id}")
        self.resize(600, 400)
        self.setup_ui()
        self.load_order_details(order_id)
        self.load_total(order_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Наименование", "Количество", "Цена", "Сумма"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.details_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.details_table)
        self.total_label = QLabel("Итого: 0 ₽")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E8B57; margin-top: 10px;")
        layout.addWidget(self.total_label)

    def load_order_details(self, order_id):
        if not order_id or not self.db: return
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = """
                SELECT COALESCE(p.name, 'Товар удален') AS name, 
                oi.quantity, oi.price, (oi.quantity * oi.price) AS total 
                FROM order_items oi 
                LEFT JOIN products p ON oi.product_id = p.product_id 
                WHERE oi.order_id = %s
            """
            cursor.execute(query, (order_id,))
            items = cursor.fetchall()
            self.details_table.setRowCount(len(items))
            for row, item in enumerate(items):
                self.details_table.setItem(row, 0, QTableWidgetItem(item[0]))
                self.details_table.setItem(row, 1, QTableWidgetItem(str(item[1])))
                self.details_table.setItem(row, 2, QTableWidgetItem(str(item[2])))
                self.details_table.setItem(row, 3, QTableWidgetItem(str(item[3])))
            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки состава: {e}")
        finally:
            self.db.release_connection(conn)

    def load_total(self, order_id):
        if not order_id or not self.db: return
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "SELECT COALESCE(SUM(quantity * price), 0) AS total FROM order_items WHERE order_id = %s"
            cursor.execute(query, (order_id,))
            total = cursor.fetchone()[0]
            self.total_label.setText(f"Итого: {total} ₽")
            cursor.close()
        except Exception as e:
            print(f"Ошибка подсчета суммы: {e}")
        finally:
            self.db.release_connection(conn)


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
        try:
            quantity = int(self.quantity_input.text())
            if quantity <= 0: raise ValueError("Количество должно быть положительным")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите число в поле 'Количество'")
            return
        try:
            price = float(self.price_input.text())
            if price <= 0: raise ValueError("Цена должна быть положительной")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите число в поле 'Цена'")
            return
        if not self.name_input.text():
            QMessageBox.critical(self, "Ошибка", "Введите наименование")
            return
        try:
            datetime.strptime(self.date_input.text(), "%d.%m.%Y")
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
        self.add_order_button = QPushButton("Добавить заказ")
        self.test_val_button = QPushButton("Тест валидации")
        self.test_val_button.setStyleSheet("background-color: #FF8C00; color: white; padding: 5px; border-radius: 5px;")
        self.test_val_button.clicked.connect(self.open_validation_test)
        button_style = "background-color: #70B2AF; color: white; font-family: Calibri; padding: 8px; border-radius: 5px; font-weight: bold;"
        self.order_button.setStyleSheet(button_style)
        self.manager_button.setStyleSheet(button_style)
        self.admin_button.setStyleSheet(button_style)
        self.add_order_button.setStyleSheet(button_style)
        self.order_button.clicked.connect(lambda: self.switch_page(2))
        self.manager_button.clicked.connect(lambda: self.switch_page(2))
        self.admin_button.clicked.connect(lambda: self.switch_page(2))
        self.add_order_button.clicked.connect(self.open_add_order_dialog)
        button_layout.addStretch()
        button_layout.addWidget(self.test_val_button)
        button_layout.addWidget(self.order_button)
        button_layout.addWidget(self.manager_button)
        button_layout.addWidget(self.admin_button)
        button_layout.addWidget(self.add_order_button)
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
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["Дата", "ФИО клиента", "Сумма", "Статус"])
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.cellClicked.connect(self.on_order_click)
        orders_layout.addWidget(self.orders_table)
        
        self.edit_order_btn = QPushButton("Редактировать заказ")
        self.edit_order_btn.setStyleSheet("background-color: #70B2AF; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.edit_order_btn.clicked.connect(self.open_edit_order_dialog)
        orders_layout.addWidget(self.edit_order_btn)

        self.delete_order_btn = QPushButton("Удалить заказ")
        self.delete_order_btn.setStyleSheet("background-color: #ff8080; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.delete_order_btn.clicked.connect(self.delete_order)
        orders_layout.addWidget(self.delete_order_btn)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Наименование", "Количество", "Цена", "Сумма", "ID"])
        self.cart_table.setColumnHidden(4, True)
        self.cart_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        orders_layout.addWidget(self.cart_table)
        self.total_label = QLabel("Итого: 0 ₽")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E8B57; margin-top: 10px;")
        orders_layout.addWidget(self.total_label)
        qty_layout = QHBoxLayout()
        self.qty_label = QLabel("Новое количество:")
        qty_layout.addWidget(self.qty_label)
        self.qty_change_spin = QSpinBox()
        self.qty_change_spin.setMinimum(1)
        self.qty_change_spin.setMaximum(999)
        qty_layout.addWidget(self.qty_change_spin)
        self.change_qty_btn = QPushButton("Изменить количество")
        self.change_qty_btn.setStyleSheet("background-color: #70B2AF; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.change_qty_btn.clicked.connect(self.change_quantity)
        qty_layout.addWidget(self.change_qty_btn)
        orders_layout.addLayout(qty_layout)
        self.remove_btn = QPushButton("Удалить выбранное")
        self.remove_btn.setStyleSheet("background-color: #ff8080; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.remove_btn.clicked.connect(self.remove_from_cart)
        orders_layout.addWidget(self.remove_btn)
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Статус заказа:")
        status_layout.addWidget(self.status_label)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Новый", "В обработке", "Завершён"])
        self.status_combo.setCurrentText("Новый")
        status_layout.addWidget(self.status_combo)
        orders_layout.addLayout(status_layout)
        self.checkout_btn = QPushButton("Подтвердить заказ")
        self.checkout_btn.setStyleSheet("background-color: #2E8B57; color: white; padding: 15px; border-radius: 5px; font-weight: bold; font-size: 16px;")
        self.checkout_btn.clicked.connect(self.confirm_order)
        orders_layout.addWidget(self.checkout_btn)
        self.stacked_widget.addWidget(self.catalog_page)
        self.stacked_widget.addWidget(self.product_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.setCurrentIndex(0)
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; font-family: Calibri; } QLabel { color: #000000; }")

    def open_add_order_dialog(self):
        dialog = AddOrderDialog(self.db, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and self.role_id in (1, 2):
            self.load_orders()

    def open_edit_order_dialog(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return
        item = self.orders_table.item(row, 0)
        if item:
            order_id = item.data(Qt.ItemDataRole.UserRole)
            if order_id:
                dialog = EditOrderDialog(self.db, order_id, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_orders()

    def delete_order(self):
        row = self.orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")
            return
        item = self.orders_table.item(row, 0)
        if item:
            order_id = item.data(Qt.ItemDataRole.UserRole)
            if not order_id:
                QMessageBox.warning(self, "Ошибка", "Выберите заказ")
                return

            reply = QMessageBox.question(
                self, "Удаление", "Вы уверены, что хотите удалить заказ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

            conn = self.db.get_connection()
            if not conn: return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
                cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
                conn.commit()   
                cursor.close()
                QMessageBox.information(self, "Успех", "Заказ удалён")
                self.load_orders()
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
            finally:
                self.db.release_connection(conn)

    def open_validation_test(self):
        dialog = ValidationDialog()
        dialog.exec()

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0: self.setWindowTitle("Мир аудиотехники — Каталог")
        elif index == 1: self.setWindowTitle("Мир аудиотехники — Карточка товара")
        elif index == 2:
            self.setWindowTitle("Мир аудиотехники — Заказы")
            if self.role_id in (1, 2): self.load_orders()

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0: self.switch_page(current_index - 1)

    def load_products(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
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

    def load_orders(self):
        if self.role_id not in (1, 2): return
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = """
                SELECT o.order_id, o.order_date, 
                CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) AS full_name, 
                COALESCE(SUM(oi.quantity * oi.price), 0) AS total, 
                o.status 
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                GROUP BY o.order_id, u.last_name, u.first_name, u.middle_name, o.status 
                ORDER BY o.order_date DESC
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            self.orders_table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                date_item = QTableWidgetItem(str(order[1]))
                date_item.setData(Qt.ItemDataRole.UserRole, order[0])
                self.orders_table.setItem(row, 0, date_item)
                self.orders_table.setItem(row, 1, QTableWidgetItem(order[2] or "Неизвестно"))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order[3])))
                self.orders_table.setItem(row, 3, QTableWidgetItem(order[4] or "Новый"))
            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
        finally:
            self.db.release_connection(conn)

    def on_order_click(self, row, column):
        item = self.orders_table.item(row, 0)
        if item:
            order_id = item.data(Qt.ItemDataRole.UserRole)
            dialog = OrderDetailsDialog(order_id, self)
            dialog.exec()

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show(); self.manager_button.show(); self.add_order_button.show(); self.order_button.hide()
            self.orders_table.show(); self.edit_order_btn.show(); self.delete_order_btn.show()
            self.cart_table.hide(); self.total_label.hide(); self.qty_label.hide()
            self.qty_change_spin.hide(); self.change_qty_btn.hide(); self.remove_btn.hide()
            self.status_label.hide(); self.status_combo.hide(); self.checkout_btn.hide()
        elif self.role_id == 2:
            self.admin_button.hide(); self.manager_button.show(); self.add_order_button.show(); self.order_button.hide()
            self.orders_table.show(); self.edit_order_btn.hide(); self.delete_order_btn.hide()
            self.cart_table.hide(); self.total_label.hide(); self.qty_label.hide()
            self.qty_change_spin.hide(); self.change_qty_btn.hide(); self.remove_btn.hide()
            self.status_label.hide(); self.status_combo.hide(); self.checkout_btn.hide()
        elif self.role_id == 3:
            self.admin_button.hide(); self.manager_button.hide(); self.add_order_button.hide(); self.order_button.show()
            self.orders_table.hide(); self.edit_order_btn.hide(); self.delete_order_btn.hide()
            self.cart_table.show(); self.total_label.show(); self.qty_label.show()
            self.qty_change_spin.show(); self.change_qty_btn.show(); self.remove_btn.show()
            self.status_label.show(); self.status_combo.show(); self.checkout_btn.show()
        else:
            self.admin_button.hide(); self.manager_button.hide(); self.add_order_button.hide(); self.order_button.hide()
            self.orders_table.hide(); self.edit_order_btn.hide(); self.delete_order_btn.hide()
            self.cart_table.hide(); self.total_label.hide(); self.qty_label.hide()
            self.qty_change_spin.hide(); self.change_qty_btn.hide(); self.remove_btn.hide()
            self.status_label.hide(); self.status_combo.hide(); self.checkout_btn.hide()

    def open_product_card(self, product_id):
        card = ProductCard(product_id, self)
        card.exec()

    def add_to_cart(self, product_id, variant_id, name, quantity, price):
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
        self.update_total()
        self.switch_page(2)

    def change_quantity(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            new_quantity = self.qty_change_spin.value()
            price = Decimal(self.cart_table.item(row, 2).text())
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(new_quantity)))
            row_sum = new_quantity * price
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(row_sum)))
            self.update_total()

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            self.cart_table.removeRow(row)
            self.update_total()

    def update_total(self):
        if self.cart_table.rowCount() == 0:
            self.total_label.setText("Итого: 0 ₽")
            return
        total = Decimal("0")
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 3)
            if item: total += Decimal(item.text())
        self.total_label.setText(f"Итого: {total} ₽")

    def confirm_order(self):
        if self.user_id is None:
            QMessageBox.warning(self, "Заказ", "Сначала войдите в систему")
            return
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Заказ", "Корзина пуста")
            return
        status = self.status_combo.currentText()
        if status not in ("Новый", "В обработке", "Завершён"):
            QMessageBox.warning(self, "Заказ", "Выберите статус")
            return
        conn = self.db.get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            with conn.cursor() as cursor:
                for row in range(self.cart_table.rowCount()):
                    identity = self.cart_table.item(row, 4)
                    quantity_item = self.cart_table.item(row, 1)
                    if any(x is None for x in (identity, quantity_item)):
                        raise ValueError("В позиции отсутствует ID или количество")
                    product_id = int(identity.text())
                    variant_id = int(identity.data(Qt.ItemDataRole.UserRole))
                    quantity = int(quantity_item.text())
                    cursor.execute("SELECT quantity FROM stock_items WHERE product_id = %s AND variant_id = %s", (product_id, variant_id))
                    stock_res = cursor.fetchone()
                    stock = stock_res[0] if stock_res else 0
                    if stock < quantity:
                        raise ValueError(f"Недостаточно товара (ID {product_id}) на складе")
                cursor.execute(
                    "INSERT INTO orders (order_date, user_id, status) VALUES (CURRENT_DATE, %s, %s) RETURNING order_id",
                    (self.user_id, status)
                )
                order_id = cursor.fetchone()[0]
                for row in range(self.cart_table.rowCount()):
                    identity = self.cart_table.item(row, 4)
                    quantity_item = self.cart_table.item(row, 1)
                    price_item = self.cart_table.item(row, 2)
                    product_id = int(identity.text())
                    variant_id = int(identity.data(Qt.ItemDataRole.UserRole))
                    quantity = int(quantity_item.text())
                    price = Decimal(price_item.text())
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                        (order_id, product_id, variant_id, quantity, price)
                    )
                    cursor.execute(
                        "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant_id = %s",
                        (quantity, product_id, variant_id)
                    )
                    if cursor.rowcount == 0:
                        raise ValueError(f"Нет остатков для товара (ID {product_id})")
            conn.commit()
        except (psycopg.Error, ValueError, TypeError, ArithmeticError) as error:
            conn.rollback()
            QMessageBox.critical(self, "Заказ не сохранён", str(error))
            return
        finally:
            self.db.release_connection(conn)
        self.cart_table.setRowCount(0)
        self.update_total()
        QMessageBox.information(self, "Заказ", f"Заказ №{order_id} сохранён")
        try:
            self.load_products()
        except Exception:
            QMessageBox.warning(self, "Обновление каталога", "Заказ сохранён. Обновите каталог перед следующей покупкой.")
        self.switch_page(0)

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