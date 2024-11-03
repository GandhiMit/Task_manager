import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
from ..controllers.project_controller import ProjectController
from typing import List, Optional

class GanttView(QWidget):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller
        self.zoom_level = 1.0
        self.scroll_position = 0
        self.selected_task = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create splitter for task list and chart
        splitter = QSplitter(Qt.Horizontal)
        
        # Task list
        self.task_list = QTreeWidget()
        self.task_list.setHeaderLabels(["Task", "Start", "Duration", "Complete"])
        self.task_list.itemClicked.connect(self.task_selected)
        splitter.addWidget(self.task_list)
        
        # Gantt chart area
        self.chart_area = QScrollArea()
        self.chart_widget = GanttChartWidget(self.controller)
        self.chart_area.setWidget(self.chart_widget)
        self.chart_area.setWidgetResizable(True)
        splitter.addWidget(self.chart_area)
        
        layout.addWidget(splitter)
        
        # Timeline controls
        timeline_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        timeline_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.clicked.connect(self.zoom_out)
        timeline_layout.addWidget(zoom_out_btn)
        
        timeline_layout.addStretch()
        
        self.date_label = QLabel()
        self.update_date_label()
        timeline_layout.addWidget(self.date_label)
        
        layout.addLayout(timeline_layout)
        
    def update_view(self):
        """Update the Gantt chart view with current project data."""
        self.task_list.clear()
        
        for task in self.controller.project.tasks:
            item = QTreeWidgetItem(self.task_list)
            item.setText(0, task.name)
            item.setText(1, task.start_date.strftime("%Y-%m-%d"))
            item.setText(2, str(task.duration))
            item.setText(3, f"{task.completion_percentage}%")
            item.setData(0, Qt.UserRole, task)
            
        self.chart_widget.update_chart()
        self.update_date_label()
        
    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_level = min(2.0, self.zoom_level * 1.2)
        self.chart_widget.set_zoom(self.zoom_level)
        
    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_level = max(0.5, self.zoom_level / 1.2)
        self.chart_widget.set_zoom(self.zoom_level)
        
    def reset_zoom(self):
        """Reset zoom to default level."""
        self.zoom_level = 1.0
        self.chart_widget.set_zoom(self.zoom_level)
        
    def task_selected(self, item):
        """Handle task selection."""
        task = item.data(0, Qt.UserRole)
        self.selected_task = task
        self.chart_widget.highlight_task(task)
        
    def highlight_critical_path(self, critical_path):
        """Highlight tasks on the critical path."""
        self.chart_widget.highlight_critical_path(critical_path)
        
    def update_date_label(self):
        """Update the date range label."""
        if self.controller.project.tasks:
            start = min(task.start_date for task in self.controller.project.tasks)
            end = max(task.get_end_date() for task in self.controller.project.tasks)
            self.date_label.setText(f"{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}")
        else:
            self.date_label.setText("")

