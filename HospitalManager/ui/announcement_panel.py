"""
Announcement Panel UI - Handles announcement system management and controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

class AnnouncementPanelFrame:
    """Announcement panel interface for managing the announcement system"""
    
    def __init__(self, parent, data_manager, announcement_system):
        """Initialize announcement panel frame"""
        self.parent = parent
        self.data_manager = data_manager
        self.announcement_system = announcement_system
        self.is_monitoring = False
        self.monitor_thread = None
        
        self.create_widgets()
        self.start_monitoring()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(main_frame, text="Announcement System", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create main layout with three columns
        self.create_main_layout(main_frame)
    
    def create_main_layout(self, parent):
        """Create main layout with status, controls, and logs"""
        # Top section - System status and controls
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Status section
        status_frame = ttk.LabelFrame(top_frame, text="System Status", padding="10")
        status_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.create_status_section(status_frame)
        
        # Quick controls section
        controls_frame = ttk.LabelFrame(top_frame, text="Quick Controls", padding="10")
        controls_frame.pack(side='right', fill='y', padx=(5, 0))
        
        self.create_controls_section(controls_frame)
        
        # Middle section - Manual announcement
        manual_frame = ttk.LabelFrame(parent, text="Manual Announcements", padding="10")
        manual_frame.pack(fill='x', pady=(0, 10))
        
        self.create_manual_announcement_section(manual_frame)
        
        # Bottom section - Logs and activity
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill='both', expand=True)
        
        # Announcement log
        log_frame = ttk.LabelFrame(bottom_frame, text="Announcement Log", padding="5")
        log_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.create_log_section(log_frame)
        
        # Queue and activity
        activity_frame = ttk.LabelFrame(bottom_frame, text="Queue & Activity", padding="5")
        activity_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.create_activity_section(activity_frame)
    
    def create_status_section(self, parent):
        """Create system status section"""
        # System status indicators
        status_grid = ttk.Frame(parent)
        status_grid.pack(fill='x')
        
        # Announcement system status
        ttk.Label(status_grid, text="Announcement System:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=2)
        self.system_status_var = tk.StringVar()
        self.system_status_label = ttk.Label(status_grid, textvariable=self.system_status_var, foreground='green')
        self.system_status_label.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # TTS status
        ttk.Label(status_grid, text="Text-to-Speech:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=2)
        self.tts_status_var = tk.StringVar()
        self.tts_status_label = ttk.Label(status_grid, textvariable=self.tts_status_var)
        self.tts_status_label.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Last announcement
        ttk.Label(status_grid, text="Last Announcement:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=2)
        self.last_announcement_var = tk.StringVar(value="None")
        ttk.Label(status_grid, textvariable=self.last_announcement_var, wraplength=300).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Statistics
        ttk.Label(status_grid, text="Announcements Today:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=2)
        self.announcements_today_var = tk.StringVar(value="0")
        ttk.Label(status_grid, textvariable=self.announcements_today_var).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Interval setting
        ttk.Label(status_grid, text="Check Interval:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=2)
        self.interval_var = tk.StringVar(value="30")
        interval_frame = ttk.Frame(status_grid)
        interval_frame.grid(row=4, column=1, sticky='w', padx=(10, 0), pady=2)
        
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=8)
        interval_entry.pack(side='left')
        ttk.Label(interval_frame, text="seconds").pack(side='left', padx=(5, 0))
        ttk.Button(interval_frame, text="Update", command=self.update_interval).pack(side='left', padx=(5, 0))
    
    def create_controls_section(self, parent):
        """Create quick controls section"""
        controls = [
            ("Start System", self.start_announcement_system, 'green'),
            ("Stop System", self.stop_announcement_system, 'red'),
            ("Test Announcement", self.test_announcement_system, 'blue'),
            ("Refresh Status", self.refresh_status, 'orange'),
            ("Clear Log", self.clear_announcement_log, 'gray')
        ]
        
        for i, (text, command, color) in enumerate(controls):
            btn = ttk.Button(parent, text=text, command=command)
            btn.pack(fill='x', pady=2)
    
    def create_manual_announcement_section(self, parent):
        """Create manual announcement section"""
        # Patient selection for announcement
        patient_frame = ttk.Frame(parent)
        patient_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(patient_frame, text="Patient:").pack(side='left', padx=(0, 5))
        self.manual_patient_var = tk.StringVar()
        self.manual_patient_combo = ttk.Combobox(patient_frame, textvariable=self.manual_patient_var, width=30)
        self.manual_patient_combo.pack(side='left', padx=(0, 10))
        
        ttk.Button(patient_frame, text="Refresh Patients", 
                  command=self.refresh_patient_list).pack(side='left', padx=(0, 10))
        
        # Pre-defined announcement types
        preset_frame = ttk.Frame(parent)
        preset_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(preset_frame, text="Quick Announcements:").pack(side='left', padx=(0, 5))
        
        preset_buttons = [
            ("Call Next Patient", self.call_next_patient),
            ("Consultation Complete", self.announce_consultation_complete),
            ("Prescription Ready", self.announce_prescription_ready),
            ("Report to Reception", self.announce_report_reception)
        ]
        
        for text, command in preset_buttons:
            ttk.Button(preset_frame, text=text, command=command).pack(side='left', padx=2)
        
        # Custom announcement
        custom_frame = ttk.Frame(parent)
        custom_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(custom_frame, text="Custom Message:").pack(anchor='w')
        
        message_frame = ttk.Frame(custom_frame)
        message_frame.pack(fill='x', pady=5)
        
        self.custom_message_text = tk.Text(message_frame, height=3, width=50)
        custom_scrollbar = ttk.Scrollbar(message_frame, orient='vertical', command=self.custom_message_text.yview)
        self.custom_message_text.configure(yscrollcommand=custom_scrollbar.set)
        
        self.custom_message_text.pack(side='left', fill='both', expand=True)
        custom_scrollbar.pack(side='right', fill='y')
        
        # Custom announcement buttons
        custom_btn_frame = ttk.Frame(custom_frame)
        custom_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(custom_btn_frame, text="Make Custom Announcement", 
                  command=self.make_custom_announcement).pack(side='left', padx=(0, 5))
        ttk.Button(custom_btn_frame, text="Clear Message", 
                  command=lambda: self.custom_message_text.delete('1.0', tk.END)).pack(side='left')
    
    def create_log_section(self, parent):
        """Create announcement log section"""
        # Log display
        self.log_text = tk.Text(parent, wrap='word', height=12, font=('Courier', 9))
        log_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Add initial log entry
        self.add_log_entry("Announcement panel initialized")
    
    def create_activity_section(self, parent):
        """Create queue and activity section"""
        # Current queue
        queue_frame = ttk.LabelFrame(parent, text="Current OPD Queue", padding="5")
        queue_frame.pack(fill='x', pady=(0, 5))
        
        self.queue_listbox = tk.Listbox(queue_frame, height=6)
        queue_scrollbar = ttk.Scrollbar(queue_frame, orient='vertical', command=self.queue_listbox.yview)
        self.queue_listbox.configure(yscrollcommand=queue_scrollbar.set)
        
        self.queue_listbox.pack(side='left', fill='both', expand=True)
        queue_scrollbar.pack(side='right', fill='y')
        
        # Completed patients
        completed_frame = ttk.LabelFrame(parent, text="Completed Today", padding="5")
        completed_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        self.completed_listbox = tk.Listbox(completed_frame, height=6)
        completed_scrollbar = ttk.Scrollbar(completed_frame, orient='vertical', command=self.completed_listbox.yview)
        self.completed_listbox.configure(yscrollcommand=completed_scrollbar.set)
        
        self.completed_listbox.pack(side='left', fill='both', expand=True)
        completed_scrollbar.pack(side='right', fill='y')
        
        # Refresh button
        ttk.Button(parent, text="Refresh Activity", 
                  command=self.refresh_activity).pack(fill='x', pady=5)
    
    def start_monitoring(self):
        """Start monitoring the announcement system"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring the announcement system"""
        self.is_monitoring = False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self.refresh_status()
                self.refresh_activity()
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Error in announcement monitor loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def refresh_status(self):
        """Refresh system status display"""
        try:
            if self.announcement_system:
                status = self.announcement_system.get_announcement_status()
                
                # Update system status
                if status['is_running']:
                    self.system_status_var.set("Active")
                    self.system_status_label.config(foreground='green')
                else:
                    self.system_status_var.set("Inactive")
                    self.system_status_label.config(foreground='red')
                
                # Update TTS status
                if status['tts_available']:
                    self.tts_status_var.set("Available")
                    self.tts_status_label.config(foreground='green')
                else:
                    self.tts_status_var.set("Not Available")
                    self.tts_status_label.config(foreground='orange')
                
                # Update announcements today
                self.announcements_today_var.set(str(status['announced_today']))
                
                # Update interval
                self.interval_var.set(str(status['announcement_interval']))
                
            else:
                self.system_status_var.set("System Unavailable")
                self.system_status_label.config(foreground='red')
                self.tts_status_var.set("Unavailable")
                self.tts_status_label.config(foreground='red')
                
        except Exception as e:
            print(f"Error refreshing status: {e}")
    
    def refresh_activity(self):
        """Refresh queue and activity displays"""
        try:
            # Clear existing items
            self.queue_listbox.delete(0, tk.END)
            self.completed_listbox.delete(0, tk.END)
            
            # Get today's OPD visits
            today_visits = self.data_manager.get_todays_opd_visits()
            
            # Current queue (in progress visits)
            in_progress_visits = [visit for visit in today_visits if visit.status == 'In Progress']
            
            for i, visit in enumerate(in_progress_visits):
                patient = self.data_manager.get_patient_by_id(visit.patient_id)
                patient_name = patient.name if patient else "Unknown Patient"
                
                try:
                    visit_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                    time_str = visit_time.strftime("%H:%M")
                except ValueError:
                    time_str = "Unknown"
                
                self.queue_listbox.insert(tk.END, f"{i+1}. {patient_name} - {visit.doctor_name} ({time_str})")
            
            if not in_progress_visits:
                self.queue_listbox.insert(tk.END, "No patients in queue")
            
            # Completed visits
            completed_visits = [visit for visit in today_visits if visit.status == 'Completed']
            
            for visit in completed_visits:
                patient = self.data_manager.get_patient_by_id(visit.patient_id)
                patient_name = patient.name if patient else "Unknown Patient"
                
                try:
                    visit_time = datetime.strptime(visit.visit_date, "%Y-%m-%d %H:%M:%S")
                    time_str = visit_time.strftime("%H:%M")
                except ValueError:
                    time_str = "Unknown"
                
                self.completed_listbox.insert(tk.END, f"{patient_name} - {visit.doctor_name} ({time_str})")
            
            if not completed_visits:
                self.completed_listbox.insert(tk.END, "No completed consultations today")
                
        except Exception as e:
            print(f"Error refreshing activity: {e}")
    
    def refresh_patient_list(self):
        """Refresh patient list for manual announcements"""
        try:
            patients = self.data_manager.get_patients()
            patient_options = [f"{p.patient_id} - {p.name}" for p in patients]
            self.manual_patient_combo.config(values=patient_options)
        except Exception as e:
            print(f"Error refreshing patient list: {e}")
    
    def start_announcement_system(self):
        """Start the announcement system"""
        try:
            if self.announcement_system:
                self.announcement_system.start_announcement_service()
                self.add_log_entry("Announcement system started")
                messagebox.showinfo("System Control", "Announcement system started successfully!")
            else:
                messagebox.showerror("Error", "Announcement system not available")
        except Exception as e:
            error_msg = f"Failed to start announcement system: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def stop_announcement_system(self):
        """Stop the announcement system"""
        try:
            if self.announcement_system:
                self.announcement_system.stop_announcement_service()
                self.add_log_entry("Announcement system stopped")
                messagebox.showinfo("System Control", "Announcement system stopped successfully!")
            else:
                messagebox.showerror("Error", "Announcement system not available")
        except Exception as e:
            error_msg = f"Failed to stop announcement system: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def test_announcement_system(self):
        """Test the announcement system"""
        try:
            if self.announcement_system:
                success = self.announcement_system.test_announcement(
                    "This is a test announcement from the announcement panel. The system is functioning correctly."
                )
                
                if success:
                    self.add_log_entry("Test announcement completed successfully")
                    messagebox.showinfo("Test", "Test announcement completed successfully!")
                else:
                    self.add_log_entry("Test announcement completed with warnings")
                    messagebox.showwarning("Test", "Test announcement completed with warnings. Check console for details.")
            else:
                messagebox.showerror("Error", "Announcement system not available")
        except Exception as e:
            error_msg = f"Test announcement failed: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def update_interval(self):
        """Update announcement check interval"""
        try:
            interval = int(self.interval_var.get())
            if interval < 10:
                messagebox.showerror("Error", "Interval must be at least 10 seconds")
                return
            
            if self.announcement_system:
                self.announcement_system.set_announcement_interval(interval)
                self.add_log_entry(f"Announcement interval updated to {interval} seconds")
                messagebox.showinfo("Update", f"Announcement interval updated to {interval} seconds")
            else:
                messagebox.showerror("Error", "Announcement system not available")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for interval")
        except Exception as e:
            error_msg = f"Failed to update interval: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def call_next_patient(self):
        """Call next patient in queue"""
        try:
            # Get next patient from queue
            today_visits = self.data_manager.get_todays_opd_visits()
            in_progress_visits = [visit for visit in today_visits if visit.status == 'In Progress']
            
            if not in_progress_visits:
                messagebox.showinfo("Queue", "No patients in queue")
                return
            
            # Get first patient
            next_visit = in_progress_visits[0]
            patient = self.data_manager.get_patient_by_id(next_visit.patient_id)
            
            if patient and self.announcement_system:
                self.announcement_system.announce_patient_call(patient.name)
                self.add_log_entry(f"Called next patient: {patient.name}")
                self.last_announcement_var.set(f"Patient call: {patient.name}")
                messagebox.showinfo("Patient Called", f"Called patient: {patient.name}")
            else:
                messagebox.showinfo("Patient Called", "Next patient has been called")
                
        except Exception as e:
            error_msg = f"Error calling next patient: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def announce_consultation_complete(self):
        """Announce consultation complete for selected patient"""
        patient_selection = self.manual_patient_var.get().strip()
        
        if not patient_selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return
        
        try:
            patient_id = patient_selection.split(' - ')[0]
            patient = self.data_manager.get_patient_by_id(patient_id)
            
            if patient and self.announcement_system:
                message = f"Patient {patient.name}, your consultation is complete. Please collect your prescription from the front desk."
                self.announcement_system.add_manual_announcement(patient.name, message)
                self.add_log_entry(f"Consultation complete announcement: {patient.name}")
                self.last_announcement_var.set(f"Consultation complete: {patient.name}")
                messagebox.showinfo("Announcement", f"Announced consultation complete for {patient.name}")
            else:
                messagebox.showerror("Error", "Patient not found or announcement system unavailable")
                
        except Exception as e:
            error_msg = f"Error making consultation complete announcement: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def announce_prescription_ready(self):
        """Announce prescription ready for selected patient"""
        patient_selection = self.manual_patient_var.get().strip()
        
        if not patient_selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return
        
        try:
            patient_id = patient_selection.split(' - ')[0]
            patient = self.data_manager.get_patient_by_id(patient_id)
            
            if patient and self.announcement_system:
                message = f"Patient {patient.name}, your prescription is ready for collection at the pharmacy counter."
                self.announcement_system.add_manual_announcement(patient.name, message)
                self.add_log_entry(f"Prescription ready announcement: {patient.name}")
                self.last_announcement_var.set(f"Prescription ready: {patient.name}")
                messagebox.showinfo("Announcement", f"Announced prescription ready for {patient.name}")
            else:
                messagebox.showerror("Error", "Patient not found or announcement system unavailable")
                
        except Exception as e:
            error_msg = f"Error making prescription ready announcement: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def announce_report_reception(self):
        """Announce patient to report to reception"""
        patient_selection = self.manual_patient_var.get().strip()
        
        if not patient_selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return
        
        try:
            patient_id = patient_selection.split(' - ')[0]
            patient = self.data_manager.get_patient_by_id(patient_id)
            
            if patient and self.announcement_system:
                message = f"Patient {patient.name}, please report to the reception desk for assistance."
                self.announcement_system.add_manual_announcement(patient.name, message)
                self.add_log_entry(f"Report to reception announcement: {patient.name}")
                self.last_announcement_var.set(f"Report to reception: {patient.name}")
                messagebox.showinfo("Announcement", f"Announced report to reception for {patient.name}")
            else:
                messagebox.showerror("Error", "Patient not found or announcement system unavailable")
                
        except Exception as e:
            error_msg = f"Error making report to reception announcement: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def make_custom_announcement(self):
        """Make custom announcement"""
        patient_selection = self.manual_patient_var.get().strip()
        custom_message = self.custom_message_text.get('1.0', tk.END).strip()
        
        if not patient_selection:
            messagebox.showwarning("Warning", "Please select a patient")
            return
        
        if not custom_message:
            messagebox.showwarning("Warning", "Please enter a custom message")
            return
        
        try:
            patient_id = patient_selection.split(' - ')[0]
            patient = self.data_manager.get_patient_by_id(patient_id)
            
            if patient and self.announcement_system:
                full_message = f"Patient {patient.name}, {custom_message}"
                self.announcement_system.add_manual_announcement(patient.name, full_message)
                self.add_log_entry(f"Custom announcement for {patient.name}: {custom_message}")
                self.last_announcement_var.set(f"Custom: {patient.name}")
                messagebox.showinfo("Announcement", f"Made custom announcement for {patient.name}")
                
                # Clear the message
                self.custom_message_text.delete('1.0', tk.END)
            else:
                messagebox.showerror("Error", "Patient not found or announcement system unavailable")
                
        except Exception as e:
            error_msg = f"Error making custom announcement: {str(e)}"
            self.add_log_entry(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def clear_announcement_log(self):
        """Clear the announcement log"""
        result = messagebox.askyesno("Clear Log", "Clear the announcement log?")
        if result:
            self.log_text.delete('1.0', tk.END)
            self.add_log_entry("Announcement log cleared")
    
    def add_log_entry(self, message):
        """Add entry to announcement log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.update()
        
        # Keep log size manageable (last 100 lines)
        lines = self.log_text.get('1.0', tk.END).count('\n')
        if lines > 100:
            # Remove first 20 lines
            for _ in range(20):
                self.log_text.delete('1.0', '2.0')
    
    def refresh(self):
        """Refresh all announcement panel data"""
        self.refresh_status()
        self.refresh_activity()
        self.refresh_patient_list()
