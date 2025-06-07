"""
Patient Management UI - Handles patient registration, editing, and search
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.patient import Patient

class PatientManagementFrame:
    """Patient management interface"""
    
    def __init__(self, parent, data_manager):
        """Initialize patient management frame"""
        self.parent = parent
        self.data_manager = data_manager
        self.current_patient = None
        
        self.create_widgets()
        self.refresh_patient_list()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(main_frame, text="Patient Management", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_patient_list_tab()
        self.create_patient_form_tab()
        self.create_patient_search_tab()
    
    def create_patient_list_tab(self):
        """Create patient list tab"""
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Patient List")
        
        # Control frame
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="Add New Patient", 
                  command=self.new_patient).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Edit Patient", 
                  command=self.edit_patient).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Delete Patient", 
                  command=self.delete_patient).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_patient_list).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="View History", 
                  command=self.view_patient_history).pack(side='left', padx=(0, 5))
        
        # Patient list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'Name', 'Age', 'Gender', 'Phone', 'Registration Date')
        self.patient_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.patient_tree.heading('ID', text='Patient ID')
        self.patient_tree.heading('Name', text='Name')
        self.patient_tree.heading('Age', text='Age')
        self.patient_tree.heading('Gender', text='Gender')
        self.patient_tree.heading('Phone', text='Phone')
        self.patient_tree.heading('Registration Date', text='Registration Date')
        
        # Column widths
        self.patient_tree.column('ID', width=100)
        self.patient_tree.column('Name', width=150)
        self.patient_tree.column('Age', width=60)
        self.patient_tree.column('Gender', width=80)
        self.patient_tree.column('Phone', width=120)
        self.patient_tree.column('Registration Date', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.patient_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient='horizontal', command=self.patient_tree.xview)
        self.patient_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.patient_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.patient_tree.bind('<Double-1>', lambda e: self.edit_patient())
    
    def create_patient_form_tab(self):
        """Create patient form tab"""
        form_frame = ttk.Frame(self.notebook)
        self.notebook.add(form_frame, text="Patient Form")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="Patient Information", padding="10")
        form_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Patient ID (read-only)
        ttk.Label(form_container, text="Patient ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.patient_id_var = tk.StringVar()
        patient_id_entry = ttk.Entry(form_container, textvariable=self.patient_id_var, 
                                   state='readonly', width=20)
        patient_id_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Name
        ttk.Label(form_container, text="Name:*").grid(row=1, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_container, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Age
        ttk.Label(form_container, text="Age:*").grid(row=2, column=0, sticky='w', pady=5)
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(form_container, textvariable=self.age_var, width=10)
        age_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Gender
        ttk.Label(form_container, text="Gender:*").grid(row=3, column=0, sticky='w', pady=5)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(form_container, textvariable=self.gender_var, 
                                  values=['Male', 'Female', 'Other'], width=15, state='readonly')
        gender_combo.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Phone
        ttk.Label(form_container, text="Phone:*").grid(row=4, column=0, sticky='w', pady=5)
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_container, textvariable=self.phone_var, width=20)
        phone_entry.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Contact
        ttk.Label(form_container, text="Emergency Contact:").grid(row=5, column=0, sticky='w', pady=5)
        self.contact_var = tk.StringVar()
        contact_entry = ttk.Entry(form_container, textvariable=self.contact_var, width=30)
        contact_entry.grid(row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Address
        ttk.Label(form_container, text="Address:").grid(row=6, column=0, sticky='nw', pady=5)
        self.address_var = tk.StringVar()
        address_text = tk.Text(form_container, width=40, height=3)
        address_text.grid(row=6, column=1, sticky='w', pady=5, padx=(10, 0))
        self.address_text = address_text
        
        # Registration date (read-only)
        ttk.Label(form_container, text="Registration Date:").grid(row=7, column=0, sticky='w', pady=5)
        self.reg_date_var = tk.StringVar()
        reg_date_entry = ttk.Entry(form_container, textvariable=self.reg_date_var, 
                                 state='readonly', width=20)
        reg_date_entry.grid(row=7, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Button frame
        button_frame = ttk.Frame(form_container)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        self.save_button = ttk.Button(button_frame, text="Save Patient", command=self.save_patient)
        self.save_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_edit).pack(side='left', padx=5)
        
        # Required fields note
        ttk.Label(form_container, text="* Required fields", foreground='red').grid(row=9, column=0, columnspan=2, pady=5)
    
    def create_patient_search_tab(self):
        """Create patient search tab"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search Patients")
        
        # Search controls
        search_control_frame = ttk.LabelFrame(search_frame, text="Search Criteria", padding="10")
        search_control_frame.pack(fill='x', padx=5, pady=5)
        
        # Search text
        ttk.Label(search_control_frame, text="Search:").grid(row=0, column=0, sticky='w', pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_control_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Gender filter
        ttk.Label(search_control_frame, text="Gender:").grid(row=0, column=2, sticky='w', pady=5, padx=(20, 0))
        self.search_gender_var = tk.StringVar()
        gender_filter = ttk.Combobox(search_control_frame, textvariable=self.search_gender_var,
                                   values=['All', 'Male', 'Female', 'Other'], width=10, state='readonly')
        gender_filter.set('All')
        gender_filter.grid(row=0, column=3, sticky='w', pady=5, padx=(10, 0))
        gender_filter.bind('<<ComboboxSelected>>', self.on_search_change)
        
        # Age range
        ttk.Label(search_control_frame, text="Age Range:").grid(row=1, column=0, sticky='w', pady=5)
        age_frame = ttk.Frame(search_control_frame)
        age_frame.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        self.min_age_var = tk.StringVar()
        ttk.Entry(age_frame, textvariable=self.min_age_var, width=5).pack(side='left')
        ttk.Label(age_frame, text=" to ").pack(side='left')
        self.max_age_var = tk.StringVar()
        ttk.Entry(age_frame, textvariable=self.max_age_var, width=5).pack(side='left')
        
        # Search button
        ttk.Button(search_control_frame, text="Search", command=self.search_patients).grid(row=1, column=2, pady=5, padx=(20, 0))
        ttk.Button(search_control_frame, text="Clear", command=self.clear_search).grid(row=1, column=3, pady=5, padx=(10, 0))
        
        # Search results
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding="5")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Search results treeview
        search_columns = ('ID', 'Name', 'Age', 'Gender', 'Phone', 'Address')
        self.search_tree = ttk.Treeview(results_frame, columns=search_columns, show='headings', height=12)
        
        for col in search_columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=100)
        
        # Search scrollbar
        search_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_tree.pack(side='left', fill='both', expand=True)
        search_scrollbar.pack(side='right', fill='y')
        
        # Bind events
        self.search_tree.bind('<Double-1>', lambda e: self.edit_selected_search_patient())
    
    def refresh_patient_list(self):
        """Refresh the patient list"""
        # Clear existing items
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        # Load patients
        patients = self.data_manager.get_patients()
        
        for patient in patients:
            # Format registration date
            try:
                reg_date = datetime.strptime(patient.registration_date, "%Y-%m-%d %H:%M:%S")
                formatted_date = reg_date.strftime("%Y-%m-%d")
            except ValueError:
                formatted_date = patient.registration_date
            
            self.patient_tree.insert('', 'end', values=(
                patient.patient_id,
                patient.name,
                patient.age,
                patient.gender,
                patient.phone,
                formatted_date
            ))
    
    def new_patient(self):
        """Start creating a new patient"""
        self.current_patient = None
        self.clear_form()
        self.notebook.select(1)  # Switch to form tab
        
        # Generate new patient ID
        new_patient = Patient()
        self.patient_id_var.set(new_patient.patient_id)
        self.reg_date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def edit_patient(self):
        """Edit selected patient"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient to edit.")
            return
        
        # Get patient ID from selection
        patient_id = self.patient_tree.item(selected[0])['values'][0]
        patient = self.data_manager.get_patient_by_id(patient_id)
        
        if patient:
            self.current_patient = patient
            self.load_patient_to_form(patient)
            self.notebook.select(1)  # Switch to form tab
        else:
            messagebox.showerror("Error", "Patient not found.")
    
    def load_patient_to_form(self, patient):
        """Load patient data into form"""
        self.patient_id_var.set(patient.patient_id)
        self.name_var.set(patient.name)
        self.age_var.set(str(patient.age))
        self.gender_var.set(patient.gender)
        self.phone_var.set(patient.phone)
        self.contact_var.set(patient.contact)
        self.reg_date_var.set(patient.registration_date)
        
        # Set address in text widget
        self.address_text.delete('1.0', tk.END)
        self.address_text.insert('1.0', patient.address)
    
    def clear_form(self):
        """Clear the patient form"""
        self.patient_id_var.set('')
        self.name_var.set('')
        self.age_var.set('')
        self.gender_var.set('')
        self.phone_var.set('')
        self.contact_var.set('')
        self.reg_date_var.set('')
        self.address_text.delete('1.0', tk.END)
        self.current_patient = None
    
    def save_patient(self):
        """Save patient data"""
        try:
            # Get form data
            patient_id = self.patient_id_var.get().strip()
            name = self.name_var.get().strip()
            age_str = self.age_var.get().strip()
            gender = self.gender_var.get().strip()
            phone = self.phone_var.get().strip()
            contact = self.contact_var.get().strip()
            address = self.address_text.get('1.0', tk.END).strip()
            
            # Validate required fields
            if not name:
                messagebox.showerror("Validation Error", "Patient name is required.")
                return
            
            if not age_str:
                messagebox.showerror("Validation Error", "Patient age is required.")
                return
            
            try:
                age = int(age_str)
                if age <= 0:
                    raise ValueError("Age must be positive")
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid age.")
                return
            
            if not gender:
                messagebox.showerror("Validation Error", "Please select a gender.")
                return
            
            if not phone:
                messagebox.showerror("Validation Error", "Phone number is required.")
                return
            
            # Create or update patient
            if self.current_patient:
                # Update existing patient
                patient = self.current_patient
                patient.name = name
                patient.age = age
                patient.gender = gender
                patient.phone = phone
                patient.contact = contact
                patient.address = address
            else:
                # Create new patient
                patient = Patient(
                    patient_id=patient_id,
                    name=name,
                    age=age,
                    gender=gender,
                    phone=phone,
                    contact=contact,
                    address=address
                )
            
            # Validate patient
            is_valid, error_message = patient.validate()
            if not is_valid:
                messagebox.showerror("Validation Error", error_message)
                return
            
            # Save patient
            success = self.data_manager.save_patient(patient)
            if success:
                messagebox.showinfo("Success", "Patient saved successfully!")
                self.clear_form()
                self.refresh_patient_list()
                self.notebook.select(0)  # Switch back to list tab
            else:
                messagebox.showerror("Error", "Failed to save patient.")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving patient:\n{str(e)}")
    
    def cancel_edit(self):
        """Cancel editing and return to list"""
        self.clear_form()
        self.notebook.select(0)
    
    def delete_patient(self):
        """Delete selected patient"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient to delete.")
            return
        
        # Get patient info
        patient_id = self.patient_tree.item(selected[0])['values'][0]
        patient_name = self.patient_tree.item(selected[0])['values'][1]
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete patient '{patient_name}'?\n\n"
                                   "This action cannot be undone.")
        
        if result:
            success = self.data_manager.delete_patient(patient_id)
            if success:
                messagebox.showinfo("Success", "Patient deleted successfully!")
                self.refresh_patient_list()
            else:
                messagebox.showerror("Error", "Failed to delete patient.")
    
    def view_patient_history(self):
        """View patient's medical history"""
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient to view history.")
            return
        
        patient_id = self.patient_tree.item(selected[0])['values'][0]
        patient = self.data_manager.get_patient_by_id(patient_id)
        
        if not patient:
            messagebox.showerror("Error", "Patient not found.")
            return
        
        # Create history window
        history_window = tk.Toplevel(self.parent)
        history_window.title(f"Medical History - {patient.name}")
        history_window.geometry("800x600")
        history_window.transient(self.parent)
        
        # History content
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Medical History for {patient.name} (ID: {patient.patient_id})", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Create notebook for different types of history
        history_notebook = ttk.Notebook(main_frame)
        history_notebook.pack(fill='both', expand=True)
        
        # Appointments tab
        self.create_appointments_history_tab(history_notebook, patient_id)
        
        # OPD visits tab
        self.create_opd_history_tab(history_notebook, patient_id)
        
        # Medical history tab
        self.create_medical_history_tab(history_notebook, patient)
    
    def create_appointments_history_tab(self, notebook, patient_id):
        """Create appointments history tab"""
        appointments_frame = ttk.Frame(notebook)
        notebook.add(appointments_frame, text="Appointments")
        
        # Get patient's appointments
        appointments = self.data_manager.get_appointments()
        patient_appointments = [appt for appt in appointments if appt.patient_id == patient_id]
        
        if not patient_appointments:
            ttk.Label(appointments_frame, text="No appointments found for this patient.").pack(pady=20)
            return
        
        # Appointments treeview
        appt_columns = ('Date', 'Time', 'Doctor', 'Department', 'Status', 'Notes')
        appt_tree = ttk.Treeview(appointments_frame, columns=appt_columns, show='headings')
        
        for col in appt_columns:
            appt_tree.heading(col, text=col)
            appt_tree.column(col, width=120)
        
        # Add appointments to tree
        for appointment in sorted(patient_appointments, key=lambda x: x.appointment_date, reverse=True):
            appt_tree.insert('', 'end', values=(
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.doctor_name,
                appointment.department,
                appointment.status,
                appointment.notes[:50] + "..." if len(appointment.notes) > 50 else appointment.notes
            ))
        
        # Scrollbar for appointments
        appt_scrollbar = ttk.Scrollbar(appointments_frame, orient='vertical', command=appt_tree.yview)
        appt_tree.configure(yscrollcommand=appt_scrollbar.set)
        
        appt_tree.pack(side='left', fill='both', expand=True)
        appt_scrollbar.pack(side='right', fill='y')
    
    def create_opd_history_tab(self, notebook, patient_id):
        """Create OPD history tab"""
        opd_frame = ttk.Frame(notebook)
        notebook.add(opd_frame, text="OPD Visits")
        
        # Get patient's OPD visits
        opd_visits = self.data_manager.get_patient_opd_history(patient_id)
        
        if not opd_visits:
            ttk.Label(opd_frame, text="No OPD visits found for this patient.").pack(pady=20)
            return
        
        # OPD visits treeview
        opd_columns = ('Date', 'Doctor', 'Symptoms', 'Diagnosis', 'Status')
        opd_tree = ttk.Treeview(opd_frame, columns=opd_columns, show='headings')
        
        for col in opd_columns:
            opd_tree.heading(col, text=col)
            opd_tree.column(col, width=150)
        
        # Add visits to tree
        for visit in sorted(opd_visits, key=lambda x: x.visit_date, reverse=True):
            visit_date = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            opd_tree.insert('', 'end', values=(
                visit_date,
                visit.doctor_name,
                visit.symptoms[:50] + "..." if len(visit.symptoms) > 50 else visit.symptoms,
                visit.diagnosis[:50] + "..." if len(visit.diagnosis) > 50 else visit.diagnosis,
                visit.status
            ))
        
        # Scrollbar for OPD visits
        opd_scrollbar = ttk.Scrollbar(opd_frame, orient='vertical', command=opd_tree.yview)
        opd_tree.configure(yscrollcommand=opd_scrollbar.set)
        
        opd_tree.pack(side='left', fill='both', expand=True)
        opd_scrollbar.pack(side='right', fill='y')
    
    def create_medical_history_tab(self, notebook, patient):
        """Create medical history tab"""
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Medical History")
        
        if not patient.medical_history:
            ttk.Label(history_frame, text="No medical history recorded for this patient.").pack(pady=20)
            return
        
        # Medical history text area
        history_text = tk.Text(history_frame, wrap='word', height=20)
        history_scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=history_text.yview)
        history_text.configure(yscrollcommand=history_scrollbar.set)
        
        # Display medical history
        for i, entry in enumerate(patient.medical_history):
            history_text.insert(tk.END, f"Entry {i+1} - {entry.get('date', 'Unknown date')}\n")
            history_text.insert(tk.END, "-" * 50 + "\n")
            for key, value in entry.items():
                if key != 'date':
                    history_text.insert(tk.END, f"{key.title()}: {value}\n")
            history_text.insert(tk.END, "\n")
        
        history_text.config(state='disabled')
        
        history_text.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')
    
    def search_patients(self):
        """Search patients based on criteria"""
        query = self.search_var.get().strip()
        
        # Build filters
        filters = {}
        
        gender = self.search_gender_var.get()
        if gender and gender != 'All':
            filters['gender'] = gender
        
        min_age_str = self.min_age_var.get().strip()
        if min_age_str:
            try:
                filters['min_age'] = int(min_age_str)
            except ValueError:
                pass
        
        max_age_str = self.max_age_var.get().strip()
        if max_age_str:
            try:
                filters['max_age'] = int(max_age_str)
            except ValueError:
                pass
        
        # Perform search
        results = self.data_manager.search_patients(query, filters)
        
        # Clear and populate search results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        for patient in results:
            self.search_tree.insert('', 'end', values=(
                patient.patient_id,
                patient.name,
                patient.age,
                patient.gender,
                patient.phone,
                patient.address[:50] + "..." if len(patient.address) > 50 else patient.address
            ))
        
        # Show results count
        messagebox.showinfo("Search Results", f"Found {len(results)} patient(s) matching your criteria.")
    
    def on_search_change(self, event=None):
        """Handle search field changes for real-time search"""
        # Perform search automatically when typing
        self.search_patients()
    
    def clear_search(self):
        """Clear search criteria"""
        self.search_var.set('')
        self.search_gender_var.set('All')
        self.min_age_var.set('')
        self.max_age_var.set('')
        
        # Clear search results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
    
    def edit_selected_search_patient(self):
        """Edit patient selected from search results"""
        selected = self.search_tree.selection()
        if not selected:
            return
        
        patient_id = self.search_tree.item(selected[0])['values'][0]
        patient = self.data_manager.get_patient_by_id(patient_id)
        
        if patient:
            self.current_patient = patient
            self.load_patient_to_form(patient)
            self.notebook.select(1)  # Switch to form tab
    
    def refresh(self):
        """Refresh the patient management interface"""
        self.refresh_patient_list()
        self.clear_search()
