"""
Appointment Scheduling UI - Handles appointment booking, management, and calendar view
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models.appointment import Appointment, DoctorSchedule
import calendar

class AppointmentSchedulingFrame:
    """Appointment scheduling interface"""
    
    def __init__(self, parent, data_manager):
        """Initialize appointment scheduling frame"""
        self.parent = parent
        self.data_manager = data_manager
        self.current_appointment = None
        self.selected_date = datetime.now().date()
        
        self.create_widgets()
        self.refresh_appointments()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(main_frame, text="Appointment Scheduling", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_calendar_tab()
        self.create_appointment_form_tab()
        self.create_appointment_list_tab()
        self.create_doctor_schedule_tab()
    
    def create_calendar_tab(self):
        """Create calendar view tab"""
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_frame, text="Calendar View")
        
        # Calendar controls
        control_frame = ttk.Frame(calendar_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Date navigation
        ttk.Button(control_frame, text="← Previous", 
                  command=self.previous_month).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Today", 
                  command=self.goto_today).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Next →", 
                  command=self.next_month).pack(side='left', padx=(0, 5))
        
        self.calendar_label = ttk.Label(control_frame, text="", style='Heading.TLabel')
        self.calendar_label.pack(side='left', padx=(20, 0))
        
        # Filter controls
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Filter by Doctor:").pack(side='left', padx=(0, 5))
        self.calendar_doctor_var = tk.StringVar()
        doctor_names = ['All'] + [doc['name'] for doc in DoctorSchedule.get_doctors()]
        doctor_filter = ttk.Combobox(filter_frame, textvariable=self.calendar_doctor_var,
                                   values=doctor_names, width=15, state='readonly')
        doctor_filter.set('All')
        doctor_filter.pack(side='left', padx=(0, 5))
        doctor_filter.bind('<<ComboboxSelected>>', self.refresh_calendar)
        
        ttk.Button(filter_frame, text="Refresh", 
                  command=self.refresh_calendar).pack(side='left', padx=(5, 0))
        
        # Calendar container
        calendar_container = ttk.Frame(calendar_frame)
        calendar_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create calendar grid
        self.create_calendar_grid(calendar_container)
        
        # Selected date info
        info_frame = ttk.LabelFrame(calendar_frame, text="Selected Date Information", padding="10")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.selected_date_label = ttk.Label(info_frame, text="No date selected")
        self.selected_date_label.pack()
        
        # Appointments for selected date
        self.date_appointments_frame = ttk.Frame(info_frame)
        self.date_appointments_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Update calendar
        self.update_calendar_display()
    
    def create_calendar_grid(self, parent):
        """Create calendar grid widget"""
        # Calendar frame
        self.calendar_grid_frame = ttk.Frame(parent)
        self.calendar_grid_frame.pack(fill='both', expand=True)
        
        # Days of week header
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_grid_frame, text=day, style='Heading.TLabel')
            label.grid(row=0, column=i, padx=1, pady=1, sticky='nsew')
        
        # Calendar day buttons
        self.day_buttons = {}
        for week in range(6):  # Max 6 weeks in a month view
            for day in range(7):
                btn = tk.Button(self.calendar_grid_frame, text="", width=8, height=4,
                              command=lambda w=week, d=day: self.select_calendar_date(w, d))
                btn.grid(row=week+1, column=day, padx=1, pady=1, sticky='nsew')
                self.day_buttons[(week, day)] = btn
        
        # Configure grid weights
        for i in range(7):
            self.calendar_grid_frame.columnconfigure(i, weight=1)
        for i in range(7):
            self.calendar_grid_frame.rowconfigure(i, weight=1)
    
    def create_appointment_form_tab(self):
        """Create appointment form tab"""
        form_frame = ttk.Frame(self.notebook)
        self.notebook.add(form_frame, text="Book Appointment")
        
        # Form container
        form_container = ttk.LabelFrame(form_frame, text="Appointment Details", padding="10")
        form_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Appointment ID (read-only)
        ttk.Label(form_container, text="Appointment ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.appointment_id_var = tk.StringVar()
        appointment_id_entry = ttk.Entry(form_container, textvariable=self.appointment_id_var, 
                                       state='readonly', width=20)
        appointment_id_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Patient selection
        ttk.Label(form_container, text="Patient:*").grid(row=1, column=0, sticky='w', pady=5)
        patient_frame = ttk.Frame(form_container)
        patient_frame.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(patient_frame, textvariable=self.patient_var, 
                                        width=25, state='readonly')
        self.patient_combo.pack(side='left')
        
        ttk.Button(patient_frame, text="Refresh Patients", 
                  command=self.refresh_patient_list).pack(side='left', padx=(5, 0))
        
        # Doctor selection
        ttk.Label(form_container, text="Doctor:*").grid(row=2, column=0, sticky='w', pady=5)
        self.doctor_var = tk.StringVar()
        doctor_combo = ttk.Combobox(form_container, textvariable=self.doctor_var,
                                  values=[doc['name'] for doc in DoctorSchedule.get_doctors()],
                                  width=25, state='readonly')
        doctor_combo.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        doctor_combo.bind('<<ComboboxSelected>>', self.on_doctor_selected)
        
        # Department (auto-filled based on doctor)
        ttk.Label(form_container, text="Department:").grid(row=3, column=0, sticky='w', pady=5)
        self.department_var = tk.StringVar()
        department_entry = ttk.Entry(form_container, textvariable=self.department_var, 
                                   state='readonly', width=25)
        department_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Date selection
        ttk.Label(form_container, text="Date:*").grid(row=4, column=0, sticky='w', pady=5)
        date_frame = ttk.Frame(form_container)
        date_frame.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))
        
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        date_entry.pack(side='left')
        date_entry.bind('<KeyRelease>', self.on_date_changed)
        
        ttk.Label(date_frame, text="(YYYY-MM-DD)").pack(side='left', padx=(5, 0))
        
        # Time selection
        ttk.Label(form_container, text="Time:*").grid(row=5, column=0, sticky='w', pady=5)
        self.time_var = tk.StringVar()
        self.time_combo = ttk.Combobox(form_container, textvariable=self.time_var,
                                     width=15, state='readonly')
        self.time_combo.grid(row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Status
        ttk.Label(form_container, text="Status:").grid(row=6, column=0, sticky='w', pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(form_container, textvariable=self.status_var,
                                  values=['Scheduled', 'Completed', 'Cancelled', 'No-Show'],
                                  width=15, state='readonly')
        status_combo.set('Scheduled')
        status_combo.grid(row=6, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(form_container, text="Notes:").grid(row=7, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(form_container, width=40, height=3)
        self.notes_text.grid(row=7, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Button frame
        button_frame = ttk.Frame(form_container)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        self.save_appointment_button = ttk.Button(button_frame, text="Save Appointment", 
                                                command=self.save_appointment)
        self.save_appointment_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_appointment_form).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_appointment_edit).pack(side='left', padx=5)
        
        # Required fields note
        ttk.Label(form_container, text="* Required fields", 
                 foreground='red').grid(row=9, column=0, columnspan=2, pady=5)
        
        # Initialize form
        self.refresh_patient_list()
        self.clear_appointment_form()
    
    def create_appointment_list_tab(self):
        """Create appointment list tab"""
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Appointment List")
        
        # Control frame
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(control_frame, text="New Appointment", 
                  command=self.new_appointment).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Edit Appointment", 
                  command=self.edit_appointment).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Cancel Appointment", 
                  command=self.cancel_appointment).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Mark Completed", 
                  command=self.mark_appointment_completed).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Refresh", 
                  command=self.refresh_appointments).pack(side='left', padx=(0, 5))
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left', padx=(0, 5))
        
        ttk.Label(filter_frame, text="Doctor:").pack(side='left', padx=(0, 5))
        self.list_doctor_var = tk.StringVar()
        doctor_filter = ttk.Combobox(filter_frame, textvariable=self.list_doctor_var,
                                   values=['All'] + [doc['name'] for doc in DoctorSchedule.get_doctors()],
                                   width=15, state='readonly')
        doctor_filter.set('All')
        doctor_filter.pack(side='left', padx=(0, 10))
        doctor_filter.bind('<<ComboboxSelected>>', self.filter_appointments)
        
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=(0, 5))
        self.list_status_var = tk.StringVar()
        status_filter = ttk.Combobox(filter_frame, textvariable=self.list_status_var,
                                   values=['All', 'Scheduled', 'Completed', 'Cancelled', 'No-Show'],
                                   width=12, state='readonly')
        status_filter.set('All')
        status_filter.pack(side='left', padx=(0, 10))
        status_filter.bind('<<ComboboxSelected>>', self.filter_appointments)
        
        ttk.Label(filter_frame, text="Date:").pack(side='left', padx=(0, 5))
        self.list_date_var = tk.StringVar()
        date_filter = ttk.Entry(filter_frame, textvariable=self.list_date_var, width=12)
        date_filter.pack(side='left', padx=(0, 5))
        date_filter.bind('<KeyRelease>', self.filter_appointments)
        
        ttk.Button(filter_frame, text="Clear Filters", 
                  command=self.clear_filters).pack(side='left', padx=(10, 0))
        
        # Appointment list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'Patient', 'Doctor', 'Department', 'Date', 'Time', 'Status', 'Notes')
        self.appointment_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.appointment_tree.heading('ID', text='Appointment ID')
        self.appointment_tree.heading('Patient', text='Patient')
        self.appointment_tree.heading('Doctor', text='Doctor')
        self.appointment_tree.heading('Department', text='Department')
        self.appointment_tree.heading('Date', text='Date')
        self.appointment_tree.heading('Time', text='Time')
        self.appointment_tree.heading('Status', text='Status')
        self.appointment_tree.heading('Notes', text='Notes')
        
        # Column widths
        self.appointment_tree.column('ID', width=120)
        self.appointment_tree.column('Patient', width=120)
        self.appointment_tree.column('Doctor', width=120)
        self.appointment_tree.column('Department', width=100)
        self.appointment_tree.column('Date', width=100)
        self.appointment_tree.column('Time', width=80)
        self.appointment_tree.column('Status', width=100)
        self.appointment_tree.column('Notes', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.appointment_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient='horizontal', command=self.appointment_tree.xview)
        self.appointment_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.appointment_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.appointment_tree.bind('<Double-1>', lambda e: self.edit_appointment())
    
    def create_doctor_schedule_tab(self):
        """Create doctor schedule overview tab"""
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Doctor Schedules")
        
        # Title
        ttk.Label(schedule_frame, text="Doctor Availability Overview", 
                 style='Title.TLabel').pack(pady=10)
        
        # Date selection for schedule view
        date_frame = ttk.Frame(schedule_frame)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="View Schedule for Date:").pack(side='left', padx=(0, 5))
        self.schedule_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        schedule_date_entry = ttk.Entry(date_frame, textvariable=self.schedule_date_var, width=12)
        schedule_date_entry.pack(side='left', padx=(0, 5))
        
        ttk.Button(date_frame, text="View Schedule", 
                  command=self.refresh_doctor_schedules).pack(side='left', padx=(5, 0))
        
        # Doctor schedule container
        self.schedule_container = ttk.Frame(schedule_frame)
        self.schedule_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initial schedule load
        self.refresh_doctor_schedules()
    
    def update_calendar_display(self):
        """Update calendar display"""
        now = datetime.now()
        display_date = datetime(now.year, now.month, 1)
        
        # Update calendar label
        self.calendar_label.config(text=display_date.strftime("%B %Y"))
        
        # Get calendar data
        cal = calendar.monthcalendar(display_date.year, display_date.month)
        
        # Clear all buttons
        for (week, day), btn in self.day_buttons.items():
            btn.config(text="", state='disabled', bg='lightgray')
        
        # Fill calendar
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                
                btn = self.day_buttons[(week_num, day_num)]
                btn.config(text=str(day), state='normal', bg='white')
                
                # Highlight today
                if (display_date.year == now.year and 
                    display_date.month == now.month and 
                    day == now.day):
                    btn.config(bg='lightblue')
                
                # Check for appointments on this day
                check_date = datetime(display_date.year, display_date.month, day).date()
                appointments = self.get_appointments_for_date(check_date)
                
                if appointments:
                    btn.config(bg='lightgreen')
                
                # Store date for button
                btn.date = check_date
    
    def select_calendar_date(self, week, day):
        """Handle calendar date selection"""
        btn = self.day_buttons[(week, day)]
        if hasattr(btn, 'date'):
            self.selected_date = btn.date
            self.update_selected_date_info()
            
            # Set date in appointment form
            self.date_var.set(self.selected_date.strftime("%Y-%m-%d"))
            self.on_date_changed()
    
    def update_selected_date_info(self):
        """Update selected date information"""
        if self.selected_date:
            self.selected_date_label.config(
                text=f"Selected Date: {self.selected_date.strftime('%A, %B %d, %Y')}"
            )
            
            # Clear previous appointment info
            for widget in self.date_appointments_frame.winfo_children():
                widget.destroy()
            
            # Get appointments for selected date
            appointments = self.get_appointments_for_date(self.selected_date)
            
            if appointments:
                ttk.Label(self.date_appointments_frame, 
                         text=f"Appointments for this date ({len(appointments)}):").pack(anchor='w')
                
                for appt in appointments:
                    patient = self.data_manager.get_patient_by_id(appt.patient_id)
                    patient_name = patient.name if patient else "Unknown Patient"
                    
                    appt_text = f"• {appt.appointment_time} - {patient_name} with {appt.doctor_name} ({appt.status})"
                    ttk.Label(self.date_appointments_frame, text=appt_text).pack(anchor='w')
            else:
                ttk.Label(self.date_appointments_frame, 
                         text="No appointments for this date").pack(anchor='w')
    
    def get_appointments_for_date(self, date):
        """Get appointments for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        appointments = self.data_manager.get_appointments_by_date(date_str)
        
        # Apply doctor filter if set
        doctor_filter = self.calendar_doctor_var.get()
        if doctor_filter and doctor_filter != 'All':
            appointments = [appt for appt in appointments if appt.doctor_name == doctor_filter]
        
        return appointments
    
    def previous_month(self):
        """Navigate to previous month"""
        current = datetime.now()
        if current.month == 1:
            new_date = current.replace(year=current.year-1, month=12)
        else:
            new_date = current.replace(month=current.month-1)
        
        # Update display (simplified for this implementation)
        self.update_calendar_display()
    
    def next_month(self):
        """Navigate to next month"""
        current = datetime.now()
        if current.month == 12:
            new_date = current.replace(year=current.year+1, month=1)
        else:
            new_date = current.replace(month=current.month+1)
        
        # Update display (simplified for this implementation)
        self.update_calendar_display()
    
    def goto_today(self):
        """Navigate to today"""
        self.selected_date = datetime.now().date()
        self.update_calendar_display()
        self.update_selected_date_info()
    
    def refresh_calendar(self, event=None):
        """Refresh calendar view"""
        self.update_calendar_display()
        self.update_selected_date_info()
    
    def refresh_patient_list(self):
        """Refresh patient list in combobox"""
        patients = self.data_manager.get_patients()
        patient_options = [f"{p.patient_id} - {p.name}" for p in patients]
        self.patient_combo.config(values=patient_options)
    
    def on_doctor_selected(self, event=None):
        """Handle doctor selection"""
        doctor_name = self.doctor_var.get()
        
        # Auto-fill department
        for doctor in DoctorSchedule.get_doctors():
            if doctor['name'] == doctor_name:
                self.department_var.set(doctor['department'])
                break
        
        # Update available time slots
        self.update_available_slots()
    
    def on_date_changed(self, event=None):
        """Handle date change"""
        self.update_available_slots()
    
    def update_available_slots(self):
        """Update available time slots based on doctor and date"""
        doctor_name = self.doctor_var.get()
        date_str = self.date_var.get()
        
        if not doctor_name or not date_str:
            self.time_combo.config(values=[])
            return
        
        try:
            # Validate date
            datetime.strptime(date_str, "%Y-%m-%d")
            
            # Get existing appointments
            existing_appointments = self.data_manager.get_appointments()
            
            # Get available slots
            available_slots = DoctorSchedule.get_available_slots(
                doctor_name, date_str, existing_appointments
            )
            
            self.time_combo.config(values=available_slots)
            
            if available_slots:
                self.time_combo.set(available_slots[0])
            else:
                self.time_combo.set("")
                
        except ValueError:
            self.time_combo.config(values=[])
    
    def new_appointment(self):
        """Start creating a new appointment"""
        self.current_appointment = None
        self.clear_appointment_form()
        self.notebook.select(1)  # Switch to form tab
        
        # Generate new appointment ID
        new_appointment = Appointment()
        self.appointment_id_var.set(new_appointment.appointment_id)
    
    def clear_appointment_form(self):
        """Clear the appointment form"""
        self.appointment_id_var.set('')
        self.patient_var.set('')
        self.doctor_var.set('')
        self.department_var.set('')
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.time_var.set('')
        self.status_var.set('Scheduled')
        self.notes_text.delete('1.0', tk.END)
        self.current_appointment = None
        
        # Update available slots
        self.update_available_slots()
    
    def save_appointment(self):
        """Save appointment data"""
        try:
            # Get form data
            appointment_id = self.appointment_id_var.get().strip()
            patient_selection = self.patient_var.get().strip()
            doctor_name = self.doctor_var.get().strip()
            department = self.department_var.get().strip()
            date_str = self.date_var.get().strip()
            time_str = self.time_var.get().strip()
            status = self.status_var.get().strip()
            notes = self.notes_text.get('1.0', tk.END).strip()
            
            # Extract patient ID from selection
            if not patient_selection:
                messagebox.showerror("Validation Error", "Please select a patient.")
                return
            
            patient_id = patient_selection.split(' - ')[0]
            
            # Create or update appointment
            if self.current_appointment:
                # Update existing appointment
                appointment = self.current_appointment
                appointment.patient_id = patient_id
                appointment.doctor_name = doctor_name
                appointment.department = department
                appointment.appointment_date = date_str
                appointment.appointment_time = time_str
                appointment.status = status
                appointment.notes = notes
            else:
                # Create new appointment
                appointment = Appointment(
                    appointment_id=appointment_id,
                    patient_id=patient_id,
                    doctor_name=doctor_name,
                    department=department,
                    appointment_date=date_str,
                    appointment_time=time_str,
                    status=status,
                    notes=notes
                )
            
            # Validate appointment
            is_valid, error_message = appointment.validate()
            if not is_valid:
                messagebox.showerror("Validation Error", error_message)
                return
            
            # Check for conflicts
            existing_appointments = self.data_manager.get_appointments()
            for existing in existing_appointments:
                if (existing.appointment_id != appointment.appointment_id and
                    existing.doctor_name == appointment.doctor_name and
                    existing.appointment_date == appointment.appointment_date and
                    existing.appointment_time == appointment.appointment_time and
                    existing.status in ['Scheduled', 'Completed']):
                    messagebox.showerror("Conflict", 
                                       f"Doctor {doctor_name} already has an appointment at {time_str} on {date_str}")
                    return
            
            # Save appointment
            success = self.data_manager.save_appointment(appointment)
            if success:
                messagebox.showinfo("Success", "Appointment saved successfully!")
                self.clear_appointment_form()
                self.refresh_appointments()
                self.refresh_calendar()
                self.notebook.select(2)  # Switch to list tab
            else:
                messagebox.showerror("Error", "Failed to save appointment.")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving appointment:\n{str(e)}")
    
    def cancel_appointment_edit(self):
        """Cancel editing and return to list"""
        self.clear_appointment_form()
        self.notebook.select(2)
    
    def edit_appointment(self):
        """Edit selected appointment"""
        selected = self.appointment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an appointment to edit.")
            return
        
        # Get appointment ID from selection
        appointment_id = self.appointment_tree.item(selected[0])['values'][0]
        appointment = self.data_manager.get_appointment_by_id(appointment_id)
        
        if appointment:
            self.current_appointment = appointment
            self.load_appointment_to_form(appointment)
            self.notebook.select(1)  # Switch to form tab
        else:
            messagebox.showerror("Error", "Appointment not found.")
    
    def load_appointment_to_form(self, appointment):
        """Load appointment data into form"""
        self.appointment_id_var.set(appointment.appointment_id)
        
        # Set patient
        patient = self.data_manager.get_patient_by_id(appointment.patient_id)
        if patient:
            patient_text = f"{patient.patient_id} - {patient.name}"
            self.patient_var.set(patient_text)
        
        self.doctor_var.set(appointment.doctor_name)
        self.department_var.set(appointment.department)
        self.date_var.set(appointment.appointment_date)
        self.time_var.set(appointment.appointment_time)
        self.status_var.set(appointment.status)
        
        # Set notes in text widget
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', appointment.notes)
        
        # Update available slots
        self.update_available_slots()
    
    def cancel_appointment(self):
        """Cancel selected appointment"""
        selected = self.appointment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an appointment to cancel.")
            return
        
        appointment_id = self.appointment_tree.item(selected[0])['values'][0]
        appointment = self.data_manager.get_appointment_by_id(appointment_id)
        
        if not appointment:
            messagebox.showerror("Error", "Appointment not found.")
            return
        
        # Confirm cancellation
        patient = self.data_manager.get_patient_by_id(appointment.patient_id)
        patient_name = patient.name if patient else "Unknown Patient"
        
        result = messagebox.askyesno("Confirm Cancellation", 
                                   f"Cancel appointment for {patient_name} with {appointment.doctor_name} "
                                   f"on {appointment.appointment_date} at {appointment.appointment_time}?")
        
        if result:
            appointment.status = "Cancelled"
            success = self.data_manager.save_appointment(appointment)
            if success:
                messagebox.showinfo("Success", "Appointment cancelled successfully!")
                self.refresh_appointments()
                self.refresh_calendar()
            else:
                messagebox.showerror("Error", "Failed to cancel appointment.")
    
    def mark_appointment_completed(self):
        """Mark selected appointment as completed"""
        selected = self.appointment_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an appointment to mark as completed.")
            return
        
        appointment_id = self.appointment_tree.item(selected[0])['values'][0]
        appointment = self.data_manager.get_appointment_by_id(appointment_id)
        
        if not appointment:
            messagebox.showerror("Error", "Appointment not found.")
            return
        
        appointment.status = "Completed"
        success = self.data_manager.save_appointment(appointment)
        if success:
            messagebox.showinfo("Success", "Appointment marked as completed!")
            self.refresh_appointments()
            self.refresh_calendar()
        else:
            messagebox.showerror("Error", "Failed to update appointment.")
    
    def refresh_appointments(self):
        """Refresh the appointment list"""
        # Clear existing items
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
        
        # Load appointments
        appointments = self.data_manager.get_appointments()
        
        # Apply filters
        doctor_filter = self.list_doctor_var.get()
        status_filter = self.list_status_var.get()
        date_filter = self.list_date_var.get()
        
        for appointment in appointments:
            # Apply filters
            if doctor_filter and doctor_filter != 'All' and appointment.doctor_name != doctor_filter:
                continue
            
            if status_filter and status_filter != 'All' and appointment.status != status_filter:
                continue
            
            if date_filter and date_filter not in appointment.appointment_date:
                continue
            
            # Get patient name
            patient = self.data_manager.get_patient_by_id(appointment.patient_id)
            patient_name = patient.name if patient else "Unknown Patient"
            
            # Truncate notes for display
            notes_display = appointment.notes[:30] + "..." if len(appointment.notes) > 30 else appointment.notes
            
            self.appointment_tree.insert('', 'end', values=(
                appointment.appointment_id,
                patient_name,
                appointment.doctor_name,
                appointment.department,
                appointment.appointment_date,
                appointment.appointment_time,
                appointment.status,
                notes_display
            ))
    
    def filter_appointments(self, event=None):
        """Apply filters to appointment list"""
        self.refresh_appointments()
    
    def clear_filters(self):
        """Clear all filters"""
        self.list_doctor_var.set('All')
        self.list_status_var.set('All')
        self.list_date_var.set('')
        self.refresh_appointments()
    
    def refresh_doctor_schedules(self):
        """Refresh doctor schedule overview"""
        # Clear existing schedule display
        for widget in self.schedule_container.winfo_children():
            widget.destroy()
        
        schedule_date = self.schedule_date_var.get()
        
        try:
            # Validate date
            datetime.strptime(schedule_date, "%Y-%m-%d")
        except ValueError:
            ttk.Label(self.schedule_container, text="Invalid date format. Use YYYY-MM-DD").pack()
            return
        
        # Get existing appointments for the date
        existing_appointments = self.data_manager.get_appointments_by_date(schedule_date)
        
        # Display schedule for each doctor
        doctors = DoctorSchedule.get_doctors()
        
        for i, doctor in enumerate(doctors):
            doctor_frame = ttk.LabelFrame(self.schedule_container, 
                                        text=f"{doctor['name']} - {doctor['department']}", 
                                        padding="10")
            doctor_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='nsew')
            
            # Get available and booked slots
            available_slots = DoctorSchedule.get_available_slots(
                doctor['name'], schedule_date, existing_appointments
            )
            
            all_slots = doctor['slots']
            booked_slots = [slot for slot in all_slots if slot not in available_slots]
            
            # Display slots
            if available_slots:
                ttk.Label(doctor_frame, text="Available:", foreground='green').pack(anchor='w')
                for slot in available_slots:
                    ttk.Label(doctor_frame, text=f"  • {slot}", foreground='green').pack(anchor='w')
            
            if booked_slots:
                ttk.Label(doctor_frame, text="Booked:", foreground='red').pack(anchor='w')
                for slot in booked_slots:
                    # Find the appointment for this slot
                    appointment = next((appt for appt in existing_appointments 
                                      if appt.doctor_name == doctor['name'] and appt.appointment_time == slot), None)
                    if appointment:
                        patient = self.data_manager.get_patient_by_id(appointment.patient_id)
                        patient_name = patient.name if patient else "Unknown"
                        ttk.Label(doctor_frame, text=f"  • {slot} - {patient_name}", foreground='red').pack(anchor='w')
                    else:
                        ttk.Label(doctor_frame, text=f"  • {slot}", foreground='red').pack(anchor='w')
            
            if not available_slots and not booked_slots:
                ttk.Label(doctor_frame, text="No schedule available").pack()
        
        # Configure grid weights
        self.schedule_container.columnconfigure(0, weight=1)
        self.schedule_container.columnconfigure(1, weight=1)
    
    def refresh(self):
        """Refresh all appointment data"""
        self.refresh_appointments()
        self.refresh_calendar()
        self.refresh_patient_list()
        self.refresh_doctor_schedules()
