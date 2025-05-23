from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QMenu, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt


class ToolManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QC Calibration")
        self.setFixedSize(1000, 600)

        # Create the outer layout that holds everything
        self.outer_layout = QVBoxLayout()
        self.outer_layout.setContentsMargins(100, 100, 100, 100)

        # Create a spacer to push everything to the center
        #self.top_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #self.outer_layout.addItem(self.top_spacer)

        # Centering the title and buttons together in a vertical layout
        self.center_layout = QVBoxLayout()
        self.center_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title = QLabel("Tool Management")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.center_layout.addWidget(self.title)

        # Button Layout
        self.button_layout = QVBoxLayout()

        # Dropdown: Tool Type Management
        self.tool_type_menu = QMenu()
        self.tool_type_menu.addAction("Add New Tool Type", self.open_add_tool_type)
        self.tool_type_menu.addAction("Update Tool Type", self.open_update_tool_type)

        self.tool_type_button = QPushButton("Manage Tool Type")
        self.tool_type_button.setMenu(self.tool_type_menu)
        self.button_layout.addWidget(self.tool_type_button)

        # Dropdown: Tool Registration
        self.tool_registration_menu = QMenu()
        self.tool_registration_menu.addAction("Register New Tool", self.open_register_tool)
        self.tool_registration_menu.addAction("Update Tool", self.open_update_tool)
        self.tool_registration_menu.addAction("Mass Calibration", self.open_mass_calibration)

        self.tool_registration_button = QPushButton("Manage Tool")
        self.tool_registration_button.setMenu(self.tool_registration_menu)
        self.button_layout.addWidget(self.tool_registration_button)

        # Back to dashboard
        self.dashboard_button = QPushButton("Back to Dashboard")
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.button_layout.addWidget(self.dashboard_button)

        # Add the button layout to the center layout
        self.center_layout.addLayout(self.button_layout)

        # Add a bottom spacer to center the layout vertically
        #self.bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #self.center_layout.addItem(self.bottom_spacer)

        # Add the center layout to the outer layout
        self.outer_layout.addLayout(self.center_layout)

        # Set the container and central widget
        container = QWidget()
        container.setLayout(self.outer_layout)
        self.setCentralWidget(container)

    # Tool Type Pages
    def open_add_tool_type(self):
        from pages.tool_type_add import AddToolTypePage
        self.page = AddToolTypePage()
        self.page.show()
        self.close()

    def open_update_tool_type(self):
        from pages.tool_type_update import UpdateToolTypePage
        self.page = UpdateToolTypePage()
        self.page.show()
        self.close()

    # Tool Registration Pages
    def open_register_tool(self):
        from pages.tool_register import RegisterToolPage
        self.page = RegisterToolPage()
        self.page.show()
        self.close()

    def open_update_tool(self):
        from pages.tool_update import UpdateToolPage
        self.page = UpdateToolPage()
        self.page.show()
        self.close()

    def open_dashboard(self):
        from pages.dashboard import DashboardPage
        self.page = DashboardPage()
        self.page.show()
        self.close()

    def open_mass_calibration(self):
        from pages.mass_calibration import MassCalibrationPage
        self.page = MassCalibrationPage()
        self.page.show()
        self.close()