class GanttChartWidget(QWidget):
    def __init__(self, controller: ProjectController):
        super().__init__()
        self.controller = controller
        self.zoom_level = 1.0
        self.day_width = 20  # pixels per day
        self.row_height = 30
        self.highlighted_task = None
        self.critical_path = []
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        """Draw the Gantt chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate date range
        if not self.controller.project.tasks:
            return
            
        start_date = min(task.start_date for task in self.controller.project.tasks)
        end_date = max(task.get_end_date() for task in self.controller.project.tasks)
        total_days = (end_date - start_date).days + 1
        
        # Draw timeline
        self.draw_timeline(painter, start_date, total_days)
        
        # Draw tasks
        y = self.row_height
        for task in self.controller.project.tasks:
            self.draw_task(painter, task, start_date, y)
            y += self.row_height
            
        # Draw dependencies
        for task in self.controller.project.tasks:
            self.draw_dependencies(painter, task, start_date)
            
    def draw_timeline(self, painter: QPainter, start_date: datetime, total_days: int):
        """Draw the timeline at the top of the chart."""
        painter.setPen(Qt.black)
        
        # Draw month labels
        current_date = start_date
        for day in range(total_days):
            x = day * self.day_width * self.zoom_level
            
            # Draw day line
            painter.drawLine(
                QPoint(x, self.row_height),
                QPoint(x, self.height())
            )
            
            # Draw month label on the first day of each month
            if current_date.day == 1:
                painter.drawText(
                    QRect(x, 0, 100, self.row_height),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    current_date.strftime("%B %Y")
                )
                
            current_date += timedelta(days=1)

    def draw_task(self, painter: QPainter, task: 'Task', start_date: datetime, y: int):
        """Draw a single task bar."""
        days_from_start = (task.start_date - start_date).days
        x = days_from_start * self.day_width * self.zoom_level
        width = task.duration * self.day_width * self.zoom_level

        # Select color based on task status
        if task in self.critical_path:
            color = QColor(255, 0, 0, 180)  # Red for critical path
        elif task == self.highlighted_task:
            color = QColor(0, 255, 0, 180)  # Green for highlighted task
        else:
            color = QColor(0, 120, 215, 180)  # Blue for normal tasks

        # Draw task bar
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.black)
        task_rect = QRectF(x, y + 5, width, self.row_height - 10)
        painter.drawRect(task_rect)

        # Draw progress bar
        if task.completion_percentage > 0:
            progress_width = width * (task.completion_percentage / 100.0)
            progress_rect = QRectF(x, y + 5, progress_width, self.row_height - 10)
            painter.setBrush(QBrush(QColor(0, 200, 0, 180)))
            painter.drawRect(progress_rect)

        # Draw task name
        painter.drawText(
            QRectF(x + 5, y, width - 10, self.row_height),
            Qt.AlignLeft | Qt.AlignVCenter,
            task.name
        )

    def draw_dependencies(self, painter: QPainter, task: 'Task', start_date: datetime):
        """Draw dependency arrows between tasks."""
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        for predecessor in task.predecessors:
            # Calculate start and end points
            start_x = ((
                                   predecessor.start_date - start_date).days + predecessor.duration) * self.day_width * self.zoom_level
            start_y = self.tasks.index(predecessor) * self.row_height + self.row_height / 2

            end_x = ((task.start_date - start_date).days) * self.day_width * self.zoom_level
            end_y = self.tasks.index(task) * self.row_height + self.row_height / 2

            # Draw arrow
            self.draw_arrow(painter, QPointF(start_x, start_y), QPointF(end_x, end_y))

    def draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        """Draw an arrow between two points."""
        # Draw line
        painter.drawLine(start, end)

        # Calculate arrow head
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        arrow_size = 10

        # Draw arrow head
        arrow_p1 = QPointF(
            end.x() - arrow_size * math.cos(angle - math.pi / 6),
            end.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = QPointF(
            end.x() - arrow_size * math.cos(angle + math.pi / 6),
            end.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        painter.setBrush(Qt.black)
        painter.drawPolygon(QPolygonF([end, arrow_p1, arrow_p2]))

    def set_zoom(self, zoom_level: float):
        """Set the zoom level and redraw."""
        self.zoom_level = zoom_level
        self.update()

    def highlight_task(self, task: 'Task'):
        """Highlight a specific task."""
        self.highlighted_task = task
        self.update()

    def highlight_critical_path(self, critical_path: List['Task']):
        """Highlight tasks on the critical path."""
        self.critical_path = critical_path
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse click events."""
        if event.button() == Qt.LeftButton:
            # Find clicked task
            task = self.find_task_at_position(event.pos())
            if task:
                self.highlight_task(task)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        task = self.find_task_at_position(event.pos())
        if task:
            QToolTip.showText(
                event.globalPos(),
                f"Task: {task.name}\n"
                f"Duration: {task.duration} days\n"
                f"Complete: {task.completion_percentage}%"
            )

    def find_task_at_position(self, pos: QPoint) -> Optional['Task']:
        """Find the task at the given position."""
        if not self.controller.project.tasks:
            return None

        start_date = min(task.start_date for task in self.controller.project.tasks)

        for i, task in enumerate(self.controller.project.tasks):
            days_from_start = (task.start_date - start_date).days
            x = days_from_start * self.day_width * self.zoom_level
            y = i * self.row_height

            task_rect = QRectF(
                x,
                y + 5,
                task.duration * self.day_width * self.zoom_level,
                self.row_height - 10
            )

            if task_rect.contains(pos):
                return task

        return None