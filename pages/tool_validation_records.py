from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QHBoxLayout
)
from PySide6.QtCore import Qt, QDate
from models.models import ToolRegistration, ToolType, ValidationRecord, LabTechnician
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from database.db import get_db
from datetime import datetime, timedelta

class ToolValidationRecordsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Validation Records")
        self.setMinimumSize(1000, 600)

        self.layout = QVBoxLayout()

        # Title
        title = QLabel("Tool Validation Records (Last 6 Months)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(title)

        # Serial number input
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter Tool Serial Number")
        self.layout.addWidget(self.serial_input)

        # Load button
        self.load_button = QPushButton("Load Records")
        self.load_button.clicked.connect(self.load_records)
        self.layout.addWidget(self.load_button)
        
        # Back to Dashboard Button
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        self.layout.addLayout(self.button_layout)

        # Tool info
        self.tool_info_label = QLabel("")
        self.tool_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.tool_info_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "Date",
            "Block 1", "Reading 1", "Pass/Fail 1",
            "Block 2", "Reading 2", "Pass/Fail 2",
            "Block 3", "Reading 3", "Pass/Fail 3",
            "Tolerance", "Final Result", "Technician"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def load_records(self):
        serial = self.serial_input.text().strip()

        if not serial:
            QMessageBox.warning(self, "Input Error", "Please enter a tool serial number.")
            return

        try:
            db_gen = get_db()        # Get generator
            db = next(db_gen)        # Get session object

            # Get tool and tool type
            tool = db.query(ToolRegistration).join(ToolType).filter(ToolRegistration.serial_number == serial).first()

            if not tool:
                QMessageBox.warning(self, "Not Found", f"No tool found with serial number '{serial}'")
                return

            self.tool_info_label.setText(f"Tool Serial Number: {serial} | Tool Type: {tool.tool_type.tool_name}")

            # Get validation records (last 6 months)
            six_months_ago = datetime.today() - timedelta(days=180)
            records = (
                db.query(ValidationRecord)
                .options(joinedload(ValidationRecord.technician))  # eager load technician
                .filter(
                    and_(
                        ValidationRecord.serial_number == tool.serial_number,
                        ValidationRecord.validation_date >= six_months_ago
                    )
                )
                .order_by(ValidationRecord.validation_date.desc())
                .all()
            )

            self.table.setRowCount(len(records))

            for row_index, record in enumerate(records):
                row_data = [
                    record.validation_date.strftime('%Y-%m-%d'),
                    tool.tool_type.block_1, record.reading_1, record.validation_status,  # Updated field names
                    tool.tool_type.block_2, record.reading_2, record.validation_status,
                    tool.tool_type.block_3, record.reading_3, record.validation_status,
                    tool.tool_type.tolerance, record.validation_status,  # Assuming validation status is final result
                    record.technician.name
                ]
                
                for col_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)

                    # Apply color for Pass/Fail
                    if value == 'Pass':
                        item.setForeground(Qt.green)
                    elif value == 'Fail':
                        item.setForeground(Qt.red)

                    self.table.setItem(row_index, col_index, item)

            if not records:
                QMessageBox.information(self, "No Records", "No validation records in the past 6 months.")

            db_gen.close()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading records:\n{str(e)}")

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()
