from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from models.models import LabTechnician
from database.db import get_db

from pages.login import LoginPage  # Avoid circular import

class RegisterPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QC Calibration")

        # Outer layout to center the form
        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(100, 100, 100, 100)

        # Inner layout for the form
        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.title = QLabel("Register Lab Technician")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.layout.addWidget(QLabel("Email"))
        self.layout.addWidget(self.email_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel("Password"))
        self.layout.addWidget(self.password_input)

        
       # Buttons in the same row
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)

        self.back_button = QPushButton("Back to Login")
        self.back_button.clicked.connect(self.back_to_login)

        self.button_layout.addWidget(self.register_button)
        self.button_layout.addWidget(self.back_button)

        self.layout.addLayout(self.button_layout)

        # Center the inner layout
        self.outer_layout.addStretch()
        self.outer_layout.addLayout(self.layout)
        self.outer_layout.addStretch()

        container = QWidget()
        container.setLayout(self.outer_layout)
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
        self.login_page = LoginPage()
        self.login_page.show()
        self.close()

