from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from .gantt_view import GanttView
from .calendar_view import CalendarView
from .resource_view import ResourceView
from .task_view import TaskView
from ..controllers.project_controller import ProjectController


class MainWindow(QMainWindow):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller

        # Initialize views as class attributes first
        self.gantt_view = None
        self.calendar_view = None
        self.resource_view = None
        self.task_view = None

        self.setWindowTitle("Project Management System")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Create views and UI
        self.create_views()
        self.create_menu_bar()
        self.create_toolbar()

        # Create status bar
        self.statusBar().showMessage("Ready")

    def create_views(self):
        """Create and initialize all views."""
        # Create tab widget
        tab_widget = QTabWidget()

        # Initialize views
        self.gantt_view = GanttView(self.controller)
        self.calendar_view = CalendarView(self.controller)
        self.resource_view = ResourceView(self.controller)
        self.task_view = TaskView(self.controller)

        # Add views to tabs
        tab_widget.addTab(self.gantt_view, "Gantt Chart")
        tab_widget.addTab(self.calendar_view, "Calendar")
        tab_widget.addTab(self.resource_view, "Resources")
        tab_widget.addTab(self.task_view, "Tasks")

        self.main_layout.addWidget(tab_widget)

    def create_menu_bar(self):
        # File menu
        file_menu = self.menuBar().addMenu("File")

        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        export_menu = file_menu.addMenu("Export")
        export_menu.addAction("Export to PDF", self.export_pdf)
        export_menu.addAction("Export to Excel", self.export_excel)

        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close, "Ctrl+Q")

        # Edit menu
        edit_menu = self.menuBar().addMenu("Edit")
        edit_menu.addAction("Undo", self.undo, "Ctrl+Z")
        edit_menu.addAction("Redo", self.redo, "Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Project Settings", self.show_project_settings)

        # View menu
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction("Zoom In", self.zoom_in, "Ctrl++")
        view_menu.addAction("Zoom Out", self.zoom_out, "Ctrl+-")
        view_menu.addAction("Reset Zoom", self.reset_zoom, "Ctrl+0")

        # Tools menu
        tools_menu = self.menuBar().addMenu("Tools")
        tools_menu.addAction("Critical Path Analysis", self.show_critical_path)
        tools_menu.addAction("Resource Leveling", self.level_resources)
        tools_menu.addAction("Cost Analysis", self.show_cost_analysis)

        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("Documentation", self.show_documentation)
        help_menu.addAction("About", self.show_about)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add task actions
        new_task_action = QAction("New Task", self)
        new_task_action.triggered.connect(lambda: self.task_view.add_task())
        toolbar.addAction(new_task_action)

        link_tasks_action = QAction("Link Tasks", self)
        link_tasks_action.triggered.connect(lambda: self.task_view.link_tasks())
        toolbar.addAction(link_tasks_action)

        # Add resource actions
        new_resource_action = QAction("Add Resource", self)
        new_resource_action.triggered.connect(lambda: self.resource_view.add_resource())
        toolbar.addAction(new_resource_action)

        # Add baseline action
        save_baseline_action = QAction("Save Baseline", self)
        save_baseline_action.triggered.connect(self.save_baseline)
        toolbar.addAction(save_baseline_action)

    # File menu actions
    def new_project(self):
        if self.maybe_save():
            self.controller.new_project()
            self.update_views()

    def open_project(self):
        if self.maybe_save():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open Project",
                "",
                "Project Files (*.proj);;All Files (*)"
            )
            if filename:
                self.controller.load_project(filename)
                self.update_views()

    def save_project(self):
        if not self.controller.current_filename:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Project",
                "",
                "Project Files (*.proj);;All Files (*)"
            )
            if filename:
                self.controller.save_project(filename)
                self.statusBar().showMessage(f"Project saved to {filename}", 3000)
        else:
            self.controller.save_project()
            self.statusBar().showMessage("Project saved", 3000)

    def export_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if filename:
            self.controller.export_pdf(filename)

    def export_excel(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        if filename:
            self.controller.export_excel(filename)

    # Edit menu actions
    def undo(self):
        self.controller.undo()
        self.update_views()

    def redo(self):
        self.controller.redo()
        self.update_views()

    def show_project_settings(self):
        dialog = ProjectSettingsDialog(self.controller.project, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_views()

    # View menu actions
    def zoom_in(self):
        self.gantt_view.zoom_in()

    def zoom_out(self):
        self.gantt_view.zoom_out()

    def reset_zoom(self):
        self.gantt_view.reset_zoom()

    # Tools menu actions
    def show_critical_path(self):
        critical_path = self.controller.calculate_critical_path()
        self.gantt_view.highlight_critical_path(critical_path)

    def level_resources(self):
        self.controller.level_resources()
        self.update_views()

    def show_cost_analysis(self):
        dialog = CostAnalysisDialog(self.controller.project, self)
        dialog.exec_()

    # Help menu actions
    def show_documentation(self):
        QDesktopServices.openUrl(QUrl("https://docs.projectmanager.com"))

    def show_about(self):
        QMessageBox.about(
            self,
            "About Project Manager",
            "Project Management System v1.0\n\n"
            "A comprehensive project management tool built with Python and PyQt5."
        )

    def save_baseline(self):
        self.controller.save_baseline()
        self.statusBar().showMessage("Baseline saved", 3000)

    def update_views(self):
        """Update all views with current project data."""
        self.gantt_view.update_view()
        self.calendar_view.update_view()
        self.resource_view.update_view()
        self.task_view.update_view()

    def maybe_save(self) -> bool:
        """Check if project needs to be saved before proceeding."""
        if self.controller.project.modified:
            reply = QMessageBox.question(
                self,
                "Save Changes",
                "The project has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                return self.save_project()
            elif reply == QMessageBox.Cancel:
                return False

        return True

    def closeEvent(self, event):
        """Handle application close event."""
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


# Additional dialog classes needed by MainWindow
class ProjectSettingsDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Settings")
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        # Project name
        self.name_edit = QLineEdit(self.project.name)
        layout.addRow("Project Name:", self.name_edit)

        # Start date
        self.start_date = QDateEdit(self.project.start_date)
        self.start_date.setCalendarPopup(True)
        layout.addRow("Start Date:", self.start_date)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class CostAnalysisDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Cost Analysis")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create table for cost breakdown
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Item", "Cost"])

        # Add total project cost
        self.add_cost_row(table, "Total Project Cost", self.project.get_total_cost())

        # Add resource costs
        for resource in self.project.resources:
            resource_cost = sum(a['hours'] * resource.cost_rate for a in resource.assignments)
            self.add_cost_row(table, f"Resource: {resource.name}", resource_cost)

        layout.addWidget(table)

        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def add_cost_row(self, table, item, cost):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(item))
        table.setItem(row, 1, QTableWidgetItem(f"${cost:.2f}"))