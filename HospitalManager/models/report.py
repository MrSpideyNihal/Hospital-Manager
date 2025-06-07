"""
Report Model - Handles report generation and data analysis
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter

class ReportGenerator:
    """Report generator class for creating various hospital reports"""
    
    def __init__(self, data_manager):
        """Initialize report generator with data manager"""
        self.data_manager = data_manager
    
    def generate_patient_visits_report(self, start_date: str, end_date: str, 
                                     doctor_filter: str = "") -> Dict[str, Any]:
        """Generate patient visits report for date range"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Get all OPD visits in date range
        opd_visits = self.data_manager.get_opd_visits()
        filtered_visits = []
        
        for visit in opd_visits:
            try:
                visit_dt = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                if start_dt <= visit_dt.date() <= end_dt.date():
                    if not doctor_filter or visit.doctor_name == doctor_filter:
                        filtered_visits.append(visit)
            except ValueError:
                continue
        
        # Generate statistics
        total_visits = len(filtered_visits)
        daily_counts = defaultdict(int)
        doctor_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for visit in filtered_visits:
            visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").date()
            daily_counts[visit_date.strftime("%Y-%m-%d")] += 1
            doctor_counts[visit.doctor_name] += 1
            status_counts[visit.status] += 1
        
        # Calculate averages
        days_in_range = (end_dt - start_dt).days + 1
        avg_daily_visits = total_visits / days_in_range if days_in_range > 0 else 0
        
        return {
            "report_type": "Patient Visits Report",
            "date_range": f"{start_date} to {end_date}",
            "doctor_filter": doctor_filter or "All Doctors",
            "total_visits": total_visits,
            "average_daily_visits": round(avg_daily_visits, 2),
            "daily_breakdown": dict(daily_counts),
            "doctor_breakdown": dict(doctor_counts),
            "status_breakdown": dict(status_counts),
            "visits": [visit.to_dict() for visit in filtered_visits],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_appointment_report(self, start_date: str, end_date: str, 
                                  doctor_filter: str = "") -> Dict[str, Any]:
        """Generate appointment summary report"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Get all appointments in date range
        appointments = self.data_manager.get_appointments()
        filtered_appointments = []
        
        for appointment in appointments:
            try:
                appt_dt = datetime.strptime(appointment.appointment_date, "%Y-%m-%d")
                if start_dt <= appt_dt <= end_dt:
                    if not doctor_filter or appointment.doctor_name == doctor_filter:
                        filtered_appointments.append(appointment)
            except ValueError:
                continue
        
        # Generate statistics
        total_appointments = len(filtered_appointments)
        status_counts = defaultdict(int)
        doctor_counts = defaultdict(int)
        department_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for appointment in filtered_appointments:
            status_counts[appointment.status] += 1
            doctor_counts[appointment.doctor_name] += 1
            department_counts[appointment.department] += 1
            daily_counts[appointment.appointment_date] += 1
        
        # Calculate completion rate
        completed = status_counts.get("Completed", 0)
        completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        
        return {
            "report_type": "Appointment Summary Report",
            "date_range": f"{start_date} to {end_date}",
            "doctor_filter": doctor_filter or "All Doctors",
            "total_appointments": total_appointments,
            "completion_rate": round(completion_rate, 2),
            "status_breakdown": dict(status_counts),
            "doctor_breakdown": dict(doctor_counts),
            "department_breakdown": dict(department_counts),
            "daily_breakdown": dict(daily_counts),
            "appointments": [appointment.to_dict() for appointment in filtered_appointments],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_doctor_consultation_report(self, doctor_name: str, 
                                          start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate doctor-wise consultation report"""
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Get doctor's appointments and OPD visits
        appointments = self.data_manager.get_appointments()
        opd_visits = self.data_manager.get_opd_visits()
        
        doctor_appointments = []
        doctor_visits = []
        
        for appointment in appointments:
            if appointment.doctor_name == doctor_name:
                try:
                    appt_dt = datetime.strptime(appointment.appointment_date, "%Y-%m-%d")
                    if start_dt <= appt_dt <= end_dt:
                        doctor_appointments.append(appointment)
                except ValueError:
                    continue
        
        for visit in opd_visits:
            if visit.doctor_name == doctor_name:
                try:
                    visit_dt = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                    if start_dt <= visit_dt.date() <= end_dt.date():
                        doctor_visits.append(visit)
                except ValueError:
                    continue
        
        # Generate statistics
        total_consultations = len(doctor_visits)
        total_appointments = len(doctor_appointments)
        
        daily_consultations = defaultdict(int)
        patient_counts = set()
        
        for visit in doctor_visits:
            visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").date()
            daily_consultations[visit_date.strftime("%Y-%m-%d")] += 1
            patient_counts.add(visit.patient_id)
        
        unique_patients = len(patient_counts)
        days_in_range = (end_dt - start_dt).days + 1
        avg_daily_consultations = total_consultations / days_in_range if days_in_range > 0 else 0
        
        return {
            "report_type": "Doctor Consultation Report",
            "doctor_name": doctor_name,
            "date_range": f"{start_date} to {end_date}",
            "total_consultations": total_consultations,
            "total_appointments": total_appointments,
            "unique_patients": unique_patients,
            "average_daily_consultations": round(avg_daily_consultations, 2),
            "daily_breakdown": dict(daily_consultations),
            "consultations": [visit.to_dict() for visit in doctor_visits],
            "appointments": [appointment.to_dict() for appointment in doctor_appointments],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_daily_summary_report(self, date: str) -> Dict[str, Any]:
        """Generate daily summary report"""
        try:
            report_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        # Get data for the specific date
        appointments = self.data_manager.get_appointments()
        opd_visits = self.data_manager.get_opd_visits()
        patients = self.data_manager.get_patients()
        
        # Filter data for the date
        daily_appointments = [appt for appt in appointments 
                            if appt.appointment_date == date]
        
        daily_visits = []
        for visit in opd_visits:
            try:
                visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").date()
                if visit_date == report_date:
                    daily_visits.append(visit)
            except ValueError:
                continue
        
        # New patient registrations
        new_patients = []
        for patient in patients:
            try:
                reg_date = datetime.strptime(patient.registration_date, "%Y-%m-%d %H:%M:%S").date()
                if reg_date == report_date:
                    new_patients.append(patient)
            except ValueError:
                continue
        
        # Generate statistics
        appointment_status = defaultdict(int)
        visit_status = defaultdict(int)
        doctor_consultations = defaultdict(int)
        
        for appointment in daily_appointments:
            appointment_status[appointment.status] += 1
        
        for visit in daily_visits:
            visit_status[visit.status] += 1
            doctor_consultations[visit.doctor_name] += 1
        
        return {
            "report_type": "Daily Summary Report",
            "date": date,
            "new_patients": len(new_patients),
            "total_appointments": len(daily_appointments),
            "total_consultations": len(daily_visits),
            "appointment_status": dict(appointment_status),
            "consultation_status": dict(visit_status),
            "doctor_consultations": dict(doctor_consultations),
            "new_patient_details": [patient.to_dict() for patient in new_patients],
            "appointments": [appointment.to_dict() for appointment in daily_appointments],
            "consultations": [visit.to_dict() for visit in daily_visits],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def export_to_csv(self, report_data: Dict, filename: str) -> bool:
        """Export report data to CSV file"""
        try:
            import os
            
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            filepath = os.path.join(exports_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if "appointments" in report_data:
                    # Appointment report
                    fieldnames = ['appointment_id', 'patient_id', 'doctor_name', 
                                'department', 'appointment_date', 'appointment_time', 'status']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for appointment in report_data['appointments']:
                        writer.writerow({k: appointment.get(k, '') for k in fieldnames})
                
                elif "consultations" in report_data:
                    # OPD consultation report
                    fieldnames = ['visit_id', 'patient_id', 'doctor_name', 'visit_date', 
                                'symptoms', 'diagnosis', 'status']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for visit in report_data['consultations']:
                        writer.writerow({k: visit.get(k, '') for k in fieldnames})
                
                else:
                    # Summary statistics
                    writer = csv.writer(csvfile)
                    writer.writerow(['Report Type', report_data.get('report_type', 'Unknown')])
                    writer.writerow(['Generated At', report_data.get('generated_at', '')])
                    writer.writerow(['Date Range', report_data.get('date_range', '')])
                    writer.writerow([])
                    
                    # Write key statistics
                    for key, value in report_data.items():
                        if key not in ['report_type', 'generated_at', 'date_range', 'appointments', 'consultations']:
                            if isinstance(value, dict):
                                writer.writerow([key.replace('_', ' ').title()])
                                for k, v in value.items():
                                    writer.writerow(['', k, v])
                            else:
                                writer.writerow([key.replace('_', ' ').title(), value])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_report_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics for dashboard"""
        patients = self.data_manager.get_patients()
        appointments = self.data_manager.get_appointments()
        opd_visits = self.data_manager.get_opd_visits()
        
        today = datetime.now().date()
        
        # Today's statistics
        today_appointments = [appt for appt in appointments 
                            if appt.appointment_date == today.strftime("%Y-%m-%d")]
        
        today_visits = []
        for visit in opd_visits:
            try:
                visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").date()
                if visit_date == today:
                    today_visits.append(visit)
            except ValueError:
                continue
        
        # This month's statistics
        month_start = today.replace(day=1)
        month_patients = []
        for patient in patients:
            try:
                reg_date = datetime.strptime(patient.registration_date, "%Y-%m-%d %H:%M:%S").date()
                if reg_date >= month_start:
                    month_patients.append(patient)
            except ValueError:
                continue
        
        return {
            "total_patients": len(patients),
            "new_patients_this_month": len(month_patients),
            "appointments_today": len(today_appointments),
            "consultations_today": len(today_visits),
            "pending_appointments": len([appt for appt in today_appointments 
                                       if appt.status == "Scheduled"]),
            "completed_visits_today": len([visit for visit in today_visits 
                                         if visit.status == "Completed"])
        }
