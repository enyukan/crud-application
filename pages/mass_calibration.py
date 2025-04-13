from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QPushButton, QMessageBox,
    QDateEdit, QHeaderView, QCheckBox, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from database.db import get_db
from sqlalchemy.orm import Session
from models.models import ToolType, ToolRegistration
from utils.app_context import app_context


class MassCalibrationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mass Calibration Update")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Mass Calibration Update")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Tool Type Dropdown
        self.tool_type_dropdown = QComboBox()
        self.tool_type_dropdown.currentIndexChanged.connect(self.load_tools)
        layout.addWidget(self.tool_type_dropdown)

        # Select All + Search Bar Row (both fill the row)
        top_row_layout = QHBoxLayout()

        # Select All button (will expand to fill the row)
        self.select_all_button = QPushButton("Select All Tools")
        self.select_all_button.clicked.connect(self.select_all_tools)
        self.select_all_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_row_layout.addWidget(self.select_all_button)

        # Search Bar (will expand to fill the row)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.filter_tools)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        top_row_layout.addWidget(self.search_input)

        # Add stretch to push both elements to fill the row
        top_row_layout.addStretch()

        layout.addLayout(top_row_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "Serial Number", "Status", "Last Calibration Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Status and Date Picker
        update_layout = QHBoxLayout()

        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Active", "Retired", "Under Calibration"])
        update_layout.addWidget(QLabel("New Status:"))
        update_layout.addWidget(self.status_dropdown)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        update_layout.addWidget(QLabel("New Calibration Date:"))
        update_layout.addWidget(self.date_edit)

        self.update_status_checkbox = QCheckBox("Update Status")
        self.update_status_checkbox.setChecked(True)
        update_layout.addWidget(self.update_status_checkbox)

        self.update_date_checkbox = QCheckBox("Update Calibration Date")
        self.update_date_checkbox.setChecked(True)
        update_layout.addWidget(self.update_date_checkbox)

        layout.addLayout(update_layout)

        # Update Button
        self.update_button = QPushButton("Update Selected Tools")
        self.update_button.clicked.connect(self.update_selected_tools)
        layout.addWidget(self.update_button)

        # Back to Dashboard Button
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        self.setLayout(layout)
        self.load_tool_types()

    def load_tool_types(self):
        try:
            db_gen = get_db()
            db: Session = next(db_gen)

            self.tool_type_dropdown.clear()
            self.tool_type_map = {}

            tool_types = db.query(ToolType).all()
            for tool_type in tool_types:
                display = f"{tool_type.tool_name}"
                self.tool_type_dropdown.addItem(display)
                self.tool_type_map[display] = tool_type.tool_type_id

            db_gen.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tool types:\n{str(e)}")

    def load_tools(self):
        selected_text = self.tool_type_dropdown.currentText()
        if not selected_text:
            return

        tool_type_id = self.tool_type_map[selected_text]

        try:
            db_gen = get_db()
            db: Session = next(db_gen)

            self.all_tools = db.query(ToolRegistration).filter(ToolRegistration.tool_type_id == tool_type_id).all()
            db_gen.close()

            self.display_tools(self.all_tools)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tools:\n{str(e)}")

    def display_tools(self, tools):
        self.table.setRowCount(len(tools))
        for row, tool in enumerate(tools):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)

            self.table.setItem(row, 1, QTableWidgetItem(tool.serial_number))
            self.table.setItem(row, 2, QTableWidgetItem(tool.tool_status))
            self.table.setItem(row, 3, QTableWidgetItem(
                tool.last_calibration.strftime("%Y-%m-%d") if tool.last_calibration else "N/A"
            ))

    def filter_tools(self, text):
        if not hasattr(self, 'all_tools'):
            return

        filtered = [tool for tool in self.all_tools if text.lower() in tool.serial_number.lower()]
        self.display_tools(filtered)

    def update_selected_tools(self):
        new_status = self.status_dropdown.currentText() if self.update_status_checkbox.isChecked() else None
        new_date = self.date_edit.date().toPython() if self.update_date_checkbox.isChecked() else None

        current_user = app_context.get_logged_in_user()
        if not current_user:
            QMessageBox.warning(self, "No User", "No logged-in user found.")
            return

        try:
            db_gen = get_db()
            db: Session = next(db_gen)

            updated = 0
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox.isChecked():
                    serial_number = self.table.item(row, 1).text()
                    tool = db.query(ToolRegistration).filter_by(serial_number=serial_number).first()
                    if tool:
                        if new_status:
                            tool.tool_status = new_status
                        if new_date:
                            tool.last_calibration = new_date
                        tool.modified_by = current_user.technician_id
                        updated += 1

            db.commit()
            db_gen.close()

            QMessageBox.information(self, "Success", f"Updated {updated} tools.")
            self.load_tools()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update tools:\n{str(e)}")

    def select_all_tools(self):
        all_selected = all(self.table.cellWidget(row, 0).isChecked() for row in range(self.table.rowCount()))
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            checkbox.setChecked(not all_selected)

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()
