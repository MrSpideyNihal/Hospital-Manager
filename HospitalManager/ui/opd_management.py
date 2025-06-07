"""
OPD Management UI - Handles outpatient department operations and visit management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.opd import OPDVisit, OPDQueue
from models.appointment import DoctorSchedule

class OPDManagementFrame:
    """OPD management interface"""
    
    def __init__(self, parent, data_manager, announcement_system):
        """Initialize OPD management frame"""
        self.parent = parent
        self.data_manager = data_manager
        self.announcement_system = announcement_system
        self.current_visit = None
        self.opd_queue = OPDQueue()
        
        self.create_widgets()
        self.refresh_visits()
        self.refresh_queue()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(main_frame, text="OPD Management", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_quick_checkin_tab()
        self.create_visit_form_tab()
        self.create_visit_list_tab()
        self.create_queue_management_tab()
    
    def create_quick_checkin_tab(self):
        """Create quick check-in tab"""
        checkin_frame = ttk.Frame(self.notebook)
        self.notebook.add(checkin_frame, text="Quick Check-in")
        
        # Check-in container
        checkin_container = ttk.LabelFrame(checkin_frame, text="Patient Check-in", padding="10")
        checkin_container.pack(fill='x', padx=5, pady=5)
        
        # Patient search
        search_frame = ttk.Frame(checkin_container)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search Patient:").pack(side='left', padx=(0, 5))
        self.checkin_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.checkin_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.search_patients_for_checkin)
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_patients_for_checkin).pack(side='left', padx=(5, 0))
        
        # Patient selection
        self.checkin_patient_var = tk.StringVar()
        self.checkin_patient_combo = ttk.Combobox(checkin_container, textvariable=self.checkin_patient_var,
                                                width=50, state='readonly')
        self.checkin_patient_combo.pack(fill='x', pady=5)
        
        # Doctor selection for quick check-in
        doctor_frame = ttk.Frame(checkin_container)
        doctor_frame.pack(fill='x', pady=5)
        
        ttk.Label(doctor_frame, text="Doctor:").pack(side='left', padx=(0, 5))
        self.checkin_doctor_var = tk.StringVar()
        doctor_combo = ttk.Combobox(doctor_frame, textvariable=self.checkin_doctor_var,
                                  values=[doc['name'] for doc in DoctorSchedule.get_doctors()],
                                  width=25, state='readonly')
        doctor_combo.pack(side='left', padx=(0, 10))
        
        # Check-in button
        ttk.Button(doctor_frame, text="Check-in Patient", 
                  command=self.quick_checkin_patient).pack(side='left', padx=(10, 0))
        
        # Today's check-ins
        today_frame = ttk.LabelFrame(checkin_frame, text="Today's Check-ins", padding="5")
        today_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Today's visits treeview
        today_columns = ('Time', 'Patient', 'Doctor', 'Status', 'Queue Position')
        self.today_tree = ttk.Treeview(today_frame, columns=today_columns, show='headings', height=10)
        
        for col in today_columns:
            self.today_tree.heading(col, text=col)
            self.today_tree.column(col, width=100)
        
        # Scrollbar for today's visits
        today_scrollbar = ttk.Scrollbar(today_frame, orient='vertical', command=self.today_tree.yview)
        self.today_tree.configure(yscrollcommand=today_scrollbar.set)
        
        self.today_tree.pack(side='left', fill='both', expand=True)
        today_scrollbar.pack(side='right', fill='y')
        
        # Refresh today's visits
        self.refresh_todays_visits()
    
    def create_visit_form_tab(self):
        """Create visit form tab"""
        form_frame = ttk.Frame(self.notebook)
        self.notebook.add(form_frame, text="Visit Form")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="OPD Visit Details", padding="10")
        form_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Visit ID (read-only)
        ttk.Label(form_container, text="Visit ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.visit_id_var = tk.StringVar()
        visit_id_entry = ttk.Entry(form_container, textvariable=self.visit_id_var, 
                                 state='readonly', width=20)
        visit_id_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Patient selection
        ttk.Label(form_container, text="Patient:*").grid(row=1, column=0, sticky='w', pady=5)
        patient_frame = ttk.Frame(form_container)
        patient_frame.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        self.form_patient_var = tk.StringVar()
        self.form_patient_combo = ttk.Combobox(patient_frame, textvariable=self.form_patient_var, 
                                             width=25, state='readonly')
        self.form_patient_combo.pack(side='left')
        
        ttk.Button(patient_frame, text="Refresh", 
                  command=self.refresh_form_patient_list).pack(side='left', padx=(5, 0))
        
        # Doctor selection
        ttk.Label(form_container, text="Doctor:*").grid(row=2, column=0, sticky='w', pady=5)
        self.form_doctor_var = tk.StringVar()
        form_doctor_combo = ttk.Combobox(form_container, textvariable=self.form_doctor_var,
                                       values=[doc['name'] for doc in DoctorSchedule.get_doctors()],
                                       width=25, state='readonly')
        form_doctor_combo.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Visit date and time (auto-filled)
        ttk.Label(form_container, text="Visit Date:").grid(row=3, column=0, sticky='w', pady=5)
        self.visit_date_var = tk.StringVar()
        visit_date_entry = ttk.Entry(form_container, textvariable=self.visit_date_var, 
                                   state='readonly', width=25)
        visit_date_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Vital signs frame
        vital_frame = ttk.LabelFrame(form_container, text="Vital Signs", padding="5")
        vital_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10, padx=(0, 0))
        
        # Blood pressure
        ttk.Label(vital_frame, text="Blood Pressure:").grid(row=0, column=0, sticky='w', pady=2)
        self.bp_var = tk.StringVar()
        ttk.Entry(vital_frame, textvariable=self.bp_var, width=15).grid(row=0, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Temperature
        ttk.Label(vital_frame, text="Temperature:").grid(row=0, column=2, sticky='w', pady=2, padx=(10, 0))
        self.temp_var = tk.StringVar()
        ttk.Entry(vital_frame, textvariable=self.temp_var, width=10).grid(row=0, column=3, sticky='w', pady=2, padx=(5, 0))
        
        # Pulse
        ttk.Label(vital_frame, text="Pulse:").grid(row=1, column=0, sticky='w', pady=2)
        self.pulse_var = tk.StringVar()
        ttk.Entry(vital_frame, textvariable=self.pulse_var, width=10).grid(row=1, column=1, sticky='w', pady=2, padx=(5, 0))
        
        # Weight
        ttk.Label(vital_frame, text="Weight:").grid(row=1, column=2, sticky='w', pady=2, padx=(10, 0))
        self.weight_var = tk.StringVar()
        ttk.Entry(vital_frame, textvariable=self.weight_var, width=10).grid(row=1, column=3, sticky='w', pady=2, padx=(5, 0))
        
        # Symptoms
        ttk.Label(form_container, text="Symptoms:*").grid(row=5, column=0, sticky='nw', pady=5)
        self.symptoms_text = tk.Text(form_container, width=50, height=4)
        self.symptoms_text.grid(row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Diagnosis
        ttk.Label(form_container, text="Diagnosis:").grid(row=6, column=0, sticky='nw', pady=5)
        self.diagnosis_text = tk.Text(form_container, width=50, height=4)
        self.diagnosis_text.grid(row=6, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Prescription
        ttk.Label(form_container, text="Prescription:").grid(row=7, column=0, sticky='nw', pady=5)
        self.prescription_text = tk.Text(form_container, width=50, height=4)
        self.prescription_text.grid(row=7, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Lab tests
        ttk.Label(form_container, text="Lab Tests:").grid(row=8, column=0, sticky='nw', pady=5)
        self.lab_tests_text = tk.Text(form_container, width=50, height=3)
        self.lab_tests_text.grid(row=8, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Follow-up date
        ttk.Label(form_container, text="Follow-up Date:").grid(row=9, column=0, sticky='w', pady=5)
        self.followup_date_var = tk.StringVar()
        followup_entry = ttk.Entry(form_container, textvariable=self.followup_date_var, width=15)
        followup_entry.grid(row=9, column=1, sticky='w', pady=5, padx=(10, 0))
        ttk.Label(form_container, text="(YYYY-MM-DD, optional)").grid(row=9, column=1, sticky='w', pady=5, padx=(130, 0))
        
        # Status
        ttk.Label(form_container, text="Status:").grid(row=10, column=0, sticky='w', pady=5)
        self.visit_status_var = tk.StringVar()
        status_combo = ttk.Combobox(form_container, textvariable=self.visit_status_var,
                                  values=['In Progress', 'Completed', 'Follow-up Required'],
                                  width=20, state='readonly')
        status_combo.set('In Progress')
        status_combo.grid(row=10, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(form_container, text="Notes:").grid(row=11, column=0, sticky='nw', pady=5)
        self.visit_notes_text = tk.Text(form_container, width=50, height=3)
        self.visit_notes_text.grid(row=11, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Button frame
        button_frame = ttk.Frame(form_container)
        button_frame.grid(row=12, column=0, columnspan=2, pady=20)
        
        self.save_visit_button = ttk.Button(button_frame, text="Save Visit", 
                                          command=self.save_visit)
        self.save_visit_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Complete Visit", 
                  command=self.complete_visit).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_visit_form).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_visit_edit).pack(side='left', padx=5)
        
        # Required fields note
        ttk.Label(form_container, text="* Required fields", 
                 foreground='red').grid(row=13, column=0, columnspan=2, pady=5)
        
        # Initialize form
        self.refresh_form_patient_list()
        self.clear_visit_form()
    
    def create_visit_list_tab(self):
        """Create visit list tab"""
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Visit List")
        
        # Control frame
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="New Visit", 
                  command=self.new_visit).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Edit Visit", 
                  command=self.edit_visit).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Complete Visit", 
                  command=self.complete_selected_visit).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="View Summary", 
                  command=self.view_visit_summary).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_visits).pack(side='left', padx=(0, 5))
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left', padx=(0, 5))
        
        # Date filter
        ttk.Label(filter_frame, text="Date:").pack(side='left', padx=(0, 5))
        self.list_date_filter_var = tk.StringVar()
        date_filter_entry = ttk.Entry(filter_frame, textvariable=self.list_date_filter_var, width=12)
        date_filter_entry.pack(side='left', padx=(0, 10))
        date_filter_entry.bind('<KeyRelease>', self.filter_visits)
        
        # Doctor filter
        ttk.Label(filter_frame, text="Doctor:").pack(side='left', padx=(0, 5))
        self.list_doctor_filter_var = tk.StringVar()
        doctor_filter = ttk.Combobox(filter_frame, textvariable=self.list_doctor_filter_var,
                                   values=['All'] + [doc['name'] for doc in DoctorSchedule.get_doctors()],
                                   width=15, state='readonly')
        doctor_filter.set('All')
        doctor_filter.pack(side='left', padx=(0, 10))
        doctor_filter.bind('<<ComboboxSelected>>', self.filter_visits)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=(0, 5))
        self.list_status_filter_var = tk.StringVar()
        status_filter = ttk.Combobox(filter_frame, textvariable=self.list_status_filter_var,
                                   values=['All', 'In Progress', 'Completed', 'Follow-up Required'],
                                   width=15, state='readonly')
        status_filter.set('All')
        status_filter.pack(side='left', padx=(0, 10))
        status_filter.bind('<<ComboboxSelected>>', self.filter_visits)
        
        ttk.Button(filter_frame, text="Clear Filters", 
                  command=self.clear_visit_filters).pack(side='left', padx=(10, 0))
        
        # Visit list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('Visit ID', 'Patient', 'Doctor', 'Date', 'Symptoms', 'Diagnosis', 'Status')
        self.visit_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.visit_tree.heading(col, text=col)
        
        # Column widths
        self.visit_tree.column('Visit ID', width=120)
        self.visit_tree.column('Patient', width=120)
        self.visit_tree.column('Doctor', width=120)
        self.visit_tree.column('Date', width=100)
        self.visit_tree.column('Symptoms', width=150)
        self.visit_tree.column('Diagnosis', width=150)
        self.visit_tree.column('Status', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.visit_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient='horizontal', command=self.visit_tree.xview)
        self.visit_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.visit_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.visit_tree.bind('<Double-1>', lambda e: self.edit_visit())
    
    def create_queue_management_tab(self):
        """Create queue management tab"""
        queue_frame = ttk.Frame(self.notebook)
        self.notebook.add(queue_frame, text="Queue Management")
        
        # Queue status frame
        status_frame = ttk.LabelFrame(queue_frame, text="Queue Status", padding="10")
        status_frame.pack(fill='x', padx=5, pady=5)
        
        self.queue_status_label = ttk.Label(status_frame, text="Queue: 0 patients waiting")
        self.queue_status_label.pack()
        
        # Queue controls
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(control_frame, text="Call Next Patient", 
                  command=self.call_next_patient).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Refresh Queue", 
                  command=self.refresh_queue).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Clear Queue", 
                  command=self.clear_queue).pack(side='left', padx=(0, 5))
        
        # Current queue
        queue_list_frame = ttk.LabelFrame(queue_frame, text="Current Queue", padding="5")
        queue_list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Queue treeview
        queue_columns = ('Position', 'Patient', 'Check-in Time', 'Doctor', 'Status')
        self.queue_tree = ttk.Treeview(queue_list_frame, columns=queue_columns, show='headings', height=10)
        
        for col in queue_columns:
            self.queue_tree.heading(col, text=col)
            self.queue_tree.column(col, width=100)
        
        # Queue scrollbar
        queue_scrollbar = ttk.Scrollbar(queue_list_frame, orient='vertical', command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)
        
        self.queue_tree.pack(side='left', fill='both', expand=True)
        queue_scrollbar.pack(side='right', fill='y')
        
        # Completed patients today
        completed_frame = ttk.LabelFrame(queue_frame, text="Completed Today", padding="5")
        completed_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Completed patients list
        self.completed_listbox = tk.Listbox(completed_frame, height=8)
        completed_scrollbar = ttk.Scrollbar(completed_frame, orient='vertical', command=self.completed_listbox.yview)
        self.completed_listbox.configure(yscrollcommand=completed_scrollbar.set)
        
        self.completed_listbox.pack(side='left', fill='both', expand=True)
        completed_scrollbar.pack(side='right', fill='y')
        
        # Manual announcement controls
        announcement_frame = ttk.Frame(completed_frame)
        announcement_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(announcement_frame, text="Manual Announcement", 
                  command=self.manual_announcement).pack(side='left', padx=(0, 5))
        ttk.Button(announcement_frame, text="Test Announcement", 
                  command=self.test_announcement).pack(side='left')
        
        # Refresh queue initially
        self.refresh_queue()
    
    def search_patients_for_checkin(self, event=None):
        """Search patients for check-in"""
        query = self.checkin_search_var.get().strip()
        if len(query) < 2:  # Start searching after 2 characters
            return
        
        patients = self.data_manager.search_patients(query)
        patient_options = [f"{p.patient_id} - {p.name} ({p.phone})" for p in patients]
        self.checkin_patient_combo.config(values=patient_options)
    
    def quick_checkin_patient(self):
        """Quick check-in for existing patient"""
        patient_selection = self.checkin_patient_var.get().strip()
        doctor_name = self.checkin_doctor_var.get().strip()
        
        if not patient_selection:
            messagebox.showerror("Error", "Please select a patient.")
            return
        
        if not doctor_name:
            messagebox.showerror("Error", "Please select a doctor.")
            return
        
        try:
            # Extract patient ID
            patient_id = patient_selection.split(' - ')[0]
            
            # Check if patient already has an active visit today
            today_visits = self.data_manager.get_todays_opd_visits()
            active_visit = next((visit for visit in today_visits 
                               if visit.patient_id == patient_id and visit.status == 'In Progress'), None)
            
            if active_visit:
                messagebox.showwarning("Warning", "Patient already has an active visit today.")
                return
            
            # Create new OPD visit
            visit = OPDVisit(
                patient_id=patient_id,
                doctor_name=doctor_name,
                symptoms="Walk-in consultation",
                status="In Progress"
            )
            
            # Save visit
            success = self.data_manager.save_opd_visit(visit)
            if success:
                # Add to queue
                patient = self.data_manager.get_patient_by_id(patient_id)
                if patient:
                    self.opd_queue.add_patient(patient_id)
                
                messagebox.showinfo("Success", f"Patient checked-in successfully!\nVisit ID: {visit.visit_id}")
                
                # Clear form
                self.checkin_patient_var.set('')
                self.checkin_doctor_var.set('')
                self.checkin_search_var.set('')
                
                # Refresh displays
                self.refresh_todays_visits()
                self.refresh_queue()
                self.refresh_visits()
            else:
                messagebox.showerror("Error", "Failed to check-in patient.")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during check-in:\n{str(e)}")
    
    def refresh_todays_visits(self):
        """Refresh today's visits display"""
        # Clear existing items
        for item in self.today_tree.get_children():
            self.today_tree.delete(item)
        
        # Get today's visits
        today_visits = self.data_manager.get_todays_opd_visits()
        
        for visit in today_visits:
            # Get patient info
            patient = self.data_manager.get_patient_by_id(visit.patient_id)
            patient_name = patient.name if patient else "Unknown Patient"
            
            # Get queue position
            queue_position = self.opd_queue.get_queue_position(visit.patient_id)
            position_text = str(queue_position) if queue_position > 0 else "-"
            
            # Format time
            try:
                visit_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                time_str = visit_time.strftime("%H:%M")
            except ValueError:
                time_str = "Unknown"
            
            self.today_tree.insert('', 'end', values=(
                time_str,
                patient_name,
                visit.doctor_name,
                visit.status,
                position_text
            ))
    
    def refresh_form_patient_list(self):
        """Refresh patient list in form"""
        patients = self.data_manager.get_patients()
        patient_options = [f"{p.patient_id} - {p.name}" for p in patients]
        self.form_patient_combo.config(values=patient_options)
    
    def new_visit(self):
        """Start creating a new visit"""
        self.current_visit = None
        self.clear_visit_form()
        self.notebook.select(1)  # Switch to form tab
        
        # Generate new visit ID
        new_visit = OPDVisit()
        self.visit_id_var.set(new_visit.visit_id)
        self.visit_date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def clear_visit_form(self):
        """Clear the visit form"""
        self.visit_id_var.set('')
        self.form_patient_var.set('')
        self.form_doctor_var.set('')
        self.visit_date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.bp_var.set('')
        self.temp_var.set('')
        self.pulse_var.set('')
        self.weight_var.set('')
        self.symptoms_text.delete('1.0', tk.END)
        self.diagnosis_text.delete('1.0', tk.END)
        self.prescription_text.delete('1.0', tk.END)
        self.lab_tests_text.delete('1.0', tk.END)
        self.followup_date_var.set('')
        self.visit_status_var.set('In Progress')
        self.visit_notes_text.delete('1.0', tk.END)
        self.current_visit = None
    
    def save_visit(self):
        """Save visit data"""
        try:
            # Get form data
            visit_id = self.visit_id_var.get().strip()
            patient_selection = self.form_patient_var.get().strip()
            doctor_name = self.form_doctor_var.get().strip()
            symptoms = self.symptoms_text.get('1.0', tk.END).strip()
            diagnosis = self.diagnosis_text.get('1.0', tk.END).strip()
            prescription = self.prescription_text.get('1.0', tk.END).strip()
            lab_tests = self.lab_tests_text.get('1.0', tk.END).strip()
            followup_date = self.followup_date_var.get().strip()
            status = self.visit_status_var.get().strip()
            notes = self.visit_notes_text.get('1.0', tk.END).strip()
            
            # Extract patient ID
            if not patient_selection:
                messagebox.showerror("Validation Error", "Please select a patient.")
                return
            
            patient_id = patient_selection.split(' - ')[0]
            
            # Create or update visit
            if self.current_visit:
                # Update existing visit
                visit = self.current_visit
                visit.patient_id = patient_id
                visit.doctor_name = doctor_name
                visit.symptoms = symptoms
                visit.diagnosis = diagnosis
                visit.prescription = prescription
                visit.lab_tests = lab_tests
                visit.follow_up_date = followup_date
                visit.status = status
                visit.notes = notes
            else:
                # Create new visit
                visit = OPDVisit(
                    visit_id=visit_id,
                    patient_id=patient_id,
                    doctor_name=doctor_name,
                    symptoms=symptoms,
                    diagnosis=diagnosis,
                    prescription=prescription,
                    lab_tests=lab_tests,
                    follow_up_date=followup_date,
                    status=status,
                    notes=notes
                )
            
            # Set vital signs
            visit.set_vital_signs(
                blood_pressure=self.bp_var.get().strip(),
                temperature=self.temp_var.get().strip(),
                pulse=self.pulse_var.get().strip(),
                weight=self.weight_var.get().strip()
            )
            
            # Validate visit
            is_valid, error_message = visit.validate()
            if not is_valid:
                messagebox.showerror("Validation Error", error_message)
                return
            
            # Save visit
            success = self.data_manager.save_opd_visit(visit)
            if success:
                messagebox.showinfo("Success", "Visit saved successfully!")
                self.clear_visit_form()
                self.refresh_visits()
                self.refresh_todays_visits()
                self.notebook.select(2)  # Switch to list tab
            else:
                messagebox.showerror("Error", "Failed to save visit.")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving visit:\n{str(e)}")
    
    def complete_visit(self):
        """Complete current visit and trigger announcement"""
        if not self.current_visit and not self.visit_id_var.get():
            messagebox.showwarning("Warning", "No visit to complete.")
            return
        
        # Save current changes first
        self.save_visit()
        
        # Get visit
        visit_id = self.visit_id_var.get()
        visit = self.data_manager.get_opd_visit_by_id(visit_id)
        
        if visit:
            # Mark as completed
            visit.mark_completed()
            success = self.data_manager.save_opd_visit(visit)
            
            if success:
                # Get patient for announcement
                patient = self.data_manager.get_patient_by_id(visit.patient_id)
                
                if patient:
                    # Add to completed queue for announcements
                    self.opd_queue.mark_patient_completed(patient.name)
                    
                    # Remove from active queue
                    self.opd_queue.remove_patient(visit.patient_id)
                    
                    # Trigger announcement
                    if self.announcement_system:
                        self.announcement_system.add_manual_announcement(
                            patient.name,
                            f"Patient {patient.name}, your consultation is complete. Please collect your prescription from the front desk."
                        )
                
                messagebox.showinfo("Success", "Visit completed successfully!")
                
                # Refresh displays
                self.refresh_visits()
                self.refresh_todays_visits()
                self.refresh_queue()
                self.clear_visit_form()
            else:
                messagebox.showerror("Error", "Failed to complete visit.")
        else:
            messagebox.showerror("Error", "Visit not found.")
    
    def cancel_visit_edit(self):
        """Cancel editing and return to list"""
        self.clear_visit_form()
        self.notebook.select(2)
    
    def edit_visit(self):
        """Edit selected visit"""
        selected = self.visit_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a visit to edit.")
            return
        
        # Get visit ID from selection
        visit_id = self.visit_tree.item(selected[0])['values'][0]
        visit = self.data_manager.get_opd_visit_by_id(visit_id)
        
        if visit:
            self.current_visit = visit
            self.load_visit_to_form(visit)
            self.notebook.select(1)  # Switch to form tab
        else:
            messagebox.showerror("Error", "Visit not found.")
    
    def load_visit_to_form(self, visit):
        """Load visit data into form"""
        self.visit_id_var.set(visit.visit_id)
        self.visit_date_var.set(visit.visit_date)
        
        # Set patient
        patient = self.data_manager.get_patient_by_id(visit.patient_id)
        if patient:
            patient_text = f"{patient.patient_id} - {patient.name}"
            self.form_patient_var.set(patient_text)
        
        self.form_doctor_var.set(visit.doctor_name)
        
        # Set vital signs
        if visit.vital_signs:
            self.bp_var.set(visit.vital_signs.get('blood_pressure', ''))
            self.temp_var.set(visit.vital_signs.get('temperature', ''))
            self.pulse_var.set(visit.vital_signs.get('pulse', ''))
            self.weight_var.set(visit.vital_signs.get('weight', ''))
        
        # Set text fields
        self.symptoms_text.delete('1.0', tk.END)
        self.symptoms_text.insert('1.0', visit.symptoms)
        
        self.diagnosis_text.delete('1.0', tk.END)
        self.diagnosis_text.insert('1.0', visit.diagnosis)
        
        self.prescription_text.delete('1.0', tk.END)
        self.prescription_text.insert('1.0', visit.prescription)
        
        self.lab_tests_text.delete('1.0', tk.END)
        self.lab_tests_text.insert('1.0', visit.lab_tests)
        
        self.followup_date_var.set(visit.follow_up_date)
        self.visit_status_var.set(visit.status)
        
        self.visit_notes_text.delete('1.0', tk.END)
        self.visit_notes_text.insert('1.0', visit.notes)
    
    def complete_selected_visit(self):
        """Complete selected visit from list"""
        selected = self.visit_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a visit to complete.")
            return
        
        visit_id = self.visit_tree.item(selected[0])['values'][0]
        visit = self.data_manager.get_opd_visit_by_id(visit_id)
        
        if not visit:
            messagebox.showerror("Error", "Visit not found.")
            return
        
        # Confirm completion
        patient = self.data_manager.get_patient_by_id(visit.patient_id)
        patient_name = patient.name if patient else "Unknown Patient"
        
        result = messagebox.askyesno("Confirm Completion", 
                                   f"Mark visit for {patient_name} as completed?")
        
        if result:
            visit.mark_completed()
            success = self.data_manager.save_opd_visit(visit)
            
            if success:
                # Trigger announcement
                if patient and self.announcement_system:
                    self.opd_queue.mark_patient_completed(patient.name)
                    self.opd_queue.remove_patient(visit.patient_id)
                    
                    self.announcement_system.add_manual_announcement(
                        patient.name,
                        f"Patient {patient.name}, your consultation is complete. Please collect your prescription from the front desk."
                    )
                
                messagebox.showinfo("Success", "Visit completed successfully!")
                self.refresh_visits()
                self.refresh_todays_visits()
                self.refresh_queue()
            else:
                messagebox.showerror("Error", "Failed to complete visit.")
    
    def view_visit_summary(self):
        """View visit summary"""
        selected = self.visit_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a visit to view summary.")
            return
        
        visit_id = self.visit_tree.item(selected[0])['values'][0]
        visit = self.data_manager.get_opd_visit_by_id(visit_id)
        
        if not visit:
            messagebox.showerror("Error", "Visit not found.")
            return
        
        # Create summary window
        summary_window = tk.Toplevel(self.parent)
        summary_window.title(f"Visit Summary - {visit.visit_id}")
        summary_window.geometry("600x500")
        summary_window.transient(self.parent)
        
        # Summary content
        main_frame = ttk.Frame(summary_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Get patient info
        patient = self.data_manager.get_patient_by_id(visit.patient_id)
        patient_name = patient.name if patient else "Unknown Patient"
        
        ttk.Label(main_frame, text=f"Visit Summary for {patient_name}", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Create summary text
        summary_text = tk.Text(main_frame, wrap='word', height=20, width=70)
        summary_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=summary_text.yview)
        summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        # Build summary content
        summary_content = f"""Visit ID: {visit.visit_id}
Patient: {patient_name} (ID: {visit.patient_id})
Doctor: {visit.doctor_name}
Date: {visit.visit_date}
Status: {visit.status}

VITAL SIGNS:
{self.format_vital_signs(visit.vital_signs)}

SYMPTOMS:
{visit.symptoms}

DIAGNOSIS:
{visit.diagnosis}

PRESCRIPTION:
{visit.prescription}

LAB TESTS:
{visit.lab_tests}

FOLLOW-UP DATE:
{visit.follow_up_date if visit.follow_up_date else 'None scheduled'}

NOTES:
{visit.notes}
"""
        
        summary_text.insert('1.0', summary_content)
        summary_text.config(state='disabled')
        
        summary_text.pack(side='left', fill='both', expand=True)
        summary_scrollbar.pack(side='right', fill='y')
        
        # Close button
        ttk.Button(main_frame, text="Close", command=summary_window.destroy).pack(pady=10)
    
    def format_vital_signs(self, vital_signs):
        """Format vital signs for display"""
        if not vital_signs:
            return "Not recorded"
        
        formatted = []
        if vital_signs.get('blood_pressure'):
            formatted.append(f"Blood Pressure: {vital_signs['blood_pressure']}")
        if vital_signs.get('temperature'):
            formatted.append(f"Temperature: {vital_signs['temperature']}")
        if vital_signs.get('pulse'):
            formatted.append(f"Pulse: {vital_signs['pulse']}")
        if vital_signs.get('weight'):
            formatted.append(f"Weight: {vital_signs['weight']}")
        
        return '\n'.join(formatted) if formatted else "Not recorded"
    
    def refresh_visits(self):
        """Refresh the visit list"""
        # Clear existing items
        for item in self.visit_tree.get_children():
            self.visit_tree.delete(item)
        
        # Load visits
        visits = self.data_manager.get_opd_visits()
        
        # Apply filters
        date_filter = self.list_date_filter_var.get()
        doctor_filter = self.list_doctor_filter_var.get()
        status_filter = self.list_status_filter_var.get()
        
        for visit in sorted(visits, key=lambda x: x.visit_date, reverse=True):
            # Apply filters
            if date_filter and date_filter not in visit.visit_date:
                continue
            
            if doctor_filter and doctor_filter != 'All' and visit.doctor_name != doctor_filter:
                continue
            
            if status_filter and status_filter != 'All' and visit.status != status_filter:
                continue
            
            # Get patient name
            patient = self.data_manager.get_patient_by_id(visit.patient_id)
            patient_name = patient.name if patient else "Unknown Patient"
            
            # Format date
            try:
                visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                date_str = visit_date.strftime("%Y-%m-%d")
            except ValueError:
                date_str = visit.visit_date
            
            # Truncate long text for display
            symptoms_display = visit.symptoms[:50] + "..." if len(visit.symptoms) > 50 else visit.symptoms
            diagnosis_display = visit.diagnosis[:50] + "..." if len(visit.diagnosis) > 50 else visit.diagnosis
            
            self.visit_tree.insert('', 'end', values=(
                visit.visit_id,
                patient_name,
                visit.doctor_name,
                date_str,
                symptoms_display,
                diagnosis_display,
                visit.status
            ))
    
    def filter_visits(self, event=None):
        """Apply filters to visit list"""
        self.refresh_visits()
    
    def clear_visit_filters(self):
        """Clear all visit filters"""
        self.list_date_filter_var.set('')
        self.list_doctor_filter_var.set('All')
        self.list_status_filter_var.set('All')
        self.refresh_visits()
    
    def refresh_queue(self):
        """Refresh queue display"""
        # Clear queue tree
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        
        # Get today's in-progress visits
        today_visits = self.data_manager.get_todays_opd_visits()
        in_progress_visits = [visit for visit in today_visits if visit.status == 'In Progress']
        
        # Update queue status
        queue_count = len(in_progress_visits)
        self.queue_status_label.config(text=f"Queue: {queue_count} patients waiting")
        
        # Display queue
        for i, visit in enumerate(in_progress_visits):
            patient = self.data_manager.get_patient_by_id(visit.patient_id)
            patient_name = patient.name if patient else "Unknown Patient"
            
            # Format check-in time
            try:
                checkin_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                time_str = checkin_time.strftime("%H:%M")
            except ValueError:
                time_str = "Unknown"
            
            self.queue_tree.insert('', 'end', values=(
                i + 1,  # Position
                patient_name,
                time_str,
                visit.doctor_name,
                visit.status
            ))
        
        # Update completed patients list
        self.completed_listbox.delete(0, tk.END)
        completed_visits = [visit for visit in today_visits if visit.status == 'Completed']
        
        for visit in completed_visits:
            patient = self.data_manager.get_patient_by_id(visit.patient_id)
            patient_name = patient.name if patient else "Unknown Patient"
            
            try:
                completion_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                time_str = completion_time.strftime("%H:%M")
            except ValueError:
                time_str = "Unknown"
            
            self.completed_listbox.insert(tk.END, f"{patient_name} - Completed at {time_str}")
    
    def call_next_patient(self):
        """Call next patient in queue"""
        # Get next patient from queue
        today_visits = self.data_manager.get_todays_opd_visits()
        in_progress_visits = [visit for visit in today_visits if visit.status == 'In Progress']
        
        if not in_progress_visits:
            messagebox.showinfo("Queue", "No patients in queue.")
            return
        
        # Get first patient
        next_visit = in_progress_visits[0]
        patient = self.data_manager.get_patient_by_id(next_visit.patient_id)
        
        if patient and self.announcement_system:
            self.announcement_system.announce_patient_call(patient.name)
            messagebox.showinfo("Patient Called", f"Called patient: {patient.name}")
        else:
            messagebox.showinfo("Patient Called", "Next patient has been called.")
    
    def clear_queue(self):
        """Clear the queue"""
        result = messagebox.askyesno("Clear Queue", "Clear all patients from the queue?")
        if result:
            self.opd_queue.clear_queue()
            self.refresh_queue()
            messagebox.showinfo("Queue", "Queue cleared successfully.")
    
    def manual_announcement(self):
        """Make manual announcement"""
        # Create manual announcement dialog
        announcement_window = tk.Toplevel(self.parent)
        announcement_window.title("Manual Announcement")
        announcement_window.geometry("400x200")
        announcement_window.transient(self.parent)
        announcement_window.grab_set()
        
        main_frame = ttk.Frame(announcement_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Patient Name:").pack(anchor='w', pady=5)
        patient_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=patient_name_var, width=40).pack(fill='x', pady=5)
        
        ttk.Label(main_frame, text="Message (optional):").pack(anchor='w', pady=5)
        message_text = tk.Text(main_frame, height=4, width=40)
        message_text.pack(fill='both', expand=True, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        def make_announcement():
            name = patient_name_var.get().strip()
            message = message_text.get('1.0', tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter patient name.")
                return
            
            if self.announcement_system:
                self.announcement_system.add_manual_announcement(name, message if message else None)
            
            announcement_window.destroy()
            messagebox.showinfo("Announcement", f"Announcement made for {name}")
        
        ttk.Button(button_frame, text="Announce", command=make_announcement).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=announcement_window.destroy).pack(side='left', padx=5)
    
    def test_announcement(self):
        """Test announcement system"""
        if self.announcement_system:
            success = self.announcement_system.test_announcement()
            if success:
                messagebox.showinfo("Test", "Announcement test completed successfully!")
            else:
                messagebox.showwarning("Test", "Announcement test completed with warnings.")
        else:
            messagebox.showerror("Error", "Announcement system not available.")
    
    def refresh(self):
        """Refresh all OPD data"""
        self.refresh_visits()
        self.refresh_todays_visits()
        self.refresh_queue()
        self.refresh_form_patient_list()
