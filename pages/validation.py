from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QDate
from database.db import get_db
from models.models import ToolRegistration, ToolType, ValidationRecord
from utils.app_context import app_context
from datetime import date


class ValidationPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Calibration Validation")
        self.setFixedSize(1000, 600)

        self.tool = None

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(20)

        # Top Section
        title_label = QLabel("Tool Calibration Validation")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        search_layout = QHBoxLayout()
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("Enter Tool Serial Number")
        self.search_button = QPushButton("Search Tool")
        self.search_button.clicked.connect(self.search_tool)
        self.status_display = QLabel("")

        search_layout.addWidget(self.serial_input)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)
        layout.addWidget(self.status_display)

        # Center Layout
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(30)
        form_layout.setVerticalSpacing(10)

        bold = "font-weight: bold;"

        # Header Row
        form_layout.addWidget(QLabel(""), 0, 0)  # Empty top-left cell
        form_layout.addWidget(QLabel("Block Value"), 0, 1)
        form_layout.addWidget(QLabel("Tolerance Range"), 0, 2)
        form_layout.addWidget(QLabel("Actual Reading"), 0, 3)
        form_layout.addWidget(QLabel("Result"), 0, 4)

        # Tool Type Row
        form_layout.addWidget(QLabel("Tool Type Name:"), 1, 0)
        self.type_label = QLabel("-")
        form_layout.addWidget(self.type_label, 1, 1)

        # Block Rows
        labels = ["Block 1:", "Block 2:", "Block 3:"]
        self.block_labels = []
        self.tolerance_labels = []
        self.reading_inputs = []
        self.reading_result_labels = []

        for i in range(3):
            form_layout.addWidget(QLabel(labels[i]), i + 2, 0)

            block_label = QLabel("-")
            tolerance_label = QLabel("-")
            reading_input = QLineEdit()
            result_label = QLabel("")
            result_label.setStyleSheet("font-weight: bold;")

            self.block_labels.append(block_label)
            self.tolerance_labels.append(tolerance_label)
            self.reading_inputs.append(reading_input)
            self.reading_result_labels.append(result_label)

            form_layout.addWidget(block_label, i + 2, 1)
            form_layout.addWidget(tolerance_label, i + 2, 2)
            form_layout.addWidget(reading_input, i + 2, 3)
            form_layout.addWidget(result_label, i + 2, 4)


        # DB Fetched
        self.type_label = QLabel("-")
        self.block_labels = [QLabel("-") for _ in range(3)]
        self.tolerance_labels = [QLabel("-") for _ in range(3)]

        form_layout.addWidget(self.type_label, 1, 1)
        for i in range(3):
            form_layout.addWidget(self.block_labels[i], i + 2, 1)
            form_layout.addWidget(self.tolerance_labels[i], i + 2, 2)

        # User Input
        self.reading_inputs = []
        self.reading_result_labels = []

        for i in range(3):
            input_field = QLineEdit()
            result_label = QLabel("")
            result_label.setStyleSheet("font-weight: bold;")  # styling
            self.reading_inputs.append(input_field)
            self.reading_result_labels.append(result_label)
            
            form_layout.addWidget(input_field, i + 2, 3)
            form_layout.addWidget(result_label, i + 2, 4)  # Add label to right of input


        layout.addLayout(form_layout)

        # Validation status display
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Pass/Fail")
        self.check_button.clicked.connect(self.check_pass_fail)
        self.submit_button = QPushButton("Submit Validation")
        self.submit_button.clicked.connect(self.submit_validation)

        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.submit_button)

        layout.addLayout(button_layout)
        
        # Back to Dashboard Button
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def search_tool(self):
        serial = self.serial_input.text().strip()
        db = next(get_db())
        self.tool = db.query(ToolRegistration).filter_by(serial_number=serial).first()

        self.submit_button.setEnabled(True)  # enable by default
        if not self.tool:
            self.status_display.setText("Tool not found.")
            self.status_display.setStyleSheet("color: red;")
            self.clear_fields()
            return

        today = date.today()
        validation_today = (
            db.query(ValidationRecord)
            .filter_by(serial_number=serial, validation_date=today)
            .first()
        )

        if validation_today:
            self.status_display.setText("This tool has been validated today.")
            self.status_display.setStyleSheet("color: green;")
        elif self.tool.tool_status == "Retired":
            self.status_display.setText("This tool is retired.")
            self.status_display.setStyleSheet("color: red;")
            self.submit_button.setEnabled(False)
        elif self.tool.tool_status == "Sent for Calibration":
            self.status_display.setText("This tool is under calibration.")
            self.status_display.setStyleSheet("color: orange;")
            self.submit_button.setEnabled(False)
        else:
            self.status_display.setText("Tool ready for validation.")
            self.status_display.setStyleSheet("color: white;")

        # Fill center data
        tool_type = self.tool.tool_type
        if tool_type:
            self.type_label.setText(tool_type.tool_name)
            blocks = [tool_type.block_1, tool_type.block_2, tool_type.block_3]
            tolerance = tool_type.tolerance

            for i in range(3):
                self.block_labels[i].setText(f"{blocks[i]}")
                self.tolerance_labels[i].setText(
                    f"{blocks[i] - tolerance:.3f} ~ {blocks[i] + tolerance:.3f}"
                )


    def check_pass_fail(self):
        if not self.tool:
            QMessageBox.warning(self, "Error", "Please search for a tool first.")
            return

        try:
            readings = [float(r.text()) for r in self.reading_inputs]
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric readings.")
            return

        tool_type = self.tool.tool_type
        blocks = [tool_type.block_1, tool_type.block_2, tool_type.block_3]
        tol = tool_type.tolerance

        results = []
        for i in range(3):
            low = blocks[i] - tol
            high = blocks[i] + tol
            if low <= readings[i] <= high:
                results.append("Pass")
                self.reading_result_labels[i].setText("Pass")
                self.reading_result_labels[i].setStyleSheet("color: green; font-weight: bold;")
            else:
                results.append("Fail")
                self.reading_result_labels[i].setText("Fail")
                self.reading_result_labels[i].setStyleSheet("color: red; font-weight: bold;")

        final = "Pass" if all(r == "Pass" for r in results) else "Fail"
        color = "green" if final == "Pass" else "red"
        self.result_label.setText(f"Result: {final}")
        self.result_label.setStyleSheet(f"color: {color}; font-weight: bold;")


    def submit_validation(self):
        if not self.tool:
            QMessageBox.warning(self, "Error", "Please search for a tool first.")
            return

        if self.tool.tool_status in ["Retired", "Sent for Calibration"]:
            QMessageBox.warning(self, "Error", "Cannot validate a retired or calibration tool.")
            return

        try:
            readings = [float(r.text()) for r in self.reading_inputs]
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid numeric readings.")
            return

        self.check_pass_fail()
        status_text = self.result_label.text()
        if not status_text.startswith("Result:"):
            QMessageBox.warning(self, "Error", "Please check pass/fail before submitting.")
            return

        final_status = "Pass" if "Pass" in status_text and "Fail" not in status_text else "Fail"

        technician = app_context.get_logged_in_user()
        if not technician:
            QMessageBox.warning(self, "Error", "No technician logged in.")
            return

        db = next(get_db())
        record = ValidationRecord(
            serial_number=self.tool.serial_number,
            validation_date=date.today(),
            technician_id=technician.technician_id,
            reading_1=readings[0],
            reading_2=readings[1],
            reading_3=readings[2],
            validation_status=final_status,
        )

        db.add(record)
        db.commit()
        QMessageBox.information(self, "Success", "Validation record submitted.")
        self.clear_fields()


    def clear_fields(self):
        self.tool = None
        self.type_label.setText("-")
        for b, t, r, res in zip(self.block_labels, self.tolerance_labels, self.reading_inputs, self.reading_result_labels):
            b.setText("-")
            t.setText("-")
            r.clear()
            res.setText("")
        self.result_label.setText("")
        self.result_label.setStyleSheet("")

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()