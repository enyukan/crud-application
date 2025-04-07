from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from models.models import LabTechnician
from database.db import get_db

from pages.login import LoginPage  # Add this at the top of register.py

class RegisterPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register New Technician")
        self.setFixedSize(1000, 750)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(30, 30, 30, 30)

        self.title = QLabel("Register Lab Technician")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.layout.addWidget(QLabel("Email"))
        self.layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel("Password"))
        self.layout.addWidget(self.password_input)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)
        self.layout.addWidget(self.register_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def register_user(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        db = next(get_db())
        existing_user = db.query(LabTechnician).filter(LabTechnician.email == email).first()

        if existing_user:
            QMessageBox.warning(self, "Error", "Email already registered.")
            return

        new_user = LabTechnician(name=name, email=email, password=password)
        db.add(new_user)
        db.commit()

        QMessageBox.information(self, "Success", "Account created successfully!")

        self.login_page = LoginPage()
        self.login_page.show()
        self.close()

    def back_to_login(self):
        from pages.login import LoginPage  # 💡 Moved import here
        self.login_page = LoginPage()
        self.login_page.show()
        self.close()
