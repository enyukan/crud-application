from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDateTime
from database.db import get_db
from models.models import ToolType, ToolRegistration
from utils.app_context import app_context

class UpdateToolPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Tool")
        self.setFixedSize(1000, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        # Top section: Tool serial search
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Tool Serial Number")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.load_tool_data)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(search_button)
        layout.addLayout(top_layout)

        # Center layout
        center_layout = QHBoxLayout()

        # Labels on the left
        label_layout = QVBoxLayout()
        label_layout.addWidget(QLabel("Serial Number:"))
        label_layout.addWidget(QLabel("Tool Type:"))
        label_layout.addWidget(QLabel("Last Calibration Date:"))
        label_layout.addWidget(QLabel("Tool Status:"))
        
        self.middle_layout = QVBoxLayout()
        
        # Label for "Current Data"
        current_data_label = QLabel("Current Data")
        current_data_label.setAlignment(Qt.AlignCenter)
        current_data_label.setStyleSheet("font-weight: bold;")
        self.middle_layout.addWidget(current_data_label)
        
        # Middle layout for current data
        self.serial_label = QLabel("-")
        self.type_label = QLabel("-")
        self.date_label = QLabel("-")
        self.status_label = QLabel("-")

        self.middle_layout.addWidget(self.serial_label)
        self.middle_layout.addWidget(self.type_label)
        self.middle_layout.addWidget(self.date_label)
        self.middle_layout.addWidget(self.status_label)

        # Right layout for modification
        self.right_layout = QVBoxLayout()
        
         # Label for "Your Modification"
        modification_label = QLabel("Your Modification")
        modification_label.setAlignment(Qt.AlignCenter)
        modification_label.setStyleSheet("font-weight: bold;")
        self.right_layout.addWidget(modification_label)
        
        self.serial_input = QLineEdit()
        self.type_dropdown = QComboBox()
        self.date_input = QLineEdit()
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["", "Active", "Sent for Calibration", "Retired"])

        self.populate_tool_type_dropdown()

        self.right_layout.addWidget(self.serial_input)
        self.right_layout.addWidget(self.type_dropdown)
        self.right_layout.addWidget(self.date_input)
        self.right_layout.addWidget(self.status_dropdown)

        center_layout.addLayout(label_layout)
        center_layout.addLayout(self.middle_layout)
        center_layout.addLayout(self.right_layout)

        layout.addLayout(center_layout)

        # Submit Button
        submit_button = QPushButton("Submit Change")
        submit_button.clicked.connect(self.submit_change)
        layout.addWidget(submit_button)
        
        # Back to Dashboard Button
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_tool_type_dropdown(self):
        db = next(get_db())
        tool_types = db.query(ToolType).all()
        self.tool_type_map = {t.tool_name: t.tool_type_id for t in tool_types}
        self.type_dropdown.clear()
        self.type_dropdown.addItem("")  # placeholder
        self.type_dropdown.addItems(self.tool_type_map.keys())

    def load_tool_data(self):
        serial_number = self.search_input.text()
        db = next(get_db())
        tool = db.query(ToolRegistration).filter(ToolRegistration.serial_number == serial_number).first()

        if tool:
            self.serial_label.setText(tool.serial_number)
            self.type_label.setText(tool.tool_type.tool_name if tool.tool_type else "-")
            self.date_label.setText(tool.last_calibration.strftime("%Y-%m-%d"))
            self.status_label.setText(tool.tool_status)

            # Prefill right inputs with current data
            self.serial_input.setText(tool.serial_number)
            self.type_dropdown.setCurrentText(tool.tool_type.tool_name if tool.tool_type else "")
            self.date_input.setText(tool.last_calibration.strftime("%Y-%m-%d"))
            self.status_dropdown.setCurrentText(tool.tool_status)
        else:
            QMessageBox.warning(self, "Error", "Tool not found.")

    def submit_change(self):
        original_serial = self.search_input.text()
        db = next(get_db())
        tool = db.query(ToolRegistration).filter(ToolRegistration.serial_number == original_serial).first()

        if not tool:
            QMessageBox.warning(self, "Error", "Original tool not found.")
            return

        updated = False
        new_serial = self.serial_input.text()
        new_type_name = self.type_dropdown.currentText()
        new_type_id = self.tool_type_map.get(new_type_name)
        new_date_str = self.date_input.text()
        new_status = self.status_dropdown.currentText()

        if new_serial and new_serial != tool.serial_number:
            tool.serial_number = new_serial
            updated = True
        if new_type_id and new_type_id != tool.tool_type_id:
            tool.tool_type_id = new_type_id
            updated = True
        if new_date_str:
            new_date = QDateTime.fromString(new_date_str, "yyyy-MM-dd").toPython()
            if new_date != tool.last_calibration:
                tool.last_calibration = new_date
                updated = True
        if new_status and new_status != tool.tool_status:
            tool.tool_status = new_status
            updated = True

        if updated:
            tool.last_modified = QDateTime.currentDateTime().toPython()
            if app_context.get_logged_in_user() is None:  # Check if user is logged in
                QMessageBox.warning(self, "Error", "No user is logged in.")
                return  # Exit the method if no user is logged in

            logged_in_user = app_context.get_logged_in_user()
            tool.modified_by = logged_in_user.technician_id  # Access the logged-in user’s ID safely
            db.commit()
            QMessageBox.information(self, "Success", "Tool information updated.")
            self.load_tool_data()
        else:
            QMessageBox.information(self, "No Change", "No modifications detected.")

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()