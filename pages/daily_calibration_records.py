from PySide6.QtWidgets import ( 
    QWidget, QVBoxLayout, QLabel, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QScrollArea, QHBoxLayout, QLineEdit
)
from PySide6.QtGui import QShortcut
from PySide6.QtCore import Qt, QDate
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import ToolRegistration, ToolType, ValidationRecord, LabTechnician

class DailyCalibrationRecordsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Validation Records")
        self.setMinimumSize(1000, 600)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Daily Validation Records")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # QDateEdit for calendar popup
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Validation Date:"))
        layout.addWidget(self.date_edit)

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
        
        # Search bar for searching records
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search records...")
        self.search_input.textChanged.connect(self.search_records)
        layout.addWidget(self.search_input)


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
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        layout.addWidget(self.table)

        # Shortcut for Ctrl + F to focus on search input
        self.search_shortcut = QShortcut(Qt.CTRL + Qt.Key_F, self)
        self.search_shortcut.activated.connect(self.focus_search_input)

        self.setLayout(layout)

    def focus_search_input(self):
        """Focus on the search input field when Ctrl + F is pressed."""
        self.search_input.setFocus()

    def search_records(self):
        """Search for records in the table based on the user's input."""
        search_text = self.search_input.text().lower()
        row_count = self.table.rowCount()

        for row in range(row_count):
            match_found = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break  # If a match is found in any column, stop checking further columns.

            self.table.setRowHidden(row, not match_found)  # Hide rows that don't match the search

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
                    if col_index in [4, 7, 10]:  # Pass/Fail 1-3 columns
                        if value == 'Pass':
                            item.setForeground(Qt.green)
                        elif value == 'Fail':
                            item.setForeground(Qt.red)

                    # Make Final Result bold and green
                    if col_index == 12:  # Final Result column
                        if value == 'Pass':
                            item.setForeground(Qt.green)
                        elif value == 'Fail':
                            item.setForeground(Qt.red)
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

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
