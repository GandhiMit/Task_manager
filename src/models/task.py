from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .resource import Resource

class Task:
    _id_counter = 1
    
    def __init__(self, name: str, duration: int, start_date: Optional[datetime] = None):
        self.id = Task._id_counter
        Task._id_counter += 1
        
        self.name = name
        self.duration = duration
        self.start_date = start_date
        self.completion_percentage = 0
        self.priority = 0
        self.notes = ""
        
        # Dependencies
        self.predecessors: List[Task] = []
        self.successors: List[Task] = []
        
        # Resource assignments
        self.assignments: List[Dict] = []
        
        # Critical path calculation fields
        self.early_start = 0
        self.early_finish = 0
        self.late_start = 0
        self.late_finish = 0
        
    def add_predecessor(self, task: 'Task') -> None:
        """Add a predecessor task."""
        if task not in self.predecessors:
            self.predecessors.append(task)
            task.successors.append(self)
            
    def remove_predecessor(self, task: 'Task') -> None:
        """Remove a predecessor task."""
        if task in self.predecessors:
            self.predecessors.remove(task)
            task.successors.remove(self)
            
    def get_end_date(self) -> datetime:
        """Calculate the end date based on start date and duration."""
        if not self.start_date:
            return None
        return self.start_date + timedelta(days=self.duration)
    
    def assign_resource(self, resource: Resource, units: float, start_date: datetime, end_date: datetime) -> None:
        """Assign a resource to this task."""
        assignment = {
            'resource': resource,
            'units': units,
            'start_date': start_date,
            'end_date': end_date,
            'hours': self.calculate_assignment_hours(units, start_date, end_date)
        }
        self.assignments.append(assignment)
        resource.add_assignment(assignment)
        
    def remove_resource(self, resource: Resource) -> None:
        """Remove a resource assignment from this task."""
        assignments_to_remove = [a for a in self.assignments if a['resource'] == resource]
        for assignment in assignments_to_remove:
            self.assignments.remove(assignment)
            resource.remove_assignment(assignment)
            
    def calculate_assignment_hours(self, units: float, start_date: datetime, end_date: datetime) -> float:
        """Calculate the total hours for a resource assignment."""
        working_days = self.get_working_days(start_date, end_date)
        return working_days * 8 * units  # Assuming 8-hour workdays
        
    def get_working_days(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate the number of working days between two dates."""
        days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                days += 1
            current_date += timedelta(days=1)
        return days
    
    def get_cost(self) -> float:
        """Calculate the total cost of this task based on resource assignments."""
        return sum(a['resource'].cost_rate * a['hours'] for a in self.assignments)
    
    def update_progress(self, completion_percentage: float) -> None:
        """Update the task's completion percentage."""
        self.completion_percentage = min(100, max(0, completion_percentage))
        
    def get_float(self) -> int:
        """Calculate the task's float (slack time)."""
        return self.late_start - self.early_start
    
    def is_critical(self) -> bool:
        """Check if this task is on the critical path."""
        return self.get_float() == 0
