from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
from calendar import monthcalendar
from ..controllers.project_controller import ProjectController
from typing import List

class CalendarView(QWidget):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller
        self.current_date = datetime.now()
        self.selected_date = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Calendar navigation
        nav_layout = QHBoxLayout()
        
        prev_month_btn = QPushButton("◀")
        prev_month_btn.clicked.connect(self.previous_month)
        nav_layout.addWidget(prev_month_btn)
        
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.month_label)
        
        next_month_btn = QPushButton("▶")
        next_month_btn.clicked.connect(self.next_month)
        nav_layout.addWidget(next_month_btn)
        
        layout.addLayout(nav_layout)
        
        # Calendar grid
        self.calendar_grid = QGridLayout()
        layout.addLayout(self.calendar_grid)
        
        # Task list for selected date
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        self.update_calendar()
        
    def update_view(self):
        """Update the calendar view with current project data."""
        self.update_calendar()
        
    def update_calendar(self):
        """Redraw the calendar grid."""
        # Clear existing calendar
        for i in reversed(range(self.calendar_grid.count())): 
            self.calendar_grid.itemAt(i).widget().setParent(None)
            
        # Update month label
        self.month_label.setText(self.current_date.strftime("%B %Y"))
        
        # Add day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            self.calendar_grid.addWidget(label, 0, i)
            
        # Get calendar data
        cal = monthcalendar(self.current_date.year, self.current_date.month)
        
        # Add calendar cells
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    cell = CalendarCell(day, self.current_date.replace(day=day))
                    cell.clicked.connect(self.date_selected)
                    
                    # Highlight current date
                    if (day == datetime.now().day and 
                        self.current_date.month == datetime.now().month and
                        self.current_date.year == datetime.now().year):
                        cell.setStyleSheet("background-color: #e6f3ff;")
                        
                    # Add tasks for this date
                    tasks = self.get_tasks_for_date(cell.date)
                    cell.set_tasks(tasks)
                    
                    self.calendar_grid.addWidget(cell, week_num + 1, day_num)
                else:
                    # Empty cell for days not in this month
                    label = QLabel("")
                    self.calendar_grid.addWidget(label, week_num + 1, day_num)
                    
    def get_tasks_for_date(self, date: datetime) -> List['Task']:
        """Get all tasks active on the given date."""
        tasks = []
        for task in self.controller.project.tasks:
            if task.start_date <= date <= task.get_end_date():
                tasks.append(task)
        return tasks
        
    def date_selected(self, date: datetime):
        """Handle date selection."""
        self.selected_date = date
        self.update_task_list()
        
    def update_task_list(self):
        """Update the task list for the selected date."""
        self.task_list.clear()
        
        if self.selected_date:
            tasks = self.get_tasks_for_date(self.selected_date)
            for task in tasks:
                item = QListWidgetItem(f"{task.name} ({task.completion_percentage}%)")
                item.setData(Qt.UserRole, task)
                self.task_list.addItem(item)
                
    def previous_month(self):
        """Go to previous month."""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
        
    def next_month(self):
        """Go to next month."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()

class CalendarCell(QPushButton):
    clicked = pyqtSignal(datetime)
    
    def __init__(self, day: int, date: datetime):
        super().__init__()
        self.day = day
        self.date = date
        self.tasks = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the calendar cell UI."""
        self.setMinimumSize(100, 80)
        self.setText(str(self.day))
        self.clicked.connect(lambda: self.clicked.emit(self.date))
        
    def set_tasks(self, tasks: List['Task']):
        """Set tasks for this date and update display."""
        self.tasks = tasks
        if tasks:
            self.setStyleSheet("QPushButton { text-align: left; padding: 5px; }")
            text = f"{self.day}\n"
            for task in tasks[:3]:  # Show max 3 tasks
                text += f"• {task.name}\n"
            if len(tasks) > 3:
                text += f"... (+{len(tasks) - 3} more)"
            self.setText(text)
