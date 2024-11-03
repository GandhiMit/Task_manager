from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from typing import List, Optional
from ..controllers.project_controller import ProjectController


class ResourceView(QWidget):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller
        self.current_resource = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        # Create buttons
        add_btn = QPushButton("Add Resource")
        add_btn.clicked.connect(self._add_resource)
        toolbar.addWidget(add_btn)

        edit_btn = QPushButton("Edit Resource")
        edit_btn.clicked.connect(self._edit_resource)
        toolbar.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Resource")
        delete_btn.clicked.connect(self._delete_resource)
        toolbar.addWidget(delete_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Resource table
        self.resource_table = QTableWidget()
        self.resource_table.setColumnCount(5)
        self.resource_table.setHorizontalHeaderLabels([
            "Name", "Cost Rate", "Availability", "Utilization", "Skills"
        ])
        self.resource_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resource_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resource_table.itemSelectionChanged.connect(self._resource_selected)
        layout.addWidget(self.resource_table)

        # Resource details
        details_group = QGroupBox("Resource Details")
        details_layout = QVBoxLayout(details_group)

        # Assignments table
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(4)
        self.assignments_table.setHorizontalHeaderLabels([
            "Task", "Start Date", "End Date", "Units"
        ])
        details_layout.addWidget(self.assignments_table)

        # Calendar
        self.calendar = ResourceCalendar()
        details_layout.addWidget(self.calendar)

        layout.addWidget(details_group)

    def update_view(self):
        """Update the resource view with current project data."""
        self.resource_table.setRowCount(0)

        for resource in self.controller.project.resources:
            row = self.resource_table.rowCount()
            self.resource_table.insertRow(row)

            # Basic resource info
            self.resource_table.setItem(row, 0, QTableWidgetItem(resource.name))
            self.resource_table.setItem(row, 1, QTableWidgetItem(f"${resource.cost_rate:.2f}/hr"))
            self.resource_table.setItem(row, 2, QTableWidgetItem(f"{resource.availability * 100}%"))

            # Calculate and show utilization
            utilization = resource.get_utilization(
                self.controller.project.start_date,
                max(task.get_end_date() for task in self.controller.project.tasks)
                if self.controller.project.tasks else datetime.now()
            )
            utilization_item = QTableWidgetItem(f"{utilization * 100:.1f}%")
            if utilization > 1:
                utilization_item.setBackground(QColor(255, 200, 200))  # Red background for over-allocation
            self.resource_table.setItem(row, 3, utilization_item)

            # Skills
            self.resource_table.setItem(row, 4, QTableWidgetItem(", ".join(resource.skills)))

        self.resource_table.resizeColumnsToContents()

    def _add_resource(self):
        """Show dialog to add a new resource."""
        dialog = ResourceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            resource = self.controller.create_resource(
                name=dialog.name_edit.text(),
                cost_rate=float(dialog.cost_edit.text()),
                availability=float(dialog.availability_edit.text()) / 100
            )
            for skill in dialog.skills_edit.text().split(","):
                if skill.strip():
                    resource.add_skill(skill.strip())
            self.update_view()

    def _edit_resource(self):
        """Show dialog to edit selected resource."""
        current_row = self.resource_table.currentRow()
        if current_row >= 0:
            resource = self.controller.project.resources[current_row]
            dialog = ResourceDialog(self, resource)
            if dialog.exec_() == QDialog.Accepted:
                resource.name = dialog.name_edit.text()
                resource.cost_rate = float(dialog.cost_edit.text())
                resource.availability = float(dialog.availability_edit.text()) / 100
                resource.skills = [s.strip() for s in dialog.skills_edit.text().split(",") if s.strip()]
                self.update_view()

    def _delete_resource(self):
        """Delete selected resource."""
        current_row = self.resource_table.currentRow()
        if current_row >= 0:
            resource = self.controller.project.resources[current_row]
            reply = QMessageBox.question(
                self,
                "Delete Resource",
                f"Are you sure you want to delete resource '{resource.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.controller.delete_resource(resource)
                self.update_view()

    def _resource_selected(self):
        """Update details when a resource is selected."""
        current_row = self.resource_table.currentRow()
        if current_row >= 0:
            resource = self.controller.project.resources[current_row]
            self.current_resource = resource
            self._update_assignments(resource)
            self.calendar.update_calendar(resource)

    def _update_assignments(self, resource):
        """Update the assignments table for the selected resource."""
        self.assignments_table.setRowCount(0)

        for assignment in resource.assignments:
            row = self.assignments_table.rowCount()
            self.assignments_table.insertRow(row)

            self.assignments_table.setItem(row, 0, QTableWidgetItem(assignment['task'].name))
            self.assignments_table.setItem(row, 1, QTableWidgetItem(assignment['start_date'].strftime("%Y-%m-%d")))
            self.assignments_table.setItem(row, 2, QTableWidgetItem(assignment['end_date'].strftime("%Y-%m-%d")))
            self.assignments_table.setItem(row, 3, QTableWidgetItem(f"{assignment['units'] * 100}%"))

        self.assignments_table.resizeColumnsToContents()


class ResourceDialog(QDialog):
    def __init__(self, parent=None, resource=None):
        super().__init__(parent)
        self.resource = resource
        self.init_ui()

    def init_ui(self):
        """Initialize the resource dialog UI."""
        self.setWindowTitle("Resource Details")
        layout = QFormLayout(self)

        # Name field
        self.name_edit = QLineEdit()
        if self.resource:
            self.name_edit.setText(self.resource.name)
        layout.addRow("Name:", self.name_edit)

        # Cost rate field
        self.cost_edit = QLineEdit()
        if self.resource:
            self.cost_edit.setText(str(self.resource.cost_rate))
        layout.addRow("Cost Rate ($/hr):", self.cost_edit)

        # Availability field
        self.availability_edit = QLineEdit()
        if self.resource:
            self.availability_edit.setText(str(self.resource.availability * 100))
        else:
            self.availability_edit.setText("100")
        layout.addRow("Availability (%):", self.availability_edit)

        # Skills field
        self.skills_edit = QLineEdit()
        if self.resource:
            self.skills_edit.setText(", ".join(self.resource.skills))
        layout.addRow("Skills:", self.skills_edit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate(self):
        """Validate input before accepting."""
        try:
            cost_rate = float(self.cost_edit.text())
            availability = float(self.availability_edit.text())

            if not self.name_edit.text():
                raise ValueError("Name is required")
            if cost_rate < 0:
                raise ValueError("Cost rate must be non-negative")
            if not 0 <= availability <= 100:
                raise ValueError("Availability must be between 0 and 100")

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))


class ResourceCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.resource = None
        self.setGridVisible(True)

    def update_calendar(self, resource):
        """Update the calendar with resource availability."""
        self.resource = resource
        self.updateCells()

    def paintCell(self, painter, rect, date):
        """Custom paint for calendar cells."""
        super().paintCell(painter, rect, date)

        if self.resource:
            # Get availability for this date
            availability = self.resource.get_availability(date.toPyDate())

            # Color cell based on availability
            if availability == 0:
                painter.fillRect(rect, QColor(255, 200, 200, 100))  # Light red for unavailable
            elif availability < 1:
                painter.fillRect(rect, QColor(255, 255, 200, 100))  # Light yellow for partial

            # Show assignments
            assignments = [a for a in self.resource.assignments
                           if a['start_date'] <= date.toPyDate() <= a['end_date']]
            if assignments:
                painter.drawText(
                    rect.adjusted(2, rect.height() - 15, -2, -2),
                    Qt.AlignRight | Qt.AlignBottom,
                    f"{len(assignments)}"
                )