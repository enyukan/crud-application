from PySide6.QtWidgets import ( 
    QVBoxLayout, QPushButton, QMessageBox, QLineEdit, QDialog, QLabel, QHBoxLayout
)

from database.db import get_db
from models.models import LabTechnician
from utils.app_context import app_context
from sqlalchemy.orm import Session

class ForgotPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset Password")
        self.setFixedSize(500, 300)
        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your registered email")
        layout.addWidget(self.email_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input)

        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def reset_password(self):
        email = self.email_input.text()
        new_pw = self.new_password_input.text()
        confirm_pw = self.confirm_password_input.text()

        if new_pw != confirm_pw:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        # Get DB session
        db_gen = get_db()
        db = next(db_gen)

        technician = db.query(LabTechnician).filter_by(email=email).first()
        if technician:
            technician.password = new_pw  # Ideally hash this
            db.commit()
            QMessageBox.information(self, "Success", "Password reset successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Email not found.")
        db_gen.close()
