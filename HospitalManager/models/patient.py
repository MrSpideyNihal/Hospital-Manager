"""
Patient Model - Handles patient data structure and operations
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class Patient:
    """Patient model class for managing patient information"""
    
    def __init__(self, patient_id: str = None, name: str = "", age: int = 0, 
                 gender: str = "", contact: str = "", address: str = "", 
                 phone: str = "", registration_date: str = None):
        """Initialize a new patient instance"""
        self.patient_id = patient_id or self.generate_patient_id()
        self.name = name
        self.age = age
        self.gender = gender
        self.contact = contact
        self.address = address
        self.phone = phone
        self.registration_date = registration_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.appointments = []  # List of appointment IDs
        self.opd_visits = []    # List of OPD visit IDs
        self.medical_history = []  # Medical history entries
        
    @staticmethod
    def generate_patient_id() -> str:
        """Generate a unique patient ID"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"P{timestamp}"
    
    def to_dict(self) -> Dict:
        """Convert patient object to dictionary"""
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact': self.contact,
            'address': self.address,
            'phone': self.phone,
            'registration_date': self.registration_date,
            'appointments': self.appointments,
            'opd_visits': self.opd_visits,
            'medical_history': self.medical_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Patient':
        """Create patient object from dictionary"""
        patient = cls(
            patient_id=data.get('patient_id'),
            name=data.get('name', ''),
            age=data.get('age', 0),
            gender=data.get('gender', ''),
            contact=data.get('contact', ''),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            registration_date=data.get('registration_date')
        )
        patient.appointments = data.get('appointments', [])
        patient.opd_visits = data.get('opd_visits', [])
        patient.medical_history = data.get('medical_history', [])
        return patient
    
    def validate(self) -> tuple[bool, str]:
        """Validate patient data"""
        if not self.name.strip():
            return False, "Patient name is required"
        
        if self.age <= 0:
            return False, "Patient age must be greater than 0"
        
        if not self.gender.strip():
            return False, "Patient gender is required"
        
        if not self.phone.strip():
            return False, "Patient phone number is required"
        
        # Basic phone validation
        if not self.phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            return False, "Invalid phone number format"
        
        return True, ""
    
    def add_medical_history(self, entry: Dict):
        """Add a medical history entry"""
        entry['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.medical_history.append(entry)
    
    def get_latest_visit(self) -> Optional[Dict]:
        """Get the latest medical history entry"""
        if self.medical_history:
            return self.medical_history[-1]
        return None
    
    def search_matches(self, query: str) -> bool:
        """Check if patient matches search query"""
        query = query.lower().strip()
        if not query:
            return True
        
        searchable_fields = [
            self.name.lower(),
            self.patient_id.lower(),
            self.phone.lower(),
            self.gender.lower(),
            self.contact.lower(),
            self.address.lower(),
            str(self.age)
        ]
        
        return any(query in field for field in searchable_fields)
    
    def __str__(self) -> str:
        """String representation of patient"""
        return f"Patient({self.patient_id}, {self.name}, Age: {self.age})"
