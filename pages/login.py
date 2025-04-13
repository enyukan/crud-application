from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from models.models import LabTechnician
from database.db import get_db
from utils.app_context import app_context 

class LoginPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QC Calibration")
        
        self.setFixedSize(1000, 600)

        # Outer layout to center the form
        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(100, 100, 100, 100)  # Optional spacing

        # Inner layout for the login form
        self.layout = QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(50, 50, 50, 50)

        # Title
        self.title = QLabel("Login Page")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your name")
        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel("Password"))
        self.layout.addWidget(self.password_input)
        
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

        # Buttons
        self.button_layout = QHBoxLayout()

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.button_layout.addWidget(self.login_button)
        self.login_button.setDefault(True)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.open_register)
        self.button_layout.addWidget(self.register_button)

        self.layout.addLayout(self.button_layout)

        # Center form in outer layout
        self.outer_layout.addStretch()
        self.outer_layout.addLayout(self.layout)
        self.outer_layout.addStretch()

        container = QWidget()
        container.setLayout(self.outer_layout)
        self.setCentralWidget(container)
        
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        db = next(get_db())
        user = db.query(LabTechnician).filter(LabTechnician.name == username).first()

        if user and user.password == password:
            app_context.set_logged_in_user(user)  # Set the logged-in user in AppContext
            self.open_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect name or password.")


    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.dashboard = DashboardPage()
        self.dashboard.show()
        self.close()

    def open_register(self):
        from pages.register import RegisterPage
        self.register_page = RegisterPage()
        self.register_page.show()
        self.close()

