from typing import List, Optional
from datetime import datetime
from ..models.project import Project
from ..models.task import Task
from ..models.resource import Resource

class ProjectController:
    def __init__(self, project: Project):
        self.project = project
        self.current_filename = None
        self.undo_stack = []
        self.redo_stack = []
        
    def new_project(self):
        """Create a new project."""
        self.save_state()
        self.project = Project("New Project", datetime.now())
        self.current_filename = None
        
    def load_project(self, filename: str):
        """Load project from file."""
        # Implementation for loading project from file
        pass
        
    def save_project(self, filename: Optional[str] = None):
        """Save project to file."""
        if filename:
            self.current_filename = filename
        # Implementation for saving project to file
        pass
        
    def create_task(self, name: str, duration: int, start_date: datetime) -> Task:
        """Create a new task."""
        self.save_state()
        task = Task(name, duration, start_date)
        self.project.add_task(task)
        return task
        
    def delete_task(self, task: Task):
        """Delete a task."""
        self.save_state()
        self.project.remove_task(task)
        
    def create_resource(self, name: str, cost_rate: float, availability: float) -> Resource:
        """Create a new resource."""
        self.save_state()
        resource = Resource(name, cost_rate, availability)
        self.project.add_resource(resource)
        return resource
        
    def delete_resource(self, resource: Resource):
        """Delete a resource."""
        self.save_state()
        self.project.remove_resource(resource)
        
    def calculate_critical_path(self) -> List[Task]:
        """Calculate the critical path."""
        return self.project.calculate_critical_path()
        
    def level_resources(self):
        """Perform resource leveling."""
        self.save_state()
        tasks = self.project.tasks.copy()
        resources = self.project.resources.copy()
        
        # Sort tasks by priority and dependencies
        tasks.sort(key=lambda t: (t.priority, len(t.predecessors)), reverse=True)
        
        # Attempt to resolve resource over-allocation
        for resource in resources:
            utilization = resource.get_utilization(
                self.project.start_date,
                max(task.get_end_date() for task in tasks)
            )
            
            if utilization > 1:
                # Find tasks using this resource
                resource_tasks = [t for t in tasks if any(
                    a['resource'] == resource for a in t.assignments
                )]
                
                # Sort by priority and float time
                resource_tasks.sort(key=lambda t: (-t.priority, t.get_float()))
                
                # Adjust task dates to resolve over-allocation
                for task in resource_tasks:
                    if task.get_float() > 0:
                        # Delay task within its float time
                        delay = min(
                            task.get_float(),
                            int((utilization - 1) * task.duration)
                        )
                        task.start_date += timedelta(days=delay)
                        
    def save_baseline(self):
        """Save the current project state as baseline."""
        self.project.save_baseline()
        
    def export_pdf(self, filename: str):
        """Export project to PDF."""
        # Implementation for PDF export
        pass
        
    def export_excel(self, filename: str):
        """Export project to Excel."""
        # Implementation for Excel export
        pass
        
    def save_state(self):
        """Save current state for undo/redo."""
        import copy
        self.undo_stack.append(copy.deepcopy(self.project))
        self.redo_stack.clear()
        
    def undo(self):
        """Undo last action."""
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.project))
            self.project = self.undo_stack.pop()

    def redo(self):
        """Redo last undone action."""
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.project))
            self.project = self.redo_stack.pop()

    def analyze_project(self) -> dict:
        """Perform comprehensive project analysis."""
        return {
            'duration': self.project.get_project_duration(),
            'total_cost': self.project.get_total_cost(),
            'resource_utilization': self.project.get_resource_utilization(),
            'critical_path': self.project.calculate_critical_path(),
            'completion_percentage': self.calculate_project_completion(),
            'resource_conflicts': self.find_resource_conflicts(),
            'schedule_risks': self.analyze_schedule_risks()
        }

    def calculate_project_completion(self) -> float:
        """Calculate overall project completion percentage."""
        if not self.project.tasks:
            return 0.0

        weighted_completion = sum(
            task.completion_percentage * task.duration
            for task in self.project.tasks
        )
        total_duration = sum(task.duration for task in self.project.tasks)

        return weighted_completion / total_duration if total_duration > 0 else 0.0

    def find_resource_conflicts(self) -> List[dict]:
        """Find resource over-allocation conflicts."""
        conflicts = []

        for resource in self.project.resources:
            # Analyze day by day for overlapping assignments
            current_date = self.project.start_date
            end_date = max(task.get_end_date() for task in self.project.tasks)

            while current_date <= end_date:
                # Get assignments for current date
                daily_assignments = [
                    assignment for task in self.project.tasks
                    for assignment in task.assignments
                    if assignment['resource'] == resource
                       and assignment['start_date'] <= current_date <= assignment['end_date']
                ]

                # Calculate total units assigned
                total_units = sum(assignment['units'] for assignment in daily_assignments)

                if total_units > resource.availability:
                    conflicts.append({
                        'date': current_date,
                        'resource': resource,
                        'assignments': daily_assignments,
                        'overallocation': total_units - resource.availability
                    })

                current_date += timedelta(days=1)

        return conflicts

    def analyze_schedule_risks(self) -> List[dict]:
        """Analyze potential schedule risks."""
        risks = []

        # Check for tasks with no slack
        critical_path = self.project.calculate_critical_path()
        for task in critical_path:
            risks.append({
                'type': 'critical_path',
                'task': task,
                'impact': 'high',
                'description': f"Task '{task.name}' is on critical path with no slack time"
            })

        # Check for resource dependencies
        for resource in self.project.resources:
            resource_tasks = [
                task for task in self.project.tasks
                if any(a['resource'] == resource for a in task.assignments)
            ]
            if len(resource_tasks) > 3:
                risks.append({
                    'type': 'resource_dependency',
                    'resource': resource,
                    'tasks': resource_tasks,
                    'impact': 'medium',
                    'description': f"Resource '{resource.name}' is assigned to {len(resource_tasks)} tasks"
                })

        # Check for long duration tasks
        avg_duration = sum(task.duration for task in self.project.tasks) / len(self.project.tasks)
        for task in self.project.tasks:
            if task.duration > 2 * avg_duration:
                risks.append({
                    'type': 'long_duration',
                    'task': task,
                    'impact': 'medium',
                    'description': f"Task '{task.name}' has unusually long duration"
                })

        return risks

    def optimize_schedule(self):
        """Attempt to optimize project schedule."""
        self.save_state()

        # First, perform resource leveling
        self.level_resources()

        # Then, try to compress schedule where possible
        critical_path = self.project.calculate_critical_path()
        non_critical_tasks = [task for task in self.project.tasks if task not in critical_path]

        # Sort non-critical tasks by total float (ascending) and duration (descending)
        non_critical_tasks.sort(key=lambda t: (t.get_float(), -t.duration))

        for task in non_critical_tasks:
            # Try to reduce duration by increasing resource allocation
            current_assignments = task.assignments.copy()
            can_compress = any(
                assignment['units'] < 1.0 and
                assignment['resource'].get_availability(task.start_date) > assignment['units']
                for assignment in current_assignments
            )

            if can_compress:
                # Increase resource allocation and reduce duration
                for assignment in task.assignments:
                    available = assignment['resource'].get_availability(task.start_date)
                    if available > assignment['units']:
                        new_units = min(1.0, available)
                        compression_factor = new_units / assignment['units']
                        new_duration = int(task.duration / compression_factor)

                        # Update task
                        task.duration = new_duration
                        assignment['units'] = new_units

    def import_from_ms_project(self, filename: str):
        """Import project data from Microsoft Project file."""
        # Implementation for importing from MS Project
        pass

    def export_to_ms_project(self, filename: str):
        """Export project data to Microsoft Project file."""
        # Implementation for exporting to MS Project
        pass

    def generate_reports(self) -> dict:
        """Generate various project reports."""
        return {
            'summary': self.generate_summary_report(),
            'tasks': self.generate_task_report(),
            'resources': self.generate_resource_report(),
            'timeline': self.generate_timeline_report()
        }

    def generate_summary_report(self) -> dict:
        """Generate project summary report."""
        return {
            'name': self.project.name,
            'start_date': self.project.start_date,
            'end_date': max(task.get_end_date() for task in self.project.tasks),
            'duration': self.project.get_project_duration(),
            'total_tasks': len(self.project.tasks),
            'completed_tasks': len([t for t in self.project.tasks if t.completion_percentage == 100]),
            'total_resources': len(self.project.resources),
            'total_cost': self.project.get_total_cost(),
            'completion_percentage': self.calculate_project_completion()
        }

    def generate_task_report(self) -> List[dict]:
        """Generate detailed task report."""
        return [{
            'id': task.id,
            'name': task.name,
            'start_date': task.start_date,
            'end_date': task.get_end_date(),
            'duration': task.duration,
            'completion': task.completion_percentage,
            'resources': [a['resource'].name for a in task.assignments],
            'predecessors': [p.name for p in task.predecessors],
            'cost': task.get_cost(),
            'is_critical': task.is_critical()
        } for task in self.project.tasks]

    def generate_resource_report(self) -> List[dict]:
        """Generate detailed resource report."""
        return [{
            'name': resource.name,
            'cost_rate': resource.cost_rate,
            'availability': resource.availability,
            'assignments': len(resource.assignments),
            'utilization': self.project.get_resource_utilization()[resource],
            'total_cost': sum(
                assignment['hours'] * resource.cost_rate
                for assignment in resource.assignments
            ),
            'skills': resource.skills
        } for resource in self.project.resources]

    def generate_timeline_report(self) -> List[dict]:
        """Generate timeline report with milestones and key dates."""
        timeline = []

        # Add project start
        timeline.append({
            'date': self.project.start_date,
            'event': 'Project Start',
            'type': 'milestone'
        })

        # Add task starts and completions
        for task in self.project.tasks:
            timeline.append({
                'date': task.start_date,
                'event': f"Task '{task.name}' Start",
                'type': 'task_start',
                'task': task
            })
            timeline.append({
                'date': task.get_end_date(),
                'event': f"Task '{task.name}' End",
                'type': 'task_end',
                'task': task
            })

        # Add project end
        timeline.append({
            'date': max(task.get_end_date() for task in self.project.tasks),
            'event': 'Project End',
            'type': 'milestone'
        })

        # Sort by date
        timeline.sort(key=lambda x: x['date'])

        return timeline