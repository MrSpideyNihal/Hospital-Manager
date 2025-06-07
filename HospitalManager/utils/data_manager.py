"""
Data Manager - Handles all data persistence and retrieval operations
"""

import json
import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict

from models.patient import Patient
from models.appointment import Appointment
from models.opd import OPDVisit, OPDQueue

class DataManager:
    """Central data manager for all hospital data operations"""
    
    def __init__(self, data_dir: str = None):
        """Initialize data manager with data directory"""
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = data_dir
        self.patients_file = os.path.join(data_dir, 'patients.json')
        self.appointments_file = os.path.join(data_dir, 'appointments.json')
        self.opd_visits_file = os.path.join(data_dir, 'opd_visits.json')
        self.settings_file = os.path.join(data_dir, 'settings.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize OPD queue
        self.opd_queue = OPDQueue()
        
        # Load initial data
        self._ensure_data_files_exist()
    
    def _ensure_data_files_exist(self):
        """Create empty data files if they don't exist"""
        default_files = {
            self.patients_file: [],
            self.appointments_file: [],
            self.opd_visits_file: [],
            self.settings_file: {
                "hospital_name": "City Hospital",
                "announcement_enabled": True,
                "announcement_interval": 30,
                "last_backup": "",
                "auto_backup_enabled": True
            }
        }
        
        for file_path, default_data in default_files.items():
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Error creating {file_path}: {e}")
    
    def _load_json_file(self, file_path: str, default_value=None):
        """Load data from JSON file with error handling"""
        if default_value is None:
            default_value = []
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_value
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading {file_path}: {e}")
            return default_value
    
    def _save_json_file(self, file_path: str, data):
        """Save data to JSON file with error handling"""
        try:
            # Create backup before saving
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False
    
    # Patient Management
    def get_patients(self) -> List[Patient]:
        """Get all patients"""
        data = self._load_json_file(self.patients_file)
        return [Patient.from_dict(patient_data) for patient_data in data]
    
    def save_patient(self, patient: Patient) -> bool:
        """Save or update a patient"""
        patients_data = self._load_json_file(self.patients_file)
        
        # Check if patient already exists
        patient_exists = False
        for i, existing_patient in enumerate(patients_data):
            if existing_patient.get('patient_id') == patient.patient_id:
                patients_data[i] = patient.to_dict()
                patient_exists = True
                break
        
        # Add new patient if not exists
        if not patient_exists:
            patients_data.append(patient.to_dict())
        
        return self._save_json_file(self.patients_file, patients_data)
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        patients = self.get_patients()
        for patient in patients:
            if patient.patient_id == patient_id:
                return patient
        return None
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient"""
        patients_data = self._load_json_file(self.patients_file)
        patients_data = [p for p in patients_data if p.get('patient_id') != patient_id]
        return self._save_json_file(self.patients_file, patients_data)
    
    def search_patients(self, query: str, filters: Dict = None) -> List[Patient]:
        """Search patients with query and filters"""
        patients = self.get_patients()
        results = []
        
        for patient in patients:
            # Text search
            if not patient.search_matches(query):
                continue
            
            # Apply filters
            if filters:
                if filters.get('gender') and patient.gender != filters['gender']:
                    continue
                if filters.get('min_age') and patient.age < filters['min_age']:
                    continue
                if filters.get('max_age') and patient.age > filters['max_age']:
                    continue
            
            results.append(patient)
        
        return results
    
    # Appointment Management
    def get_appointments(self) -> List[Appointment]:
        """Get all appointments"""
        data = self._load_json_file(self.appointments_file)
        return [Appointment.from_dict(appointment_data) for appointment_data in data]
    
    def save_appointment(self, appointment: Appointment) -> bool:
        """Save or update an appointment"""
        appointments_data = self._load_json_file(self.appointments_file)
        
        # Check if appointment already exists
        appointment_exists = False
        for i, existing_appointment in enumerate(appointments_data):
            if existing_appointment.get('appointment_id') == appointment.appointment_id:
                appointments_data[i] = appointment.to_dict()
                appointment_exists = True
                break
        
        # Add new appointment if not exists
        if not appointment_exists:
            appointments_data.append(appointment.to_dict())
        
        # Update patient's appointment list
        patient = self.get_patient_by_id(appointment.patient_id)
        if patient:
            if appointment.appointment_id not in patient.appointments:
                patient.appointments.append(appointment.appointment_id)
                self.save_patient(patient)
        
        return self._save_json_file(self.appointments_file, appointments_data)
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID"""
        appointments = self.get_appointments()
        for appointment in appointments:
            if appointment.appointment_id == appointment_id:
                return appointment
        return None
    
    def delete_appointment(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        appointments_data = self._load_json_file(self.appointments_file)
        appointments_data = [a for a in appointments_data if a.get('appointment_id') != appointment_id]
        return self._save_json_file(self.appointments_file, appointments_data)
    
    def get_appointments_by_date(self, date: str) -> List[Appointment]:
        """Get appointments for a specific date"""
        appointments = self.get_appointments()
        return [appt for appt in appointments if appt.appointment_date == date]
    
    def get_appointments_by_doctor(self, doctor_name: str) -> List[Appointment]:
        """Get appointments for a specific doctor"""
        appointments = self.get_appointments()
        return [appt for appt in appointments if appt.doctor_name == doctor_name]
    
    # OPD Management
    def get_opd_visits(self) -> List[OPDVisit]:
        """Get all OPD visits"""
        data = self._load_json_file(self.opd_visits_file)
        return [OPDVisit.from_dict(visit_data) for visit_data in data]
    
    def save_opd_visit(self, visit: OPDVisit) -> bool:
        """Save or update an OPD visit"""
        visits_data = self._load_json_file(self.opd_visits_file)
        
        # Check if visit already exists
        visit_exists = False
        for i, existing_visit in enumerate(visits_data):
            if existing_visit.get('visit_id') == visit.visit_id:
                visits_data[i] = visit.to_dict()
                visit_exists = True
                break
        
        # Add new visit if not exists
        if not visit_exists:
            visits_data.append(visit.to_dict())
        
        # Update patient's visit list
        patient = self.get_patient_by_id(visit.patient_id)
        if patient:
            if visit.visit_id not in patient.opd_visits:
                patient.opd_visits.append(visit.visit_id)
                self.save_patient(patient)
        
        return self._save_json_file(self.opd_visits_file, visits_data)
    
    def get_opd_visit_by_id(self, visit_id: str) -> Optional[OPDVisit]:
        """Get OPD visit by ID"""
        visits = self.get_opd_visits()
        for visit in visits:
            if visit.visit_id == visit_id:
                return visit
        return None
    
    def get_patient_opd_history(self, patient_id: str) -> List[OPDVisit]:
        """Get OPD visit history for a patient"""
        visits = self.get_opd_visits()
        return [visit for visit in visits if visit.patient_id == patient_id]
    
    def get_todays_opd_visits(self) -> List[OPDVisit]:
        """Get today's OPD visits"""
        visits = self.get_opd_visits()
        return [visit for visit in visits if visit.is_today()]
    
    # Settings Management
    def get_settings(self) -> Dict:
        """Get application settings"""
        return self._load_json_file(self.settings_file, {})
    
    def save_settings(self, settings: Dict) -> bool:
        """Save application settings"""
        return self._save_json_file(self.settings_file, settings)
    
    def get_setting(self, key: str, default_value=None):
        """Get a specific setting value"""
        settings = self.get_settings()
        return settings.get(key, default_value)
    
    def set_setting(self, key: str, value) -> bool:
        """Set a specific setting value"""
        settings = self.get_settings()
        settings[key] = value
        return self.save_settings(settings)
    
    # Backup and Restore
    def create_backup(self) -> bool:
        """Create a backup of all data"""
        try:
            backup_dir = os.path.join(self.data_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"hospital_backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Collect all data
            backup_data = {
                'patients': self._load_json_file(self.patients_file),
                'appointments': self._load_json_file(self.appointments_file),
                'opd_visits': self._load_json_file(self.opd_visits_file),
                'settings': self._load_json_file(self.settings_file),
                'backup_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '1.0'
            }
            
            # Save backup
            success = self._save_json_file(backup_path, backup_data)
            
            if success:
                # Update last backup time
                self.set_setting('last_backup', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            return success
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_file_path: str) -> bool:
        """Restore data from backup file"""
        try:
            backup_data = self._load_json_file(backup_file_path)
            
            if not backup_data or 'patients' not in backup_data:
                return False
            
            # Restore each data file
            success = True
            success &= self._save_json_file(self.patients_file, backup_data.get('patients', []))
            success &= self._save_json_file(self.appointments_file, backup_data.get('appointments', []))
            success &= self._save_json_file(self.opd_visits_file, backup_data.get('opd_visits', []))
            success &= self._save_json_file(self.settings_file, backup_data.get('settings', {}))
            
            return success
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def get_backup_files(self) -> List[str]:
        """Get list of available backup files"""
        backup_dir = os.path.join(self.data_dir, 'backups')
        if not os.path.exists(backup_dir):
            return []
        
        try:
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith('hospital_backup_') and filename.endswith('.json'):
                    backup_files.append(os.path.join(backup_dir, filename))
            return sorted(backup_files, reverse=True)  # Most recent first
        except Exception as e:
            print(f"Error getting backup files: {e}")
            return []
    
    # Data Statistics
    def get_data_statistics(self) -> Dict:
        """Get overall data statistics"""
        patients = self.get_patients()
        appointments = self.get_appointments()
        opd_visits = self.get_opd_visits()
        
        today = datetime.now().date()
        
        return {
            'total_patients': len(patients),
            'total_appointments': len(appointments),
            'total_opd_visits': len(opd_visits),
            'todays_appointments': len([a for a in appointments if a.appointment_date == today.strftime("%Y-%m-%d")]),
            'todays_visits': len([v for v in opd_visits if v.is_today()]),
            'pending_appointments': len([a for a in appointments if a.status == "Scheduled"]),
            'completed_visits_today': len([v for v in opd_visits if v.is_today() and v.status == "Completed"])
        }
