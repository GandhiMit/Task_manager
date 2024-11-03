from datetime import datetime
from typing import List, Dict, Optional

class Resource:
    _id_counter = 1
    
    def __init__(self, name: str, cost_rate: float, availability: float = 1.0):
        self.id = Resource._id_counter
        Resource._id_counter += 1
        
        self.name = name
        self.cost_rate = cost_rate  # Cost per hour
        self.availability = availability  # Percentage of time available (0.0 to 1.0)
        self.assignments: List[Dict] = []
        self.calendar: Dict[datetime, float] = {}  # Custom calendar for availability
        self.skills: List[str] = []
        
    def add_assignment(self, assignment: Dict) -> None:
        """Add a new assignment to this resource."""
        self.assignments.append(assignment)
        self._update_calendar(assignment)
        
    def remove_assignment(self, assignment: Dict) -> None:
        """Remove an assignment from this resource."""
        if assignment in self.assignments:
            self.assignments.remove(assignment)
            self._update_calendar(assignment, remove=True)
            
    def get_availability(self, date: datetime) -> float:
        """Get resource availability for a specific date."""
        # Check custom calendar first
        if date in self.calendar:
            return self.calendar[date]
        
        # If no custom calendar entry, check if it's a working day
        if date.weekday() < 5:  # Monday = 0, Friday = 4
            return self.availability
        return 0.0
        
    def set_custom_availability(self, date: datetime, availability: float) -> None:
        """Set custom availability for a specific date."""
        self.calendar[date] = max(0.0, min(1.0, availability))
        
    def clear_custom_availability(self, date: datetime) -> None:
        """Clear custom availability for a specific date."""
        if date in self.calendar:
            del self.calendar[date]
            
    def get_utilization(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate resource utilization for a given period."""
        total_available_hours = 0
        total_assigned_hours = 0
        
        current_date = start_date
        while current_date <= end_date:
            availability = self.get_availability(current_date)
            total_available_hours += availability * 8  # Assuming 8-hour workdays
            
            # Calculate assigned hours for this date
            assigned_hours = sum(
                assignment['units'] * 8
                for assignment in self.assignments
                if assignment['start_date'] <= current_date <= assignment['end_date']
            )
            total_assigned_hours += assigned_hours
            
            current_date += timedelta(days=1)
            
        return total_assigned_hours / total_available_hours if total_available_hours > 0 else 0.0
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the resource."""
        if skill not in self.skills:
            self.skills.append(skill)
            
    def remove_skill(self, skill: str) -> None:
        """Remove a skill from the resource."""
        if skill in self.skills:
            self.skills.remove(skill)
            
    def _update_calendar(self, assignment: Dict, remove: bool = False) -> None:
        """Update the calendar based on assignments."""
        units = -assignment['units'] if remove else assignment['units']
        current_date = assignment['start_date']
        
        while current_date <= assignment['end_date']:
            if current_date not in self.calendar:
                self.calendar[current_date] = self.availability
            
            self.calendar[current_date] -= units
            self.calendar[current_date] = max(0.0, min(1.0, self.calendar[current_date]))
            
            current_date += timedelta(days=1)
