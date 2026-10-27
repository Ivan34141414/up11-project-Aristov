from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Авторизация")
        self.resize(300, 250)
        
        layout = QVBoxLayout()
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как гость")
        self.guest_button.clicked.connect(self.login_as_guest)
        layout.addWidget(self.guest_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)

    def login_as_guest(self):
        from main import MainWindow
        self.main_window = MainWindow(role_id=None, full_name="Гость")
        self.main_window.show()
        self.close()

    def check_login(self):
        login = self.login_input.text()
        
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT user_id, role_id, last_name, first_name, middle_name FROM users WHERE login = %s", (login,))
        result = cursor.fetchone()
        cursor.close()
        self.db.release_connection(conn)

        if result is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин")
        else:
            self.user_id = result[0]
            self.role_id = result[1]
            
            last_name = result[2]
            first_name = result[3]
            middle_name = result[4]
            
            if middle_name:
                full_name = f"{last_name} {first_name} {middle_name}"
            else:
                full_name = f"{last_name} {first_name}"
            
            from main import MainWindow
            self.main_window = MainWindow(role_id=self.role_id, full_name=full_name)
            self.main_window.show()
            self.close()