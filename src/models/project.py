from datetime import datetime
from typing import List, Dict, Optional
from .task import Task
from .resource import Resource

class Project:
    def __init__(self, name: str, start_date: Optional[datetime] = None):
        self.name = name
        self.start_date = start_date or datetime.now()
        self.tasks: List[Task] = []
        self.resources: List[Resource] = []
        self.baseline: Dict = {}
        self.modified = False
        
    def add_task(self, task: Task) -> None:
        """Add a new task to the project."""
        self.tasks.append(task)
        self.modified = True
        
    def remove_task(self, task: Task) -> None:
        """Remove a task from the project."""
        if task in self.tasks:
            self.tasks.remove(task)
            self.modified = True
            
    def add_resource(self, resource: Resource) -> None:
        """Add a new resource to the project."""
        self.resources.append(resource)
        self.modified = True
        
    def remove_resource(self, resource: Resource) -> None:
        """Remove a resource from the project."""
        if resource in self.resources:
            self.resources.remove(resource)
            self.modified = True
            
    def calculate_critical_path(self) -> List[Task]:
        """Calculate the critical path of the project."""
        # Initialize early start and early finish
        for task in self.tasks:
            task.early_start = 0
            task.early_finish = task.duration
            
        # Forward pass
        for task in self.tasks:
            for successor in task.successors:
                if successor.early_start < task.early_finish:
                    successor.early_start = task.early_finish
                    successor.early_finish = successor.early_start + successor.duration
                    
        # Initialize late start and late finish
        project_duration = max(task.early_finish for task in self.tasks)
        for task in self.tasks:
            task.late_finish = project_duration
            task.late_start = task.late_finish - task.duration
            
        # Backward pass
        for task in reversed(self.tasks):
            for predecessor in task.predecessors:
                if predecessor.late_finish > task.late_start:
                    predecessor.late_finish = task.late_start
                    predecessor.late_start = predecessor.late_finish - predecessor.duration
                    
        # Find critical path (tasks with zero float)
        critical_path = [task for task in self.tasks if task.late_start - task.early_start == 0]
        return critical_path
    
    def save_baseline(self) -> None:
        """Save the current project state as a baseline."""
        self.baseline = {
            'tasks': [(task.name, task.start_date, task.duration) for task in self.tasks],
            'resources': [(res.name, res.cost_rate, res.availability) for res in self.resources],
            'date': datetime.now()
        }
        
    def get_project_duration(self) -> int:
        """Calculate the total project duration in days."""
        if not self.tasks:
            return 0
        latest_finish = max(task.get_end_date() for task in self.tasks)
        return (latest_finish - self.start_date).days
    
    def get_total_cost(self) -> float:
        """Calculate the total project cost."""
        return sum(task.get_cost() for task in self.tasks)
    
    def find_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its ID."""
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def get_resource_utilization(self) -> Dict[Resource, float]:
        """Calculate resource utilization."""
        utilization = {}
        for resource in self.resources:
            total_hours = sum(assignment.hours for assignment in resource.assignments)
            available_hours = resource.availability * 8 * self.get_project_duration()  # Assuming 8-hour workdays
            utilization[resource] = total_hours / available_hours if available_hours > 0 else 0
        return utilization
