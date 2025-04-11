from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from database.db import get_db
from models.models import ToolType


class AddToolTypePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Tool Type")
        self.setFixedSize(1000, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        title = QLabel("Add New Tool Type")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Tool name input
        self.tool_name_input = QLineEdit()
        self.tool_name_input.setPlaceholderText("Tool Name")
        layout.addWidget(self.tool_name_input)

        # Block inputs
        self.block1_input = QLineEdit()
        self.block1_input.setPlaceholderText("Block 1")
        layout.addWidget(self.block1_input)

        self.block2_input = QLineEdit()
        self.block2_input.setPlaceholderText("Block 2")
        layout.addWidget(self.block2_input)

        self.block3_input = QLineEdit()
        self.block3_input.setPlaceholderText("Block 3")
        layout.addWidget(self.block3_input)

        self.tolerance_input = QLineEdit()
        self.tolerance_input.setPlaceholderText("Tolerance")
        layout.addWidget(self.tolerance_input)

        # Submit button
        add_button = QPushButton("Add Tool Type")
        add_button.clicked.connect(self.add_tool_type)
        layout.addWidget(add_button)
        
        # Back to dashboard
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_tool_type(self):
        # Get input values
        tool_name = self.tool_name_input.text()
        block1 = self.block1_input.text()
        block2 = self.block2_input.text()
        block3 = self.block3_input.text()
        tolerance = self.tolerance_input.text()

        # Validation to ensure all fields are filled in
        if not tool_name or not block1 or not block2 or not block3 or not tolerance:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        db = next(get_db())

        # Check if tool type already exists
        existing_tool_type = db.query(ToolType).filter(ToolType.tool_name == tool_name).first()
        if existing_tool_type:
            QMessageBox.warning(self, "Error", "Tool type with this name already exists.")
            return

        # Create new ToolType object
        new_tool_type = ToolType(
            tool_name=tool_name,
            block_1=block1,
            block_2=block2,
            block_3=block3,
            tolerance=tolerance
        )

        # Add to the database
        db.add(new_tool_type)
        db.commit()

        # Success message
        QMessageBox.information(self, "Success", "Tool Type added successfully!")

        # Clear fields after submission
        self.tool_name_input.clear()
        self.block1_input.clear()
        self.block2_input.clear()
        self.block3_input.clear()
        self.tolerance_input.clear()

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()