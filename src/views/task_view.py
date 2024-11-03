from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from typing import List, Optional
from ..controllers.project_controller import ProjectController
from ..models.task import Task


class TaskView(QWidget):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller
        self.current_task = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self._add_task)
        toolbar.addWidget(add_btn)

        edit_btn = QPushButton("Edit Task")
        edit_btn.clicked.connect(self._edit_task)
        toolbar.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Task")
        delete_btn.clicked.connect(self._delete_task)
        toolbar.addWidget(delete_btn)

        link_btn = QPushButton("Link Tasks")
        link_btn.clicked.connect(self._link_tasks)
        toolbar.addWidget(link_btn)

        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Splitter for task table and details
        splitter = QSplitter(Qt.Vertical)

        # Task table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(7)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "Name", "Start Date", "Duration", "Complete", "Resources", "Predecessors"
        ])
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.task_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.task_table.itemSelectionChanged.connect(self._task_selected)
        splitter.addWidget(self.task_table)

        # Task details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # Progress tracking
        progress_group = QGroupBox("Progress")
        progress_layout = QHBoxLayout(progress_group)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.valueChanged.connect(self._update_progress)
        progress_layout.addWidget(self.progress_slider)

        self.progress_label = QLabel("0%")
        progress_layout.addWidget(self.progress_label)

        details_layout.addWidget(progress_group)

        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.textChanged.connect(self._update_notes)
        notes_layout.addWidget(self.notes_edit)
        details_layout.addWidget(notes_group)

        splitter.addWidget(details_widget)

        layout.addWidget(splitter)

    def update_view(self):
        """Update the task view with current project data."""
        self.task_table.setRowCount(0)

        for task in self.controller.project.tasks:
            row = self.task_table.rowCount()
            self.task_table.insertRow(row)

            # Basic task info
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.name))
            self.task_table.setItem(row, 2, QTableWidgetItem(task.start_date.strftime("%Y-%m-%d")))
            self.task_table.setItem(row, 3, QTableWidgetItem(f"{task.duration} days"))

            # Completion percentage
            progress_item = QTableWidgetItem(f"{task.completion_percentage}%")
            if task.completion_percentage == 100:
                progress_item.setBackground(QColor(200, 255, 200))  # Light green for completed tasks
            self.task_table.setItem(row, 4, progress_item)

            # Resources
            resources = [a['resource'].name for a in task.assignments]
            self.task_table.setItem(row, 5, QTableWidgetItem(", ".join(resources)))

            # Predecessors
            predecessors = [str(t.id) for t in task.predecessors]
            self.task_table.setItem(row, 6, QTableWidgetItem(", ".join(predecessors)))

        self.task_table.resizeColumnsToContents()

    def _add_task(self):
        """Show dialog to add a new task."""
        dialog = TaskDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            task = self.controller.create_task(
                name=dialog.name_edit.text(),
                duration=int(dialog.duration_edit.text()),
                start_date=dialog.start_date.date().toPyDate()
            )
            self.update_view()

    def _edit_task(self):
        """Show dialog to edit selected task."""
        task = self._get_selected_task()
        if task:
            dialog = TaskDialog(self.controller, self, task)
            if dialog.exec_() == QDialog.Accepted:
                task.name = dialog.name_edit.text()
                task.duration = int(dialog.duration_edit.text())
                task.start_date = dialog.start_date.date().toPyDate()
                self.update_view()

    def _delete_task(self):
        """Delete selected task."""
        task = self._get_selected_task()
        if task:
            reply = QMessageBox.question(
                self,
                "Delete Task",
                f"Are you sure you want to delete task '{task.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.controller.delete_task(task)
                self.update_view()

    def _link_tasks(self):
        """Show dialog to link tasks."""
        dialog = LinkTasksDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_view()

    def _task_selected(self):
        """Update details when a task is selected."""
        task = self._get_selected_task()
        if task:
            self.current_task = task
            self.progress_slider.setValue(int(task.completion_percentage))
            self.progress_label.setText(f"{task.completion_percentage}%")
            self.notes_edit.setText(task.notes)
        else:
            self.current_task = None
            self.progress_slider.setValue(0)
            self.progress_label.setText("0%")
            self.notes_edit.clear()

    def _get_selected_task(self) -> Optional[Task]:
        """Get the currently selected task."""
        current_row = self.task_table.currentRow()
        if current_row >= 0:
            task_id = int(self.task_table.item(current_row, 0).text())
            return self.controller.project.find_task_by_id(task_id)
        return None

    def _update_progress(self):
        """Update the progress of the selected task."""
        if self.current_task:
            progress = self.progress_slider.value()
            self.current_task.completion_percentage = progress
            self.progress_label.setText(f"{progress}%")
            self.update_view()

    def _update_notes(self):
        """Update the notes of the selected task."""
        if self.current_task:
            self.current_task.notes = self.notes_edit.toPlainText()

    def add_task(self):
        """Public method for adding a task."""
        self._add_task()

    def link_tasks(self):
        """Public method for linking tasks."""
        self._link_tasks()


class TaskDialog(QDialog):
    def __init__(self, controller: ProjectController, parent=None, task: Optional[Task] = None):
        super().__init__(parent)
        self.controller = controller
        self.task = task
        self.init_ui()

    def init_ui(self):
        """Initialize the task dialog UI."""
        self.setWindowTitle("Task Details")
        layout = QFormLayout(self)

        # Name field
        self.name_edit = QLineEdit()
        if self.task:
            self.name_edit.setText(self.task.name)
        layout.addRow("Name:", self.name_edit)

        # Duration field
        self.duration_edit = QLineEdit()
        if self.task:
            self.duration_edit.setText(str(self.task.duration))
        layout.addRow("Duration (days):", self.duration_edit)

        # Start date field
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        if self.task:
            self.start_date.setDate(self.task.start_date)
        else:
            self.start_date.setDate(QDate.currentDate())
        layout.addRow("Start Date:", self.start_date)

        # Resources
        self.resources_group = QGroupBox("Resources")
        resources_layout = QVBoxLayout(self.resources_group)

        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(3)
        self.resources_table.setHorizontalHeaderLabels(["Resource", "Units", "Remove"])
        self._update_resources_table()
        resources_layout.addWidget(self.resources_table)

        add_resource_btn = QPushButton("Add Resource")
        add_resource_btn.clicked.connect(self._add_resource)
        resources_layout.addWidget(add_resource_btn)

        layout.addRow(self.resources_group)

        # Predecessors
        self.predecessors_group = QGroupBox("Predecessors")
        predecessors_layout = QVBoxLayout(self.predecessors_group)

        self.predecessors_list = QListWidget()
        self._update_predecessors_list()
        predecessors_layout.addWidget(self.predecessors_list)

        add_predecessor_btn = QPushButton("Add Predecessor")
        add_predecessor_btn.clicked.connect(self._add_predecessor)
        predecessors_layout.addWidget(add_predecessor_btn)

        layout.addRow(self.predecessors_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _update_resources_table(self):
        """Update the resources table."""
        self.resources_table.setRowCount(0)

        if self.task:
            for assignment in self.task.assignments:
                row = self.resources_table.rowCount()
                self.resources_table.insertRow(row)

                self.resources_table.setItem(row, 0, QTableWidgetItem(assignment['resource'].name))
                self.resources_table.setItem(row, 1, QTableWidgetItem(f"{assignment['units'] * 100}%"))

                remove_btn = QPushButton("Remove")
                remove_btn.clicked.connect(lambda _, r=row: self._remove_resource(r))
                self.resources_table.setCellWidget(row, 2, remove_btn)

    def _update_predecessors_list(self):
        """Update the predecessors list."""
        self.predecessors_list.clear()

        if self.task:
            for pred in self.task.predecessors:
                item = QListWidgetItem(f"{pred.id}: {pred.name}")
                item.setData(Qt.UserRole, pred)
                self.predecessors_list.addItem(item)

    def _add_resource(self):
        """Show dialog to add a resource assignment."""
        dialog = ResourceAssignmentDialog(self.controller, self)
        if dialog.exec_() == QDialog.Accepted and self.task:
            resource = dialog.resource_combo.currentData()
            units = float(dialog.units_edit.text()) / 100
            self.task.assign_resource(
                resource,
                units,
                self.task.start_date,
                self.task.get_end_date()
            )
            self._update_resources_table()

    def _remove_resource(self, row: int):
        """Remove a resource assignment."""
        if self.task:
            resource_name = self.resources_table.item(row, 0).text()
            resource = next((r for r in self.controller.project.resources if r.name == resource_name), None)
            if resource:
                self.task.remove_resource(resource)
                self._update_resources_table()

    def _add_predecessor(self):
        """Show dialog to add a predecessor task."""
        dialog = PredecessorDialog(self.controller, self.task, self)
        if dialog.exec_() == QDialog.Accepted:
            pred_task = dialog.task_combo.currentData()
            if pred_task:
                self.task.add_predecessor(pred_task)
                self._update_predecessors_list()

    def validate(self):
        """Validate input before accepting."""
        try:
            duration = int(self.duration_edit.text())

            if not self.name_edit.text():
                raise ValueError("Name is required")
            if duration <= 0:
                raise ValueError("Duration must be positive")

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))


