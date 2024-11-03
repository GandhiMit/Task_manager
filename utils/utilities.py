from datetime import datetime, timedelta
from typing import List, Tuple

def get_working_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of working days between two dates."""
    days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Consider Monday (0) through Friday (4) as working days
        if current_date.weekday() < 5:
            days += 1
        current_date += timedelta(days=1)
        
    return days

def add_working_days(date: datetime, days: int) -> datetime:
    """Add specified number of working days to a date."""
    current_date = date
    remaining_days = days
    
    while remaining_days > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Monday through Friday
            remaining_days -= 1
            
    return current_date

def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Get list of dates between start and end dates."""
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
        
    return dates

def get_month_boundaries(date: datetime) -> Tuple[datetime, datetime]:
    """Get first and last day of the month for given date."""
    first_day = date.replace(day=1)
    
    # Find last day by going to first day of next month and subtracting one day
    if date.month == 12:
        last_day = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
        
    return first_day, last_day

def is_working_day(date: datetime) -> bool:
    """Check if given date is a working day."""
    return date.weekday() < 5

def get_fiscal_year_dates(date: datetime, fiscal_start_month: int = 1) -> Tuple[datetime, datetime]:
    """Get fiscal year start and end dates."""
    if date.month >= fiscal_start_month:
        start_date = datetime(date.year, fiscal_start_month, 1)
        end_date = datetime(date.year + 1, fiscal_start_month, 1) - timedelta(days=1)
    else:
        start_date = datetime(date.year - 1, fiscal_start_month, 1)
        end_date = datetime(date.year, fiscal_start_month, 1) - timedelta(days=1)
        
    return start_date, end_date

def get_quarter_dates(date: datetime) -> Tuple[datetime, datetime]:
    """Get quarter start and end dates."""
    quarter = (date.month - 1) // 3
    start_month = quarter * 3 + 1
    
    start_date = date.replace(month=start_month, day=1)
    if start_month + 2 == 12:
        end_date = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = date.replace(month=start_month + 3, day=1) - timedelta(days=1)
        
    return start_date, end_date

def calculate_date_difference(start_date: datetime, end_date: datetime, 
                            include_working_days: bool = True) -> dict:
    """Calculate detailed difference between two dates."""
    total_days = (end_date - start_date).days
    working_days = get_working_days(start_date, end_date) if include_working_days else total_days
    
    weeks = total_days // 7
    remaining_days = total_days % 7
    
    return {
        'total_days': total_days,
        'working_days': working_days,
        'weeks': weeks,
        'remaining_days': remaining_days,
        'weekends': total_days - working_days if include_working_days else 0
    }
