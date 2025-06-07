"""
OPD (Outpatient Department) Model - Handles OPD visit data structure and operations
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class OPDVisit:
    """OPD Visit model class for managing outpatient visit information"""
    
    def __init__(self, visit_id: str = None, patient_id: str = "", 
                 doctor_name: str = "", visit_date: str = None,
                 symptoms: str = "", diagnosis: str = "", 
                 prescription: str = "", lab_tests: str = "",
                 follow_up_date: str = "", notes: str = "",
                 status: str = "In Progress"):
        """Initialize a new OPD visit instance"""
        self.visit_id = visit_id or self.generate_visit_id()
        self.patient_id = patient_id
        self.doctor_name = doctor_name
        self.visit_date = visit_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.symptoms = symptoms
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.lab_tests = lab_tests
        self.follow_up_date = follow_up_date
        self.notes = notes
        self.status = status  # In Progress, Completed, Follow-up Required
        self.vital_signs = {}  # Blood pressure, temperature, etc.
        
    @staticmethod
    def generate_visit_id() -> str:
        """Generate a unique visit ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"V{timestamp}"
    
    def to_dict(self) -> Dict:
        """Convert OPD visit object to dictionary"""
        return {
            'visit_id': self.visit_id,
            'patient_id': self.patient_id,
            'doctor_name': self.doctor_name,
            'visit_date': self.visit_date,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'lab_tests': self.lab_tests,
            'follow_up_date': self.follow_up_date,
            'notes': self.notes,
            'status': self.status,
            'vital_signs': self.vital_signs
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OPDVisit':
        """Create OPD visit object from dictionary"""
        visit = cls(
            visit_id=data.get('visit_id'),
            patient_id=data.get('patient_id', ''),
            doctor_name=data.get('doctor_name', ''),
            visit_date=data.get('visit_date'),
            symptoms=data.get('symptoms', ''),
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            lab_tests=data.get('lab_tests', ''),
            follow_up_date=data.get('follow_up_date', ''),
            notes=data.get('notes', ''),
            status=data.get('status', 'In Progress')
        )
        visit.vital_signs = data.get('vital_signs', {})
        return visit
    
    def validate(self) -> tuple[bool, str]:
        """Validate OPD visit data"""
        if not self.patient_id.strip():
            return False, "Patient ID is required"
        
        if not self.doctor_name.strip():
            return False, "Doctor name is required"
        
        if not self.symptoms.strip():
            return False, "Symptoms are required"
        
        # Validate follow-up date format if provided
        if self.follow_up_date.strip():
            try:
                datetime.strptime(self.follow_up_date, "%Y-%m-%d")
            except ValueError:
                return False, "Invalid follow-up date format. Use YYYY-MM-DD"
        
        return True, ""
    
    def set_vital_signs(self, blood_pressure: str = "", temperature: str = "", 
                       pulse: str = "", weight: str = "", height: str = ""):
        """Set vital signs for the visit"""
        self.vital_signs = {
            'blood_pressure': blood_pressure,
            'temperature': temperature,
            'pulse': pulse,
            'weight': weight,
            'height': height,
            'recorded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_visit_summary(self) -> Dict:
        """Get a summary of the visit for display"""
        return {
            'Visit ID': self.visit_id,
            'Patient ID': self.patient_id,
            'Doctor': self.doctor_name,
            'Date': self.visit_date,
            'Status': self.status,
            'Symptoms': self.symptoms[:100] + "..." if len(self.symptoms) > 100 else self.symptoms,
            'Diagnosis': self.diagnosis[:100] + "..." if len(self.diagnosis) > 100 else self.diagnosis
        }
    
    def is_today(self) -> bool:
        """Check if visit is from today"""
        visit_date = datetime.strptime(self.visit_date, "%Y-%m-%d %H:%M:%S").date()
        return visit_date == datetime.now().date()
    
    def needs_follow_up(self) -> bool:
        """Check if visit requires follow-up"""
        return bool(self.follow_up_date.strip()) or self.status == "Follow-up Required"
    
    def is_follow_up_due(self) -> bool:
        """Check if follow-up is due"""
        if not self.follow_up_date.strip():
            return False
        
        try:
            follow_up_date = datetime.strptime(self.follow_up_date, "%Y-%m-%d").date()
            return follow_up_date <= datetime.now().date()
        except ValueError:
            return False
    
    def search_matches(self, query: str) -> bool:
        """Check if OPD visit matches search query"""
        query = query.lower().strip()
        if not query:
            return True
        
        searchable_fields = [
            self.visit_id.lower(),
            self.patient_id.lower(),
            self.doctor_name.lower(),
            self.symptoms.lower(),
            self.diagnosis.lower(),
            self.status.lower(),
            self.visit_date
        ]
        
        return any(query in field for field in searchable_fields)
    
    def mark_completed(self):
        """Mark the visit as completed"""
        self.status = "Completed"
        if not self.visit_date:
            self.visit_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def __str__(self) -> str:
        """String representation of OPD visit"""
        return f"OPDVisit({self.visit_id}, {self.patient_id}, {self.doctor_name}, {self.visit_date})"

class OPDQueue:
    """Helper class for managing OPD patient queue"""
    
    def __init__(self):
        """Initialize OPD queue"""
        self.queue = []  # List of patient IDs in queue
        self.completed_today = []  # List of completed patient names for announcements
        
    def add_patient(self, patient_id: str):
        """Add patient to OPD queue"""
        if patient_id not in self.queue:
            self.queue.append(patient_id)
    
    def remove_patient(self, patient_id: str):
        """Remove patient from OPD queue"""
        if patient_id in self.queue:
            self.queue.remove(patient_id)
    
    def get_next_patient(self) -> Optional[str]:
        """Get next patient in queue"""
        return self.queue[0] if self.queue else None
    
    def get_queue_position(self, patient_id: str) -> int:
        """Get patient's position in queue (1-based)"""
        try:
            return self.queue.index(patient_id) + 1
        except ValueError:
            return -1
    
    def mark_patient_completed(self, patient_name: str):
        """Mark patient as completed and add to announcement queue"""
        self.completed_today.append({
            'name': patient_name,
            'completed_at': datetime.now().strftime("%H:%M:%S"),
            'announced': False
        })
    
    def get_pending_announcements(self) -> List[Dict]:
        """Get list of patients pending announcement"""
        return [patient for patient in self.completed_today if not patient['announced']]
    
    def mark_announced(self, patient_name: str):
        """Mark patient as announced"""
        for patient in self.completed_today:
            if patient['name'] == patient_name and not patient['announced']:
                patient['announced'] = True
                break
    
    def clear_completed_today(self):
        """Clear today's completed patients list"""
        self.completed_today.clear()
        self.queue.clear()
    
    def get_queue_summary(self) -> Dict:
        """Get queue summary statistics"""
        return {
            'total_in_queue': len(self.queue),
            'completed_today': len(self.completed_today),
            'pending_announcements': len(self.get_pending_announcements())
        }
