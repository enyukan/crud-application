from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from database.db import get_db
from models.models import ToolType, ToolRegistration
from utils.app_context import app_context
from datetime import datetime

class RegisterToolPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register New Tool")
        self.setFixedSize(1000, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        title = QLabel("Register New Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Serial Number
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter serial number")
        layout.addWidget(QLabel("Serial Number"))
        layout.addWidget(self.serial_input)

        # Tool Type
        self.tool_type_dropdown = QComboBox()
        layout.addWidget(QLabel("Tool Type"))
        layout.addWidget(self.tool_type_dropdown)
        self.populate_tool_types()

        # Last Calibration Date
        layout.addWidget(QLabel("Last Calibration Date"))
        self.calibration_input = QLineEdit()
        self.calibration_input.setPlaceholderText("YYYY/MM/DD")
        layout.addWidget(self.calibration_input)

        # Submit Button
        self.submit_button = QPushButton("Register Tool")
        self.submit_button.clicked.connect(self.register_tool)
        layout.addWidget(self.submit_button)

        # Back Button
        self.back_button = QPushButton("Back to Dashboard")
        self.back_button.clicked.connect(self.open_dashboard)
        layout.addWidget(self.back_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_tool_types(self):
        db = next(get_db())
        tool_types = db.query(ToolType).all()
        self.tool_type_map = {tool.tool_name: tool.tool_type_id for tool in tool_types}
        for tool_name in self.tool_type_map:
            self.tool_type_dropdown.addItem(tool_name)

    def register_tool(self):
        if app_context.get_logged_in_user() is None:  # Check if user is logged in
            QMessageBox.warning(self, "Error", "No user is logged in.")
            return  # Exit the method if no user is logged in

        logged_in_user = app_context.get_logged_in_user()
        modified_by = logged_in_user.technician_id  # Access the logged-in user’s ID safely
        serial_number = self.serial_input.text().strip()
        selected_tool_name = self.tool_type_dropdown.currentText()
        try:
            last_calibration = datetime.strptime(self.calibration_input.text().strip(), "%Y/%m/%d").date()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid date format. Use YYYY/MM/DD.")
            return
        tool_status = "Active"

        if not serial_number or not selected_tool_name:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        tool_type_id = self.tool_type_map.get(selected_tool_name)

        new_tool = ToolRegistration(
            serial_number=serial_number,
            tool_type_id=tool_type_id,
            tool_status=tool_status,
            last_calibration=last_calibration,
            modified_by=modified_by
        )

        try:
            db = next(get_db())
            db.add(new_tool)
            db.commit()
            QMessageBox.information(self, "Success", "Tool registered successfully!")
            self.clear_form()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"Failed to register tool: {str(e)}")

    def clear_form(self):
        self.serial_input.clear()

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.dashboard = DashboardPage()
        self.dashboard.show()
        self.close()
