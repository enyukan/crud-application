from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from database.db import get_db
from models.models import ToolType

class UpdateToolTypePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Tool Type")
        self.setFixedSize(1000, 600)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)

        # Top section: Dropdown to select tool type and select button
        title = QLabel("Update Tool Type")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Tool Type Dropdown and Select Tool Button
        tool_selection_layout = QHBoxLayout()

        self.tool_type_dropdown = QComboBox()
        self.tool_type_dropdown.addItem("Select Tool Type")  # Placeholder option
        self.populate_tool_type_dropdown()

        self.tool_type_dropdown.currentIndexChanged.connect(self.load_tool_data)
        tool_selection_layout.addWidget(self.tool_type_dropdown)

        layout.addLayout(tool_selection_layout)

        # Center section (3 columns)
        center_layout = QHBoxLayout()

        # Left section: Labels
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(QLabel(""))
        self.left_layout.addWidget(QLabel("Block 1:"))
        self.left_layout.addWidget(QLabel("Block 2:"))
        self.left_layout.addWidget(QLabel("Block 3:"))
        self.left_layout.addWidget(QLabel("Tolerance:"))

        # Center section: Data fetched from the database
        self.middle_layout = QVBoxLayout()

        # Label for "Current Data"
        current_data_label = QLabel("Current Data")
        current_data_label.setAlignment(Qt.AlignCenter)
        current_data_label.setStyleSheet("font-weight: bold;")
        self.middle_layout.addWidget(current_data_label)

        self.block1_data_label = QLabel("-")
        self.block2_data_label = QLabel("-")
        self.block3_data_label = QLabel("-")
        self.tolerance_data_label = QLabel("-")

        self.middle_layout.addWidget(self.block1_data_label)
        self.middle_layout.addWidget(self.block2_data_label)
        self.middle_layout.addWidget(self.block3_data_label)
        self.middle_layout.addWidget(self.tolerance_data_label)

        # Right section: Input fields for modification
        self.right_layout = QVBoxLayout()

        # Label for "Your Modification"
        modification_label = QLabel("Your Modification")
        modification_label.setAlignment(Qt.AlignCenter)
        modification_label.setStyleSheet("font-weight: bold;")
        self.right_layout.addWidget(modification_label)

        self.block1_input = QLineEdit()
        self.block2_input = QLineEdit()
        self.block3_input = QLineEdit()
        self.tolerance_input = QLineEdit()

        self.right_layout.addWidget(self.block1_input)
        self.right_layout.addWidget(self.block2_input)
        self.right_layout.addWidget(self.block3_input)
        self.right_layout.addWidget(self.tolerance_input)

        # Add left, middle, right layouts to the center section
        center_layout.addLayout(self.left_layout)
        center_layout.addLayout(self.middle_layout)
        center_layout.addLayout(self.right_layout)

        # Bottom section: Delete and Submit Button in the same row
        button_row_layout = QHBoxLayout()

        self.delete_button = QPushButton("Delete Tool Type")
        self.delete_button.clicked.connect(self.delete_tool_type)
        self.delete_button.setStyleSheet("color: red; font-weight: bold;")

        self.submit_button = QPushButton("Submit Change")
        self.submit_button.clicked.connect(self.submit_change)

        button_row_layout.addWidget(self.delete_button)
        button_row_layout.addWidget(self.submit_button)

        layout.addLayout(center_layout)
        layout.addLayout(button_row_layout)

        # Back to dashboard
        self.button_layout = QHBoxLayout()
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)
        layout.addLayout(self.button_layout)

        # Set the main layout for the window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event):
        # Check if the pressed key is "Enter"
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.submit_change()

    def populate_tool_type_dropdown(self):
        # Clear the existing items from the dropdown
        self.tool_type_dropdown.clear()
        
        # Add the placeholder option again
        self.tool_type_dropdown.addItem("Select Tool Type")  
        
        # Populate the dropdown with tool type names from the database
        db = next(get_db())
        tool_types = db.query(ToolType).all()
        for tool_type in tool_types:
            self.tool_type_dropdown.addItem(tool_type.tool_name)

    def load_tool_data(self):
        tool_name = self.tool_type_dropdown.currentText()
        if tool_name == "Select Tool Type" or not tool_name:
            return

        db = next(get_db())
        tool = db.query(ToolType).filter(ToolType.tool_name == tool_name).first()

        if tool:
            # Populate the middle section with data from the database
            self.block1_data_label.setText(str(tool.block_1) if tool.block_1 is not None else "-")
            self.block2_data_label.setText(str(tool.block_2) if tool.block_2 is not None else "-")
            self.block3_data_label.setText(str(tool.block_3) if tool.block_3 is not None else "-")
            self.tolerance_data_label.setText(str(tool.tolerance) if tool.tolerance is not None else "-")

            # Populate the right section with input fields for modification
            self.block1_input.setText(str(tool.block_1) if tool.block_1 is not None else "")
            self.block2_input.setText(str(tool.block_2) if tool.block_2 is not None else "")
            self.block3_input.setText(str(tool.block_3) if tool.block_3 is not None else "")
            self.tolerance_input.setText(str(tool.tolerance) if tool.tolerance is not None else "")
        else:
            QMessageBox.warning(self, "Error", "Tool type not found.")


    def submit_change(self):
        tool_name = self.tool_type_dropdown.currentText()
        if tool_name == "Select Tool Type" or not tool_name:
            QMessageBox.warning(self, "Error", "No tool type selected.")
            return

        db = next(get_db())
        tool = db.query(ToolType).filter(ToolType.tool_name == tool_name).first()

        if tool:
            try:
                # Get and process input data
                new_block1 = self.block1_input.text().strip()
                new_block2 = self.block2_input.text().strip()
                new_block3 = self.block3_input.text().strip()
                new_tolerance = self.tolerance_input.text().strip()

                # Required fields
                if not new_block1 or not new_tolerance:
                    QMessageBox.warning(self, "Error", "Block 1 and Tolerance are required.")
                    return

                tool.block_1 = float(new_block1)
                tool.block_2 = float(new_block2) if new_block2 else None
                tool.block_3 = float(new_block3) if new_block3 else None
                tool.tolerance = float(new_tolerance)

                db.commit()
                QMessageBox.information(self, "Success", "Tool information updated successfully!")
                self.load_tool_data()  # Refresh the displayed data

            except ValueError:
                QMessageBox.warning(self, "Error", "Block values and Tolerance must be valid numbers.")
            except Exception as e:
                db.rollback()
                QMessageBox.critical(self, "Error", f"Failed to update tool: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Tool type not found.")

    def delete_tool_type(self):
        tool_name = self.tool_type_dropdown.currentText()
        if tool_name == "Select Tool Type" or not tool_name:
            QMessageBox.warning(self, "Error", "No tool type selected.")
            return

        # Confirm deletion action
        reply = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the tool type '{tool_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            db = next(get_db())
            tool = db.query(ToolType).filter(ToolType.tool_name == tool_name).first()

            if tool:
                db.delete(tool)
                db.commit()
                QMessageBox.information(self, "Success", f"Tool type '{tool_name}' deleted successfully!")
                self.clear_tool_data()  # Clear the current tool data
                self.populate_tool_type_dropdown()  # Refresh the dropdown
            else:
                QMessageBox.warning(self, "Error", "Tool type not found.")

    def clear_tool_data(self):
        # Clear all data fields after deletion
        self.block1_data_label.setText("-")
        self.block2_data_label.setText("-")
        self.block3_data_label.setText("-")
        self.tolerance_data_label.setText("-")
        self.block1_input.clear()
        self.block2_input.clear()
        self.block3_input.clear()
        self.tolerance_input.clear()

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()
