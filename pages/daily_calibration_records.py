from PySide6.QtWidgets import ( 
    QWidget, QVBoxLayout, QLabel, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QScrollArea, QHBoxLayout, QLineEdit
)
from PySide6.QtCore import Qt, QDate
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import ToolRegistration, ToolType, ValidationRecord, LabTechnician

class DailyCalibrationRecordsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Calibration Records")
        self.setMinimumSize(1000, 600)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Daily Calibration Records")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # QDateEdit for calendar popup
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("New Calibration Date:"))
        layout.addWidget(self.date_edit)

        # QLineEdit for user to input the date manually
        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText("Enter date (YYYY-MM-DD)")
        self.date_input.textChanged.connect(self.update_calendar_from_input)
        layout.addWidget(self.date_input)

        # Load button
        self.load_button = QPushButton("Load Records")
        self.load_button.clicked.connect(self.load_records)
        layout.addWidget(self.load_button)
        
        # Back to Dashboard Button
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(14)
        self.table.setHorizontalHeaderLabels([
            "Serial No", "Tool Type", 
            "Block 1", "Reading 1", "Pass/Fail 1",
            "Block 2", "Reading 2", "Pass/Fail 2",
            "Block 3", "Reading 3", "Pass/Fail 3",
            "Tolerance", "Final Result", "Technician"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def update_calendar_from_input(self):
        """Update the calendar when the user types a date."""
        input_date = self.date_input.text()
        try:
            date = QDate.fromString(input_date, "yyyy-MM-dd")
            if date.isValid():
                self.date_edit.setDate(date)  # Update the QDateEdit calendar
                self.date_input.setStyleSheet("background-color: white;")  # Reset background color
            else:
                self.date_input.setStyleSheet("background-color: pink;")  # Invalid date
        except:
            self.date_input.setStyleSheet("background-color: pink;")  # Invalid date

    def load_records(self):
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")  # Get date from QDateEdit
        try:
            # Get session
            db_gen = get_db()
            db = next(db_gen)

            # SQLAlchemy ORM query to fetch daily calibration records
            records = db.query(
                ToolRegistration.serial_number,
                ToolType.tool_name.label("tool_type_name"),
                ToolType.block_1,
                ValidationRecord.reading_1,
                ValidationRecord.validation_status.label("pass_fail_1"),
                ToolType.block_2,
                ValidationRecord.reading_2,
                ValidationRecord.validation_status.label("pass_fail_2"),
                ToolType.block_3,
                ValidationRecord.reading_3,
                ValidationRecord.validation_status.label("pass_fail_3"),
                ToolType.tolerance,
                ValidationRecord.validation_status.label("final_result"),
                LabTechnician.name.label("technician_name")
            ).join(ToolType, ToolRegistration.tool_type_id == ToolType.tool_type_id) \
             .join(ValidationRecord, ToolRegistration.serial_number == ValidationRecord.serial_number) \
             .join(LabTechnician, ValidationRecord.technician_id == LabTechnician.technician_id) \
             .filter(ValidationRecord.validation_date == selected_date) \
             .all()

            self.table.setRowCount(len(records))

            # Populate the table with records
            for row_index, row_data in enumerate(records):
                for col_index, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)

                    # Apply color to Pass/Fail columns
                    if col_index == 4 or col_index == 7 or col_index == 10:  # Pass/Fail columns
                        if value == 'Pass':
                            item.setForeground(Qt.green)
                        elif value == 'Fail':
                            item.setForeground(Qt.red)

                    self.table.setItem(row_index, col_index, item)

            if not records:
                QMessageBox.information(self, "No Records", "No validation records found for this date.")

            db_gen.close()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading records:\n{str(e)}")

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()
