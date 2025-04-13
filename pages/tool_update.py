from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox,
    QGridLayout, QGroupBox

)
from PySide6.QtCore import Qt, QDateTime, QTimer
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
        
        
        
        # Top section: Dropdown to select tool type and select button
        title = QLabel("Update Tool Type")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Top section: Tool serial search
        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Tool Serial Number")
        top_layout.addWidget(self.search_input)
        # Debounced search with QTimer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(400)  # Wait 400ms after typing stops
        self.search_timer.timeout.connect(self.load_tool_data)
        self.search_input.textChanged.connect(lambda: self.search_timer.start())

        layout.addLayout(top_layout)

        # Center layout using a grid
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)

        bold_style = "font-weight: bold;"

        # Row 0 - Section headers
        form_layout.addWidget(QLabel(""), 0, 0)  # Empty top-left cell
        current_data_label = QLabel("Current Data")
        current_data_label.setStyleSheet(bold_style)
        form_layout.addWidget(current_data_label, 0, 1)

        modification_label = QLabel("Your Modification")
        modification_label.setStyleSheet(bold_style)
        form_layout.addWidget(modification_label, 0, 2)

        # Row 1 - Serial Number
        form_layout.addWidget(QLabel("Serial Number:"), 1, 0)
        self.serial_label = QLabel("-")
        self.serial_input = QLineEdit()
        form_layout.addWidget(self.serial_label, 1, 1)
        form_layout.addWidget(self.serial_input, 1, 2)

        # Row 2 - Tool Type
        form_layout.addWidget(QLabel("Tool Type:"), 2, 0)
        self.type_label = QLabel("-")
        self.type_dropdown = QComboBox()
        self.populate_tool_type_dropdown()
        form_layout.addWidget(self.type_label, 2, 1)
        form_layout.addWidget(self.type_dropdown, 2, 2)

        # Row 3 - Last Calibration Date
        form_layout.addWidget(QLabel("Last Calibration Date:"), 3, 0)
        self.date_label = QLabel("-")
        self.date_input = QLineEdit()
        form_layout.addWidget(self.date_label, 3, 1)
        form_layout.addWidget(self.date_input, 3, 2)

        # Row 4 - Tool Status
        form_layout.addWidget(QLabel("Tool Status:"), 4, 0)
        self.status_label = QLabel("-")
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["", "Active", "Sent for Calibration", "Retired"])
        form_layout.addWidget(self.status_label, 4, 1)
        form_layout.addWidget(self.status_dropdown, 4, 2)

        layout.addLayout(form_layout)

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