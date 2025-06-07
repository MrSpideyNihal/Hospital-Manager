"""
Reporting UI - Handles report generation, viewing, and export
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from models.report import ReportGenerator
import os
import threading

class ReportingFrame:
    """Reporting interface for generating various hospital reports"""
    
    def __init__(self, parent, data_manager):
        """Initialize reporting frame"""
        self.parent = parent
        self.data_manager = data_manager
        self.report_generator = ReportGenerator(data_manager)
        self.current_report_data = None
        
        self.create_widgets()
        self.load_dashboard_stats()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(main_frame, text="Reports & Analytics", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_patient_visits_tab()
        self.create_appointment_reports_tab()
        self.create_doctor_reports_tab()
        self.create_daily_summary_tab()
        self.create_export_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard overview tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Dashboard title
        ttk.Label(dashboard_frame, text="Hospital Dashboard", 
                 style='Title.TLabel').pack(pady=10)
        
        # Stats container
        stats_container = ttk.Frame(dashboard_frame)
        stats_container.pack(fill='x', padx=20, pady=10)
        
        # Create stats cards in a grid
        self.create_stats_cards(stats_container)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Quick Actions", padding="10")
        actions_frame.pack(fill='x', padx=20, pady=10)
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack()
        
        # Action buttons
        ttk.Button(actions_grid, text="Today's Summary", 
                  command=self.generate_today_summary).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(actions_grid, text="Weekly Report", 
                  command=self.generate_weekly_report).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(actions_grid, text="Monthly Report", 
                  command=self.generate_monthly_report).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(actions_grid, text="Export All Data", 
                  command=self.export_all_data).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(actions_grid, text="Refresh Dashboard", 
                  command=self.load_dashboard_stats).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(actions_grid, text="Create Backup", 
                  command=self.create_backup).grid(row=1, column=2, padx=5, pady=5)
        
        # Recent activity
        activity_frame = ttk.LabelFrame(dashboard_frame, text="Recent Activity", padding="5")
        activity_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Activity listbox
        self.activity_listbox = tk.Listbox(activity_frame, height=8)
        activity_scrollbar = ttk.Scrollbar(activity_frame, orient='vertical', 
                                         command=self.activity_listbox.yview)
        self.activity_listbox.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_listbox.pack(side='left', fill='both', expand=True)
        activity_scrollbar.pack(side='right', fill='y')
        
        # Load recent activity
        self.load_recent_activity()
    
    def create_stats_cards(self, parent):
        """Create statistical overview cards"""
        # Stats frame
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x')
        
        # Configure grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Create individual stat cards
        self.total_patients_var = tk.StringVar()
        self.new_patients_var = tk.StringVar()
        self.appointments_today_var = tk.StringVar()
        self.consultations_today_var = tk.StringVar()
        
        # Total Patients Card
        patients_card = ttk.LabelFrame(stats_frame, text="Total Patients", padding="10")
        patients_card.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Label(patients_card, textvariable=self.total_patients_var, 
                 font=('Arial', 20, 'bold')).pack()
        
        # New Patients This Month
        new_patients_card = ttk.LabelFrame(stats_frame, text="New This Month", padding="10")
        new_patients_card.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(new_patients_card, textvariable=self.new_patients_var, 
                 font=('Arial', 20, 'bold')).pack()
        
        # Appointments Today
        appointments_card = ttk.LabelFrame(stats_frame, text="Appointments Today", padding="10")
        appointments_card.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        ttk.Label(appointments_card, textvariable=self.appointments_today_var, 
                 font=('Arial', 20, 'bold')).pack()
        
        # Consultations Today
        consultations_card = ttk.LabelFrame(stats_frame, text="Consultations Today", padding="10")
        consultations_card.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        ttk.Label(consultations_card, textvariable=self.consultations_today_var, 
                 font=('Arial', 20, 'bold')).pack()
    
    def create_patient_visits_tab(self):
        """Create patient visits report tab"""
        visits_frame = ttk.Frame(self.notebook)
        self.notebook.add(visits_frame, text="Patient Visits")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(visits_frame, text="Report Parameters", padding="10")
        params_frame.pack(fill='x', padx=5, pady=5)
        
        # Date range
        date_frame = ttk.Frame(params_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(side='left', padx=(0, 5))
        ttk.Label(date_frame, text="From:").pack(side='left', padx=(10, 5))
        self.visits_start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.visits_start_date_var, width=12).pack(side='left', padx=(0, 10))
        
        ttk.Label(date_frame, text="To:").pack(side='left', padx=(0, 5))
        self.visits_end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.visits_end_date_var, width=12).pack(side='left', padx=(0, 10))
        
        # Doctor filter
        doctor_frame = ttk.Frame(params_frame)
        doctor_frame.pack(fill='x', pady=5)
        
        ttk.Label(doctor_frame, text="Doctor Filter:").pack(side='left', padx=(0, 5))
        self.visits_doctor_var = tk.StringVar()
        from models.appointment import DoctorSchedule
        doctor_options = ['All Doctors'] + [doc['name'] for doc in DoctorSchedule.get_doctors()]
        doctor_combo = ttk.Combobox(doctor_frame, textvariable=self.visits_doctor_var,
                                  values=doctor_options, width=20, state='readonly')
        doctor_combo.set('All Doctors')
        doctor_combo.pack(side='left', padx=(0, 10))
        
        # Generate button
        ttk.Button(doctor_frame, text="Generate Report", 
                  command=self.generate_patient_visits_report).pack(side='left', padx=(10, 0))
        
        # Report display area
        report_frame = ttk.LabelFrame(visits_frame, text="Report Results", padding="5")
        report_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Report text area
        self.visits_report_text = tk.Text(report_frame, wrap='word', height=20)
        visits_scrollbar = ttk.Scrollbar(report_frame, orient='vertical', 
                                       command=self.visits_report_text.yview)
        self.visits_report_text.configure(yscrollcommand=visits_scrollbar.set)
        
        self.visits_report_text.pack(side='left', fill='both', expand=True)
        visits_scrollbar.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = ttk.Frame(visits_frame)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=lambda: self.export_current_report('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Print Report", 
                  command=self.print_current_report).pack(side='left', padx=5)
    
    def create_appointment_reports_tab(self):
        """Create appointment reports tab"""
        appointments_frame = ttk.Frame(self.notebook)
        self.notebook.add(appointments_frame, text="Appointments")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(appointments_frame, text="Report Parameters", padding="10")
        params_frame.pack(fill='x', padx=5, pady=5)
        
        # Date range
        date_frame = ttk.Frame(params_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(side='left', padx=(0, 5))
        ttk.Label(date_frame, text="From:").pack(side='left', padx=(10, 5))
        self.appt_start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.appt_start_date_var, width=12).pack(side='left', padx=(0, 10))
        
        ttk.Label(date_frame, text="To:").pack(side='left', padx=(0, 5))
        self.appt_end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.appt_end_date_var, width=12).pack(side='left', padx=(0, 10))
        
        # Doctor filter
        doctor_frame = ttk.Frame(params_frame)
        doctor_frame.pack(fill='x', pady=5)
        
        ttk.Label(doctor_frame, text="Doctor Filter:").pack(side='left', padx=(0, 5))
        self.appt_doctor_var = tk.StringVar()
        from models.appointment import DoctorSchedule
        doctor_options = ['All Doctors'] + [doc['name'] for doc in DoctorSchedule.get_doctors()]
        doctor_combo = ttk.Combobox(doctor_frame, textvariable=self.appt_doctor_var,
                                  values=doctor_options, width=20, state='readonly')
        doctor_combo.set('All Doctors')
        doctor_combo.pack(side='left', padx=(0, 10))
        
        # Generate button
        ttk.Button(doctor_frame, text="Generate Report", 
                  command=self.generate_appointment_report).pack(side='left', padx=(10, 0))
        
        # Report display area
        report_frame = ttk.LabelFrame(appointments_frame, text="Report Results", padding="5")
        report_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Report text area
        self.appt_report_text = tk.Text(report_frame, wrap='word', height=20)
        appt_scrollbar = ttk.Scrollbar(report_frame, orient='vertical', 
                                     command=self.appt_report_text.yview)
        self.appt_report_text.configure(yscrollcommand=appt_scrollbar.set)
        
        self.appt_report_text.pack(side='left', fill='both', expand=True)
        appt_scrollbar.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = ttk.Frame(appointments_frame)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=lambda: self.export_current_report('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Print Report", 
                  command=self.print_current_report).pack(side='left', padx=5)
    
    def create_doctor_reports_tab(self):
        """Create doctor-specific reports tab"""
        doctor_frame = ttk.Frame(self.notebook)
        self.notebook.add(doctor_frame, text="Doctor Reports")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(doctor_frame, text="Report Parameters", padding="10")
        params_frame.pack(fill='x', padx=5, pady=5)
        
        # Doctor selection
        doctor_select_frame = ttk.Frame(params_frame)
        doctor_select_frame.pack(fill='x', pady=5)
        
        ttk.Label(doctor_select_frame, text="Select Doctor:").pack(side='left', padx=(0, 5))
        self.doctor_report_var = tk.StringVar()
        from models.appointment import DoctorSchedule
        doctor_options = [doc['name'] for doc in DoctorSchedule.get_doctors()]
        doctor_combo = ttk.Combobox(doctor_select_frame, textvariable=self.doctor_report_var,
                                  values=doctor_options, width=25, state='readonly')
        if doctor_options:
            doctor_combo.set(doctor_options[0])
        doctor_combo.pack(side='left', padx=(0, 10))
        
        # Date range
        date_frame = ttk.Frame(params_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(side='left', padx=(0, 5))
        ttk.Label(date_frame, text="From:").pack(side='left', padx=(10, 5))
        self.doctor_start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.doctor_start_date_var, width=12).pack(side='left', padx=(0, 10))
        
        ttk.Label(date_frame, text="To:").pack(side='left', padx=(0, 5))
        self.doctor_end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.doctor_end_date_var, width=12).pack(side='left', padx=(0, 10))
        
        # Generate button
        ttk.Button(date_frame, text="Generate Report", 
                  command=self.generate_doctor_report).pack(side='left', padx=(10, 0))
        
        # Report display area
        report_frame = ttk.LabelFrame(doctor_frame, text="Doctor Consultation Report", padding="5")
        report_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Report text area
        self.doctor_report_text = tk.Text(report_frame, wrap='word', height=20)
        doctor_scrollbar = ttk.Scrollbar(report_frame, orient='vertical', 
                                       command=self.doctor_report_text.yview)
        self.doctor_report_text.configure(yscrollcommand=doctor_scrollbar.set)
        
        self.doctor_report_text.pack(side='left', fill='both', expand=True)
        doctor_scrollbar.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = ttk.Frame(doctor_frame)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=lambda: self.export_current_report('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Print Report", 
                  command=self.print_current_report).pack(side='left', padx=5)
    
    def create_daily_summary_tab(self):
        """Create daily summary tab"""
        daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(daily_frame, text="Daily Summary")
        
        # Parameters frame
        params_frame = ttk.LabelFrame(daily_frame, text="Select Date", padding="10")
        params_frame.pack(fill='x', padx=5, pady=5)
        
        # Date selection
        date_frame = ttk.Frame(params_frame)
        date_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_frame, text="Report Date:").pack(side='left', padx=(0, 5))
        self.daily_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.daily_date_var, width=12).pack(side='left', padx=(0, 10))
        
        ttk.Button(date_frame, text="Today", 
                  command=lambda: self.daily_date_var.set(datetime.now().strftime("%Y-%m-%d"))).pack(side='left', padx=(5, 10))
        ttk.Button(date_frame, text="Yesterday", 
                  command=lambda: self.daily_date_var.set((datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))).pack(side='left', padx=(0, 10))
        
        # Generate button
        ttk.Button(date_frame, text="Generate Daily Summary", 
                  command=self.generate_daily_summary).pack(side='left', padx=(10, 0))
        
        # Report display area
        report_frame = ttk.LabelFrame(daily_frame, text="Daily Summary Report", padding="5")
        report_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Report text area
        self.daily_report_text = tk.Text(report_frame, wrap='word', height=20)
        daily_scrollbar = ttk.Scrollbar(report_frame, orient='vertical', 
                                      command=self.daily_report_text.yview)
        self.daily_report_text.configure(yscrollcommand=daily_scrollbar.set)
        
        self.daily_report_text.pack(side='left', fill='both', expand=True)
        daily_scrollbar.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = ttk.Frame(daily_frame)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=lambda: self.export_current_report('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Print Report", 
                  command=self.print_current_report).pack(side='left', padx=5)
    
    def create_export_tab(self):
        """Create export and backup tab"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Export & Backup")
        
        # Export options
        export_options_frame = ttk.LabelFrame(export_frame, text="Export Options", padding="10")
        export_options_frame.pack(fill='x', padx=5, pady=5)
        
        # Export all data
        all_data_frame = ttk.Frame(export_options_frame)
        all_data_frame.pack(fill='x', pady=5)
        
        ttk.Label(all_data_frame, text="Export All Hospital Data:").pack(side='left')
        ttk.Button(all_data_frame, text="Export to CSV", 
                  command=self.export_all_to_csv).pack(side='right', padx=(0, 5))
        
        # Export by type
        type_frame = ttk.LabelFrame(export_options_frame, text="Export by Data Type", padding="5")
        type_frame.pack(fill='x', pady=10)
        
        export_buttons_frame = ttk.Frame(type_frame)
        export_buttons_frame.pack()
        
        ttk.Button(export_buttons_frame, text="Export Patients", 
                  command=lambda: self.export_data_type('patients')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(export_buttons_frame, text="Export Appointments", 
                  command=lambda: self.export_data_type('appointments')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(export_buttons_frame, text="Export OPD Visits", 
                  command=lambda: self.export_data_type('opd_visits')).grid(row=0, column=2, padx=5, pady=5)
        
        # Backup options
        backup_frame = ttk.LabelFrame(export_frame, text="Backup & Restore", padding="10")
        backup_frame.pack(fill='x', padx=5, pady=5)
        
        backup_buttons_frame = ttk.Frame(backup_frame)
        backup_buttons_frame.pack()
        
        ttk.Button(backup_buttons_frame, text="Create Backup", 
                  command=self.create_backup).pack(side='left', padx=5)
        ttk.Button(backup_buttons_frame, text="Restore Backup", 
                  command=self.restore_backup).pack(side='left', padx=5)
        ttk.Button(backup_buttons_frame, text="View Backup Files", 
                  command=self.view_backup_files).pack(side='left', padx=5)
        
        # Export status
        status_frame = ttk.LabelFrame(export_frame, text="Export Status", padding="5")
        status_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.export_status_text = tk.Text(status_frame, wrap='word', height=10)
        status_scrollbar = ttk.Scrollbar(status_frame, orient='vertical', 
                                       command=self.export_status_text.yview)
        self.export_status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.export_status_text.pack(side='left', fill='both', expand=True)
        status_scrollbar.pack(side='right', fill='y')
        
        # Initial status message
        self.add_export_status("Export system ready. Select an export option above.")
    
    def load_dashboard_stats(self):
        """Load dashboard statistics"""
        try:
            stats = self.report_generator.get_report_summary_stats()
            
            self.total_patients_var.set(str(stats.get('total_patients', 0)))
            self.new_patients_var.set(str(stats.get('new_patients_this_month', 0)))
            self.appointments_today_var.set(str(stats.get('appointments_today', 0)))
            self.consultations_today_var.set(str(stats.get('consultations_today', 0)))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard statistics:\n{str(e)}")
    
    def load_recent_activity(self):
        """Load recent activity list"""
        try:
            self.activity_listbox.delete(0, tk.END)
            
            # Get recent appointments and visits
            appointments = self.data_manager.get_appointments()
            visits = self.data_manager.get_opd_visits()
            
            # Get today's activities
            today = datetime.now().strftime("%Y-%m-%d")
            today_appointments = [appt for appt in appointments if appt.appointment_date == today]
            today_visits = [visit for visit in visits if visit.is_today()]
            
            # Add to activity list
            for appt in today_appointments[:10]:  # Show last 10
                patient = self.data_manager.get_patient_by_id(appt.patient_id)
                patient_name = patient.name if patient else "Unknown"
                self.activity_listbox.insert(tk.END, 
                    f"Appointment: {patient_name} with {appt.doctor_name} at {appt.appointment_time}")
            
            for visit in today_visits[:10]:  # Show last 10
                patient = self.data_manager.get_patient_by_id(visit.patient_id)
                patient_name = patient.name if patient else "Unknown"
                try:
                    visit_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                except ValueError:
                    visit_time = "Unknown"
                self.activity_listbox.insert(tk.END, 
                    f"OPD Visit: {patient_name} with {visit.doctor_name} at {visit_time}")
            
            if not today_appointments and not today_visits:
                self.activity_listbox.insert(tk.END, "No activity recorded for today")
                
        except Exception as e:
            self.activity_listbox.insert(tk.END, f"Error loading activity: {str(e)}")
    
    def generate_patient_visits_report(self):
        """Generate patient visits report"""
        try:
            start_date = self.visits_start_date_var.get()
            end_date = self.visits_end_date_var.get()
            doctor_filter = self.visits_doctor_var.get()
            
            if doctor_filter == 'All Doctors':
                doctor_filter = ""
            
            # Show loading message
            self.visits_report_text.delete('1.0', tk.END)
            self.visits_report_text.insert('1.0', "Generating report... Please wait.")
            self.visits_report_text.update()
            
            # Generate report in background
            def generate_report():
                try:
                    report_data = self.report_generator.generate_patient_visits_report(
                        start_date, end_date, doctor_filter
                    )
                    
                    if "error" in report_data:
                        self.visits_report_text.delete('1.0', tk.END)
                        self.visits_report_text.insert('1.0', f"Error: {report_data['error']}")
                        return
                    
                    # Format and display report
                    formatted_report = self.format_patient_visits_report(report_data)
                    self.visits_report_text.delete('1.0', tk.END)
                    self.visits_report_text.insert('1.0', formatted_report)
                    
                    # Store for export
                    self.current_report_data = report_data
                    
                except Exception as e:
                    self.visits_report_text.delete('1.0', tk.END)
                    self.visits_report_text.insert('1.0', f"Error generating report: {str(e)}")
            
            # Run in background thread
            thread = threading.Thread(target=generate_report)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def format_patient_visits_report(self, report_data):
        """Format patient visits report for display"""
        formatted = f"""
{report_data['report_type']}
{'=' * 50}

Report Period: {report_data['date_range']}
Doctor Filter: {report_data['doctor_filter']}
Generated: {report_data['generated_at']}

SUMMARY STATISTICS
{'=' * 30}
Total Visits: {report_data['total_visits']}
Average Daily Visits: {report_data['average_daily_visits']}

DAILY BREAKDOWN
{'=' * 20}
"""
        
        for date, count in report_data['daily_breakdown'].items():
            formatted += f"{date}: {count} visits\n"
        
        formatted += f"""
DOCTOR BREAKDOWN
{'=' * 20}
"""
        
        for doctor, count in report_data['doctor_breakdown'].items():
            formatted += f"{doctor}: {count} visits\n"
        
        formatted += f"""
STATUS BREAKDOWN
{'=' * 20}
"""
        
        for status, count in report_data['status_breakdown'].items():
            formatted += f"{status}: {count} visits\n"
        
        if report_data['visits']:
            formatted += f"""
DETAILED VISIT LIST
{'=' * 25}
"""
            for visit in report_data['visits'][:20]:  # Show first 20
                formatted += f"Visit ID: {visit['visit_id']}\n"
                formatted += f"Patient: {visit['patient_id']}\n"
                formatted += f"Doctor: {visit['doctor_name']}\n"
                formatted += f"Date: {visit['visit_date']}\n"
                formatted += f"Status: {visit['status']}\n"
                formatted += "-" * 30 + "\n"
            
            if len(report_data['visits']) > 20:
                formatted += f"\n... and {len(report_data['visits']) - 20} more visits\n"
        
        return formatted
    
    def generate_appointment_report(self):
        """Generate appointment report"""
        try:
            start_date = self.appt_start_date_var.get()
            end_date = self.appt_end_date_var.get()
            doctor_filter = self.appt_doctor_var.get()
            
            if doctor_filter == 'All Doctors':
                doctor_filter = ""
            
            # Show loading message
            self.appt_report_text.delete('1.0', tk.END)
            self.appt_report_text.insert('1.0', "Generating report... Please wait.")
            self.appt_report_text.update()
            
            # Generate report
            def generate_report():
                try:
                    report_data = self.report_generator.generate_appointment_report(
                        start_date, end_date, doctor_filter
                    )
                    
                    if "error" in report_data:
                        self.appt_report_text.delete('1.0', tk.END)
                        self.appt_report_text.insert('1.0', f"Error: {report_data['error']}")
                        return
                    
                    # Format and display report
                    formatted_report = self.format_appointment_report(report_data)
                    self.appt_report_text.delete('1.0', tk.END)
                    self.appt_report_text.insert('1.0', formatted_report)
                    
                    # Store for export
                    self.current_report_data = report_data
                    
                except Exception as e:
                    self.appt_report_text.delete('1.0', tk.END)
                    self.appt_report_text.insert('1.0', f"Error generating report: {str(e)}")
            
            # Run in background thread
            thread = threading.Thread(target=generate_report)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def format_appointment_report(self, report_data):
        """Format appointment report for display"""
        formatted = f"""
{report_data['report_type']}
{'=' * 50}

Report Period: {report_data['date_range']}
Doctor Filter: {report_data['doctor_filter']}
Generated: {report_data['generated_at']}

SUMMARY STATISTICS
{'=' * 30}
Total Appointments: {report_data['total_appointments']}
Completion Rate: {report_data['completion_rate']}%

STATUS BREAKDOWN
{'=' * 20}
"""
        
        for status, count in report_data['status_breakdown'].items():
            formatted += f"{status}: {count} appointments\n"
        
        formatted += f"""
DOCTOR BREAKDOWN
{'=' * 20}
"""
        
        for doctor, count in report_data['doctor_breakdown'].items():
            formatted += f"{doctor}: {count} appointments\n"
        
        formatted += f"""
DEPARTMENT BREAKDOWN
{'=' * 25}
"""
        
        for dept, count in report_data['department_breakdown'].items():
            formatted += f"{dept}: {count} appointments\n"
        
        formatted += f"""
DAILY BREAKDOWN
{'=' * 20}
"""
        
        for date, count in report_data['daily_breakdown'].items():
            formatted += f"{date}: {count} appointments\n"
        
        return formatted
    
    def generate_doctor_report(self):
        """Generate doctor consultation report"""
        try:
            doctor_name = self.doctor_report_var.get()
            start_date = self.doctor_start_date_var.get()
            end_date = self.doctor_end_date_var.get()
            
            if not doctor_name:
                messagebox.showerror("Error", "Please select a doctor.")
                return
            
            # Show loading message
            self.doctor_report_text.delete('1.0', tk.END)
            self.doctor_report_text.insert('1.0', "Generating report... Please wait.")
            self.doctor_report_text.update()
            
            # Generate report
            def generate_report():
                try:
                    report_data = self.report_generator.generate_doctor_consultation_report(
                        doctor_name, start_date, end_date
                    )
                    
                    if "error" in report_data:
                        self.doctor_report_text.delete('1.0', tk.END)
                        self.doctor_report_text.insert('1.0', f"Error: {report_data['error']}")
                        return
                    
                    # Format and display report
                    formatted_report = self.format_doctor_report(report_data)
                    self.doctor_report_text.delete('1.0', tk.END)
                    self.doctor_report_text.insert('1.0', formatted_report)
                    
                    # Store for export
                    self.current_report_data = report_data
                    
                except Exception as e:
                    self.doctor_report_text.delete('1.0', tk.END)
                    self.doctor_report_text.insert('1.0', f"Error generating report: {str(e)}")
            
            # Run in background thread
            thread = threading.Thread(target=generate_report)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def format_doctor_report(self, report_data):
        """Format doctor consultation report for display"""
        formatted = f"""
{report_data['report_type']}
{'=' * 50}

Doctor: {report_data['doctor_name']}
Report Period: {report_data['date_range']}
Generated: {report_data['generated_at']}

SUMMARY STATISTICS
{'=' * 30}
Total Consultations: {report_data['total_consultations']}
Total Appointments: {report_data['total_appointments']}
Unique Patients: {report_data['unique_patients']}
Average Daily Consultations: {report_data['average_daily_consultations']}

DAILY CONSULTATION BREAKDOWN
{'=' * 35}
"""
        
        for date, count in report_data['daily_breakdown'].items():
            formatted += f"{date}: {count} consultations\n"
        
        if report_data['consultations']:
            formatted += f"""
RECENT CONSULTATIONS
{'=' * 25}
"""
            for consultation in report_data['consultations'][:10]:  # Show first 10
                formatted += f"Visit ID: {consultation['visit_id']}\n"
                formatted += f"Patient: {consultation['patient_id']}\n"
                formatted += f"Date: {consultation['visit_date']}\n"
                formatted += f"Status: {consultation['status']}\n"
                formatted += "-" * 30 + "\n"
        
        return formatted
    
    def generate_daily_summary(self):
        """Generate daily summary report"""
        try:
            report_date = self.daily_date_var.get()
            
            # Show loading message
            self.daily_report_text.delete('1.0', tk.END)
            self.daily_report_text.insert('1.0', "Generating report... Please wait.")
            self.daily_report_text.update()
            
            # Generate report
            def generate_report():
                try:
                    report_data = self.report_generator.generate_daily_summary_report(report_date)
                    
                    if "error" in report_data:
                        self.daily_report_text.delete('1.0', tk.END)
                        self.daily_report_text.insert('1.0', f"Error: {report_data['error']}")
                        return
                    
                    # Format and display report
                    formatted_report = self.format_daily_summary(report_data)
                    self.daily_report_text.delete('1.0', tk.END)
                    self.daily_report_text.insert('1.0', formatted_report)
                    
                    # Store for export
                    self.current_report_data = report_data
                    
                except Exception as e:
                    self.daily_report_text.delete('1.0', tk.END)
                    self.daily_report_text.insert('1.0', f"Error generating report: {str(e)}")
            
            # Run in background thread
            thread = threading.Thread(target=generate_report)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def format_daily_summary(self, report_data):
        """Format daily summary report for display"""
        formatted = f"""
{report_data['report_type']}
{'=' * 50}

Date: {report_data['date']}
Generated: {report_data['generated_at']}

DAILY OVERVIEW
{'=' * 20}
New Patient Registrations: {report_data['new_patients']}
Total Appointments: {report_data['total_appointments']}
Total Consultations: {report_data['total_consultations']}

APPOINTMENT STATUS
{'=' * 25}
"""
        
        for status, count in report_data['appointment_status'].items():
            formatted += f"{status}: {count}\n"
        
        formatted += f"""
CONSULTATION STATUS
{'=' * 25}
"""
        
        for status, count in report_data['consultation_status'].items():
            formatted += f"{status}: {count}\n"
        
        formatted += f"""
DOCTOR CONSULTATIONS
{'=' * 25}
"""
        
        for doctor, count in report_data['doctor_consultations'].items():
            formatted += f"{doctor}: {count} consultations\n"
        
        if report_data['new_patient_details']:
            formatted += f"""
NEW PATIENT REGISTRATIONS
{'=' * 35}
"""
            for patient in report_data['new_patient_details']:
                formatted += f"ID: {patient['patient_id']}, Name: {patient['name']}\n"
        
        return formatted
    
    def export_current_report(self, format_type):
        """Export current report to specified format"""
        if not self.current_report_data:
            messagebox.showwarning("Warning", "No report data to export. Please generate a report first.")
            return
        
        try:
            if format_type == 'csv':
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_type = self.current_report_data.get('report_type', 'report').replace(' ', '_').lower()
                filename = f"{report_type}_{timestamp}.csv"
                
                # Export to CSV
                success = self.report_generator.export_to_csv(self.current_report_data, filename)
                
                if success:
                    messagebox.showinfo("Export Success", f"Report exported to CSV successfully!\nFile: {filename}")
                else:
                    messagebox.showerror("Export Error", "Failed to export report to CSV.")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting report:\n{str(e)}")
    
    def print_current_report(self):
        """Print current report"""
        # Get the current active report text widget
        current_tab = self.notebook.index(self.notebook.select())
        
        text_widgets = [
            self.visits_report_text,
            self.appt_report_text, 
            self.doctor_report_text,
            self.daily_report_text
        ]
        
        if current_tab >= 1 and current_tab <= 4:
            text_widget = text_widgets[current_tab - 1]
            content = text_widget.get('1.0', tk.END)
            
            if content.strip():
                # Create print preview window
                self.show_print_preview(content)
            else:
                messagebox.showwarning("Warning", "No report content to print.")
        else:
            messagebox.showwarning("Warning", "Please select a report tab to print.")
    
    def show_print_preview(self, content):
        """Show print preview window"""
        preview_window = tk.Toplevel(self.parent)
        preview_window.title("Print Preview")
        preview_window.geometry("800x600")
        preview_window.transient(self.parent)
        
        # Preview content
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.pack(fill='both', expand=True)
        
        ttk.Label(preview_frame, text="Print Preview", style='Title.TLabel').pack(pady=(0, 10))
        
        # Text area
        preview_text = tk.Text(preview_frame, wrap='word', font=('Courier', 10))
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        preview_text.insert('1.0', content)
        preview_text.config(state='disabled')
        
        preview_text.pack(side='left', fill='both', expand=True)
        preview_scrollbar.pack(side='right', fill='y')
        
        # Print button
        ttk.Button(preview_frame, text="Close Preview", 
                  command=preview_window.destroy).pack(pady=10)
    
    def generate_today_summary(self):
        """Generate today's summary report"""
        self.daily_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.notebook.select(4)  # Switch to daily summary tab
        self.generate_daily_summary()
    
    def generate_weekly_report(self):
        """Generate weekly report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        self.visits_start_date_var.set(start_date.strftime("%Y-%m-%d"))
        self.visits_end_date_var.set(end_date.strftime("%Y-%m-%d"))
        self.notebook.select(1)  # Switch to patient visits tab
        self.generate_patient_visits_report()
    
    def generate_monthly_report(self):
        """Generate monthly report"""
        end_date = datetime.now()
        start_date = end_date.replace(day=1)
        
        self.visits_start_date_var.set(start_date.strftime("%Y-%m-%d"))
        self.visits_end_date_var.set(end_date.strftime("%Y-%m-%d"))
        self.notebook.select(1)  # Switch to patient visits tab
        self.generate_patient_visits_report()
    
    def export_all_data(self):
        """Export all hospital data"""
        self.notebook.select(5)  # Switch to export tab
        self.export_all_to_csv()
    
    def export_all_to_csv(self):
        """Export all data to CSV files"""
        try:
            # Ask for export directory
            export_dir = filedialog.askdirectory(title="Select Export Directory")
            if not export_dir:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export patients
            patients = self.data_manager.get_patients()
            if patients:
                import csv
                patients_file = os.path.join(export_dir, f"patients_{timestamp}.csv")
                with open(patients_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Contact', 'Address', 'Registration Date'])
                    for patient in patients:
                        writer.writerow([
                            patient.patient_id, patient.name, patient.age, patient.gender,
                            patient.phone, patient.contact, patient.address, patient.registration_date
                        ])
                self.add_export_status(f"Exported {len(patients)} patients to {os.path.basename(patients_file)}")
            
            # Export appointments
            appointments = self.data_manager.get_appointments()
            if appointments:
                appt_file = os.path.join(export_dir, f"appointments_{timestamp}.csv")
                with open(appt_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Appointment ID', 'Patient ID', 'Doctor', 'Department', 'Date', 'Time', 'Status', 'Notes'])
                    for appt in appointments:
                        writer.writerow([
                            appt.appointment_id, appt.patient_id, appt.doctor_name, appt.department,
                            appt.appointment_date, appt.appointment_time, appt.status, appt.notes
                        ])
                self.add_export_status(f"Exported {len(appointments)} appointments to {os.path.basename(appt_file)}")
            
            # Export OPD visits
            visits = self.data_manager.get_opd_visits()
            if visits:
                visits_file = os.path.join(export_dir, f"opd_visits_{timestamp}.csv")
                with open(visits_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Visit ID', 'Patient ID', 'Doctor', 'Date', 'Symptoms', 'Diagnosis', 'Prescription', 'Status'])
                    for visit in visits:
                        writer.writerow([
                            visit.visit_id, visit.patient_id, visit.doctor_name, visit.visit_date,
                            visit.symptoms, visit.diagnosis, visit.prescription, visit.status
                        ])
                self.add_export_status(f"Exported {len(visits)} OPD visits to {os.path.basename(visits_file)}")
            
            messagebox.showinfo("Export Complete", f"All data exported successfully to {export_dir}")
            
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            self.add_export_status(error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def export_data_type(self, data_type):
        """Export specific data type"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_{timestamp}.csv"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=filename
            )
            
            if not file_path:
                return
            
            import csv
            
            if data_type == 'patients':
                patients = self.data_manager.get_patients()
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Patient ID', 'Name', 'Age', 'Gender', 'Phone', 'Contact', 'Address', 'Registration Date'])
                    for patient in patients:
                        writer.writerow([
                            patient.patient_id, patient.name, patient.age, patient.gender,
                            patient.phone, patient.contact, patient.address, patient.registration_date
                        ])
                self.add_export_status(f"Exported {len(patients)} patients to {os.path.basename(file_path)}")
            
            elif data_type == 'appointments':
                appointments = self.data_manager.get_appointments()
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Appointment ID', 'Patient ID', 'Doctor', 'Department', 'Date', 'Time', 'Status', 'Notes'])
                    for appt in appointments:
                        writer.writerow([
                            appt.appointment_id, appt.patient_id, appt.doctor_name, appt.department,
                            appt.appointment_date, appt.appointment_time, appt.status, appt.notes
                        ])
                self.add_export_status(f"Exported {len(appointments)} appointments to {os.path.basename(file_path)}")
            
            elif data_type == 'opd_visits':
                visits = self.data_manager.get_opd_visits()
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Visit ID', 'Patient ID', 'Doctor', 'Date', 'Symptoms', 'Diagnosis', 'Prescription', 'Status'])
                    for visit in visits:
                        writer.writerow([
                            visit.visit_id, visit.patient_id, visit.doctor_name, visit.visit_date,
                            visit.symptoms, visit.diagnosis, visit.prescription, visit.status
                        ])
                self.add_export_status(f"Exported {len(visits)} OPD visits to {os.path.basename(file_path)}")
            
            messagebox.showinfo("Export Complete", f"Data exported successfully to {os.path.basename(file_path)}")
            
        except Exception as e:
            error_msg = f"Error exporting {data_type}: {str(e)}"
            self.add_export_status(error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def create_backup(self):
        """Create data backup"""
        try:
            success = self.data_manager.create_backup()
            if success:
                self.add_export_status("Backup created successfully")
                messagebox.showinfo("Backup", "Backup created successfully!")
            else:
                self.add_export_status("Failed to create backup")
                messagebox.showerror("Backup", "Failed to create backup!")
        except Exception as e:
            error_msg = f"Error creating backup: {str(e)}"
            self.add_export_status(error_msg)
            messagebox.showerror("Backup Error", error_msg)
    
    def restore_backup(self):
        """Restore from backup"""
        try:
            backup_files = self.data_manager.get_backup_files()
            
            if not backup_files:
                messagebox.showinfo("Restore", "No backup files found!")
                return
            
            file_path = filedialog.askopenfilename(
                title="Select Backup File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=os.path.dirname(backup_files[0]) if backup_files else None
            )
            
            if file_path:
                result = messagebox.askyesno("Restore Backup", 
                                           "This will replace all current data. Are you sure?")
                if result:
                    success = self.data_manager.restore_backup(file_path)
                    if success:
                        self.add_export_status(f"Data restored from {os.path.basename(file_path)}")
                        messagebox.showinfo("Restore", "Data restored successfully!")
                        self.load_dashboard_stats()  # Refresh dashboard
                    else:
                        self.add_export_status("Failed to restore backup")
                        messagebox.showerror("Restore", "Failed to restore backup!")
        except Exception as e:
            error_msg = f"Error restoring backup: {str(e)}"
            self.add_export_status(error_msg)
            messagebox.showerror("Restore Error", error_msg)
    
    def view_backup_files(self):
        """View available backup files"""
        try:
            backup_files = self.data_manager.get_backup_files()
            
            if not backup_files:
                messagebox.showinfo("Backup Files", "No backup files found.")
                return
            
            # Create backup files window
            backup_window = tk.Toplevel(self.parent)
            backup_window.title("Available Backup Files")
            backup_window.geometry("600x400")
            backup_window.transient(self.parent)
            
            main_frame = ttk.Frame(backup_window, padding="10")
            main_frame.pack(fill='both', expand=True)
            
            ttk.Label(main_frame, text="Available Backup Files", style='Title.TLabel').pack(pady=(0, 10))
            
            # Backup files listbox
            files_frame = ttk.Frame(main_frame)
            files_frame.pack(fill='both', expand=True)
            
            backup_listbox = tk.Listbox(files_frame)
            backup_scrollbar = ttk.Scrollbar(files_frame, orient='vertical', command=backup_listbox.yview)
            backup_listbox.configure(yscrollcommand=backup_scrollbar.set)
            
            for backup_file in backup_files:
                filename = os.path.basename(backup_file)
                file_size = os.path.getsize(backup_file) / 1024  # KB
                mod_time = datetime.fromtimestamp(os.path.getmtime(backup_file)).strftime("%Y-%m-%d %H:%M")
                backup_listbox.insert(tk.END, f"{filename} ({file_size:.1f} KB) - {mod_time}")
            
            backup_listbox.pack(side='left', fill='both', expand=True)
            backup_scrollbar.pack(side='right', fill='y')
            
            ttk.Button(main_frame, text="Close", command=backup_window.destroy).pack(pady=10)
            
        except Exception as e:
            error_msg = f"Error viewing backup files: {str(e)}"
            self.add_export_status(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def add_export_status(self, message):
        """Add message to export status"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.export_status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.export_status_text.see(tk.END)
        self.export_status_text.update()
    
    def refresh(self):
        """Refresh all report data"""
        self.load_dashboard_stats()
        self.load_recent_activity()
        self.current_report_data = None
