from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from pages.tool_management import ToolManagementPage
'''from pages.validation import ValidationRecordsPage
from pages.view_records import ViewRecordsPage'''

class DashboardPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QC Calibration")

        self.setFixedSize(1000, 600)
        
        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # Welcome message
        self.welcome_label = QLabel("QC Calibration Dashboard")
        self.welcome_label.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.welcome_label)

        # Navigation buttons layout
        self.button_layout = QVBoxLayout()

        # Tool Management Button
        self.tool_management_button = QPushButton("Tool Management")
        self.tool_management_button.clicked.connect(self.open_tool_management)
        self.button_layout.addWidget(self.tool_management_button)

        # Validation Records Button
        self.validation_records_button = QPushButton("Daily Validation")
        self.validation_records_button.clicked.connect(self.open_validation_records)
        self.button_layout.addWidget(self.validation_records_button)

        # View Records Button
        self.view_records_button = QPushButton("View Records")
        self.view_records_button.clicked.connect(self.open_view_records)
        self.button_layout.addWidget(self.view_records_button)

        self.layout.addLayout(self.button_layout)

        # Add logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def open_tool_management(self):
        self.tool_management_page = ToolManagementPage()
        if self.isFullScreen():
            self.tool_management_page.showFullScreen()
        else:
            self.tool_management_page.show()
        self.close()
        
    def open_validation_records(self):
        '''self.validation_records_page = ValidationRecordsPage()
        if self.isFullScreen():
            self.validation_records_page.showFullScreen()
        else:
            self.validation_records_page.show()
        self.close()'''

    def open_view_records(self):
        '''self.view_records_page = ViewRecordsPage()
        if self.isFullScreen():
            self.view_records_page.showFullScreen()
        else:
            self.view_records_page.show()
        self.close()'''

    def logout(self):
        from pages.login import LoginPage
        self.login_page = LoginPage()
        if self.isFullScreen():
            self.login_page.showFullScreen()
        else:
            self.login_page.show()
        self.close()