class ResourceAssignmentDialog(QDialog):
    def __init__(self, controller: ProjectController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize the resource assignment dialog UI."""
        self.setWindowTitle("Assign Resource")
        layout = QFormLayout(self)

        # Resource selection
        self.resource_combo = QComboBox()
        for resource in self.controller.project.resources:
            self.resource_combo.addItem(resource.name, resource)
        layout.addRow("Resource:", self.resource_combo)

        # Units field
        self.units_edit = QLineEdit("100")
        layout.addRow("Units (%):", self.units_edit)

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
            units = float(self.units_edit.text())
            if not 0 < units <= 100:
                raise ValueError("Units must be between 0 and 100")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))


class PredecessorDialog(QDialog):
    def __init__(self, controller: ProjectController, current_task: Task, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_task = current_task
        self.init_ui()

    def init_ui(self):
        """Initialize the predecessor dialog UI."""
        self.setWindowTitle("Add Predecessor")
        layout = QFormLayout(self)

        # Task selection
        self.task_combo = QComboBox()
        for task in self.controller.project.tasks:
            # Only show tasks that aren't already predecessors and aren't the current task
            if task != self.current_task and task not in self.current_task.predecessors:
                self.task_combo.addItem(f"{task.id}: {task.name}", task)
        layout.addRow("Predecessor Task:", self.task_combo)

        # Dependency type (could be extended in future)
        self.dependency_type = QComboBox()
        self.dependency_type.addItems(["Finish to Start", "Start to Start", "Finish to Finish", "Start to Finish"])
        layout.addRow("Dependency Type:", self.dependency_type)

        # Lag time
        self.lag_spinbox = QSpinBox()
        self.lag_spinbox.setRange(-999, 999)
        self.lag_spinbox.setValue(0)
        self.lag_spinbox.setSuffix(" days")
        layout.addRow("Lag Time:", self.lag_spinbox)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate(self):
        """Validate input before accepting."""
        if self.task_combo.currentData() is None:
            QMessageBox.warning(self, "Invalid Selection", "Please select a predecessor task")
            return

        # Check for circular dependencies
        if self._would_create_circular_dependency():
            QMessageBox.warning(self, "Invalid Dependency",
                                "This would create a circular dependency")
            return

        self.accept()

    def _would_create_circular_dependency(self) -> bool:
        """Check if adding this predecessor would create a circular dependency."""
        pred_task = self.task_combo.currentData()
        visited = set()

        def has_cycle(task):
            if task in visited:
                return True
            visited.add(task)
            for predecessor in task.predecessors:
                if has_cycle(predecessor):
                    return True
            visited.remove(task)
            return False

        # Temporarily add the new dependency
        self.current_task.predecessors.append(pred_task)
        has_circular = has_cycle(pred_task)
        # Remove the temporary dependency
        self.current_task.predecessors.remove(pred_task)

        return has_circular


class LinkTasksDialog(QDialog):
    def __init__(self, controller: ProjectController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        """Initialize the link tasks dialog UI."""
        self.setWindowTitle("Link Tasks")
        layout = QFormLayout(self)

        # Predecessor task selection
        self.pred_combo = QComboBox()
        for task in self.controller.project.tasks:
            self.pred_combo.addItem(f"{task.id}: {task.name}", task)
        layout.addRow("Predecessor:", self.pred_combo)

        # Successor task selection
        self.succ_combo = QComboBox()
        for task in self.controller.project.tasks:
            self.succ_combo.addItem(f"{task.id}: {task.name}", task)
        layout.addRow("Successor:", self.succ_combo)

        # Dependency type
        self.dependency_type = QComboBox()
        self.dependency_type.addItems(["Finish to Start", "Start to Start", "Finish to Finish", "Start to Finish"])
        layout.addRow("Dependency Type:", self.dependency_type)

        # Lag time
        self.lag_spinbox = QSpinBox()
        self.lag_spinbox.setRange(-999, 999)
        self.lag_spinbox.setValue(0)
        self.lag_spinbox.setSuffix(" days")
        layout.addRow("Lag Time:", self.lag_spinbox)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Connect selection changed signals
        self.pred_combo.currentIndexChanged.connect(self._update_successor_combo)
        self.succ_combo.currentIndexChanged.connect(self._update_predecessor_combo)

    def _update_successor_combo(self):
        """Update successor combo box based on predecessor selection."""
        pred_task = self.pred_combo.currentData()
        current_succ = self.succ_combo.currentData()

        self.succ_combo.clear()
        for task in self.controller.project.tasks:
            if task != pred_task and not self._would_create_circular_dependency(pred_task, task):
                self.succ_combo.addItem(f"{task.id}: {task.name}", task)

        # Restore previous selection if valid
        if current_succ:
            index = self.succ_combo.findData(current_succ)
            if index >= 0:
                self.succ_combo.setCurrentIndex(index)

    def _update_predecessor_combo(self):
        """Update predecessor combo box based on successor selection."""
        succ_task = self.succ_combo.currentData()
        current_pred = self.pred_combo.currentData()

        self.pred_combo.clear()
        for task in self.controller.project.tasks:
            if task != succ_task and not self._would_create_circular_dependency(task, succ_task):
                self.pred_combo.addItem(f"{task.id}: {task.name}", task)

        # Restore previous selection if valid
        if current_pred:
            index = self.pred_combo.findData(current_pred)
            if index >= 0:
                self.pred_combo.setCurrentIndex(index)

    def validate(self):
        """Validate input before accepting."""
        pred_task = self.pred_combo.currentData()
        succ_task = self.succ_combo.currentData()

        if pred_task is None or succ_task is None:
            QMessageBox.warning(self, "Invalid Selection", "Please select both tasks")
            return

        if pred_task == succ_task:
            QMessageBox.warning(self, "Invalid Selection", "Cannot link a task to itself")
            return

        if self._would_create_circular_dependency(pred_task, succ_task):
            QMessageBox.warning(self, "Invalid Dependency",
                                "This would create a circular dependency")
            return

        self.accept()

    def _would_create_circular_dependency(self, pred_task: Task, succ_task: Task) -> bool:
        """Check if adding this dependency would create a circular dependency."""
        # Temporarily add the new dependency
        succ_task.predecessors.append(pred_task)

        # Check for cycles
        visited = set()
        cycle_found = False

        def check_cycle(task):
            nonlocal cycle_found
            if task in visited:
                cycle_found = True
                return
            visited.add(task)
            for predecessor in task.predecessors:
                check_cycle(predecessor)
            visited.remove(task)

        check_cycle(pred_task)

        # Remove the temporary dependency
        succ_task.predecessors.remove(pred_task)

        return cycle_found