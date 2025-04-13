from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from database.db import get_db
from models.models import ToolRegistration, ValidationRecord
from utils.app_context import app_context
from datetime import date
from dateutil.relativedelta import relativedelta


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

        # Timer for delay in search
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.search_tool)

        # Trigger timer when user types
        self.serial_input.returnPressed.connect(self.search_tool)

        self.status_display = QLabel("")

        search_layout.addWidget(self.serial_input)

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

        # Tool Type Name Display (before the form)
        type_layout = QHBoxLayout()
        type_title = QLabel("Tool Type Name:")
        type_title.setStyleSheet("font-weight: bold;")
        self.type_label = QLabel("-")
        type_layout.addWidget(type_title)
        type_layout.addWidget(self.type_label)
        layout.addLayout(type_layout)


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
        messages = []
        styles = []
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

        # Start collecting status messages
        status_messages = []
        six_months_later = self.tool.last_calibration + relativedelta(months=6)
        # First check tool condition
        if self.tool.tool_status == "Retired":
            status_messages.append("❌ This tool is retired.")
            self.submit_button.setEnabled(False)
        elif self.tool.tool_status == "Sent for Calibration":
            status_messages.append("🔧 This tool is under calibration.")
            self.submit_button.setEnabled(False)
        elif validation_today:
            # Get the most recent validation record (latest date)
            latest_record = (
                db.query(ValidationRecord)
                .filter_by(serial_number=serial)
                .order_by(ValidationRecord.validation_date.desc())
                .first()
            )

            if latest_record and latest_record.validation_date == today:
                if validation_today.validation_status == "Fail":
                    status_messages.append("⚠️ This tool failed validation today.")
                    # allow revalidation only if this is the latest record
                    self.submit_button.setEnabled(True)
                else:
                    status_messages.append("✅ This tool has been validated today.")
                    self.submit_button.setEnabled(False)
            else:
                status_messages.append("✅ This tool has been validated today.")
                self.submit_button.setEnabled(False)

        elif today > six_months_later:
                status_messages.append(
                    f"⛔ This tool is overdue for calibration. Tool was last calibrated on {self.tool.last_calibration.strftime('%Y-%m-%d')}."
                )
                self.submit_button.setEnabled(False)
        else:
            status_messages.append("🟡 Tool ready for validation.")

        # Now check calibration deadline
        if self.tool.last_calibration and self.tool.tool_status not in ["Retired", "Sent for Calibration"]:
            five_months_later = self.tool.last_calibration + relativedelta(months=5)
            
            if today > five_months_later:
                status_messages.append(
                    f"⚠️ This tool needs to be sent for calibration by {five_months_later.strftime('%Y-%m-%d')}."
                )


        # Join and display all status messages
        self.status_display.setText("\n".join(status_messages))
        self.status_display.setStyleSheet("color: white;")

        # Fill center data
        tool_type = self.tool.tool_type
        if tool_type:
            self.type_label.setText(tool_type.tool_name)
            blocks = [tool_type.block_1, tool_type.block_2, tool_type.block_3]
            tolerance = tool_type.tolerance
            for i in range(3):
                block = blocks[i]
                if block is not None:
                    lower = block - tolerance
                    upper = block + tolerance
                    self.block_labels[i].setText(f"{block:.5f}")
                    self.tolerance_labels[i].setText(f"{lower:.5f} ~ {upper:.5f}")
                    self.reading_inputs[i].setEnabled(True)
                else:
                    self.block_labels[i].setText("-")
                    self.tolerance_labels[i].setText("-")
                    self.reading_inputs[i].clear()
                    self.reading_inputs[i].setEnabled(False)

    def check_pass_fail(self):
        if not self.tool:
            QMessageBox.warning(self, "Error", "Please search for a tool first.")
            return

        try:
            readings = [float(r.text()) if r.text() else None for r in self.reading_inputs]
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid numeric readings.")
            return

        tool_type = self.tool.tool_type
        blocks = [tool_type.block_1, tool_type.block_2, tool_type.block_3]
        tol = tool_type.tolerance

        results = []
        for i in range(3):
            block = blocks[i]
            if block is None:
                self.reading_result_labels[i].setText("N/A")
                self.reading_result_labels[i].setStyleSheet("color: gray; font-weight: bold;")
                continue

            low = block - tol
            high = block + tol
            reading = readings[i]
            if reading is None:
                self.reading_result_labels[i].setText("N/A")
                self.reading_result_labels[i].setStyleSheet("color: gray; font-weight: bold;")
                continue

            if low <= reading <= high:
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
            readings = []
            for i in range(3):
                if self.block_labels[i].text() == "-":
                    readings.append(None)
                else:
                    val = self.reading_inputs[i].text()
                    if not val:
                        QMessageBox.warning(self, "Error", f"Reading for Block {i+1} is required.")
                        return
                    readings.append(float(val))
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
        self.serial_input.clear()
        self.tool = None
        self.result_label.clear()
        self.status_display.clear()
        for i in range(3):
            self.reading_inputs[i].clear()
            self.reading_result_labels[i].clear()
            self.block_labels[i].clear()
            self.tolerance_labels[i].clear()

    def open_dashboard(self):
        self.close()
        from pages.dashboard import DashboardPage
        self.dashboard = DashboardPage()
        self.dashboard.show()
