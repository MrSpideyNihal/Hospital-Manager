"""
Appointment Model - Handles appointment data structure and operations
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class Appointment:
    """Appointment model class for managing appointment information"""
    
    def __init__(self, appointment_id: str = None, patient_id: str = "", 
                 doctor_name: str = "", department: str = "", 
                 appointment_date: str = "", appointment_time: str = "",
                 status: str = "Scheduled", notes: str = ""):
        """Initialize a new appointment instance"""
        self.appointment_id = appointment_id or self.generate_appointment_id()
        self.patient_id = patient_id
        self.doctor_name = doctor_name
        self.department = department
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.status = status  # Scheduled, Completed, Cancelled, No-Show
        self.notes = notes
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    @staticmethod
    def generate_appointment_id() -> str:
        """Generate a unique appointment ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"A{timestamp}"
    
    def to_dict(self) -> Dict:
        """Convert appointment object to dictionary"""
        return {
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_name': self.doctor_name,
            'department': self.department,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'status': self.status,
            'notes': self.notes,
            'created_date': self.created_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Appointment':
        """Create appointment object from dictionary"""
        appointment = cls(
            appointment_id=data.get('appointment_id'),
            patient_id=data.get('patient_id', ''),
            doctor_name=data.get('doctor_name', ''),
            department=data.get('department', ''),
            appointment_date=data.get('appointment_date', ''),
            appointment_time=data.get('appointment_time', ''),
            status=data.get('status', 'Scheduled'),
            notes=data.get('notes', '')
        )
        appointment.created_date = data.get('created_date', appointment.created_date)
        return appointment
    
    def validate(self) -> tuple[bool, str]:
        """Validate appointment data"""
        if not self.patient_id.strip():
            return False, "Patient ID is required"
        
        if not self.doctor_name.strip():
            return False, "Doctor name is required"
        
        if not self.department.strip():
            return False, "Department is required"
        
        if not self.appointment_date.strip():
            return False, "Appointment date is required"
        
        if not self.appointment_time.strip():
            return False, "Appointment time is required"
        
        # Validate date format
        try:
            datetime.strptime(self.appointment_date, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
        
        # Validate time format
        try:
            datetime.strptime(self.appointment_time, "%H:%M")
        except ValueError:
            return False, "Invalid time format. Use HH:MM"
        
        # Check if appointment is in the past
        appointment_datetime = datetime.strptime(
            f"{self.appointment_date} {self.appointment_time}", 
            "%Y-%m-%d %H:%M"
        )
        if appointment_datetime < datetime.now():
            return False, "Cannot schedule appointment in the past"
        
        return True, ""
    
    def is_today(self) -> bool:
        """Check if appointment is scheduled for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.appointment_date == today
    
    def is_upcoming(self) -> bool:
        """Check if appointment is upcoming"""
        appointment_datetime = datetime.strptime(
            f"{self.appointment_date} {self.appointment_time}", 
            "%Y-%m-%d %H:%M"
        )
        return appointment_datetime > datetime.now()
    
    def get_datetime(self) -> datetime:
        """Get appointment datetime object"""
        return datetime.strptime(
            f"{self.appointment_date} {self.appointment_time}", 
            "%Y-%m-%d %H:%M"
        )
    
    def time_until_appointment(self) -> str:
        """Get human-readable time until appointment"""
        appointment_datetime = self.get_datetime()
        now = datetime.now()
        
        if appointment_datetime < now:
            return "Past"
        
        diff = appointment_datetime - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} day(s)"
        elif hours > 0:
            return f"{hours} hour(s)"
        else:
            return f"{minutes} minute(s)"
    
    def search_matches(self, query: str) -> bool:
        """Check if appointment matches search query"""
        query = query.lower().strip()
        if not query:
            return True
        
        searchable_fields = [
            self.appointment_id.lower(),
            self.patient_id.lower(),
            self.doctor_name.lower(),
            self.department.lower(),
            self.appointment_date,
            self.status.lower()
        ]
        
        return any(query in field for field in searchable_fields)
    
    def __str__(self) -> str:
        """String representation of appointment"""
        return f"Appointment({self.appointment_id}, {self.patient_id}, {self.doctor_name}, {self.appointment_date} {self.appointment_time})"

class DoctorSchedule:
    """Helper class for managing doctor schedules and availability"""
    
    DEFAULT_DOCTORS = [
        {"name": "Dr. Smith", "department": "General Medicine", "slots": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]},
        {"name": "Dr. Johnson", "department": "Cardiology", "slots": ["09:30", "10:30", "11:30", "14:30", "15:30"]},
        {"name": "Dr. Williams", "department": "Pediatrics", "slots": ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00"]},
        {"name": "Dr. Brown", "department": "Orthopedics", "slots": ["10:00", "11:00", "14:00", "15:00", "16:00"]},
        {"name": "Dr. Davis", "department": "Dermatology", "slots": ["09:00", "10:00", "11:00", "15:00", "16:00"]},
    ]
    
    @classmethod
    def get_available_slots(cls, doctor_name: str, date: str, existing_appointments: List[Appointment]) -> List[str]:
        """Get available time slots for a doctor on a specific date"""
        # Find doctor's default slots
        doctor_slots = []
        for doctor in cls.DEFAULT_DOCTORS:
            if doctor["name"] == doctor_name:
                doctor_slots = doctor["slots"].copy()
                break
        
        if not doctor_slots:
            return []
        
        # Remove booked slots
        booked_slots = []
        for appointment in existing_appointments:
            if (appointment.doctor_name == doctor_name and 
                appointment.appointment_date == date and 
                appointment.status in ["Scheduled", "Completed"]):
                booked_slots.append(appointment.appointment_time)
        
        available_slots = [slot for slot in doctor_slots if slot not in booked_slots]
        return available_slots
    
    @classmethod
    def get_doctors(cls) -> List[Dict]:
        """Get list of all doctors"""
        return cls.DEFAULT_DOCTORS.copy()
    
    @classmethod
    def get_departments(cls) -> List[str]:
        """Get list of all departments"""
        departments = list(set(doctor["department"] for doctor in cls.DEFAULT_DOCTORS))
        return sorted(departments)
