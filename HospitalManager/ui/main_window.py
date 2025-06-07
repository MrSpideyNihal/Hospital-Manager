"""
Main Window - Hospital Management System GUI Main Window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Import UI modules
from ui.patient_management import PatientManagementFrame
from ui.appointment_scheduling import AppointmentSchedulingFrame
from ui.opd_management import OPDManagementFrame
from ui.reporting import ReportingFrame
from ui.announcement_panel import AnnouncementPanelFrame

# Import utility modules
from utils.announcement import AnnouncementSystem

class MainWindow:
    """Main application window with navigation and module management"""
    
    def __init__(self, root, data_manager):
        """Initialize main window"""
        self.root = root
        self.data_manager = data_manager
        self.current_frame = None
        
        # Initialize announcement system
        self.announcement_system = AnnouncementSystem(
            data_manager, 
            self.display_announcement
        )
        
        self.setup_window()
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # Show patient management by default
        self.show_patient_management()
        
        # Start announcement system
        self.announcement_system.start_announcement_service()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Hospital Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Navigation.TButton', padding=(10, 5))
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Create Backup", command=self.create_backup)
        file_menu.add_command(label="Restore Backup", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Modules", menu=view_menu)
        view_menu.add_command(label="Patient Management", command=self.show_patient_management)
        view_menu.add_command(label="Appointment Scheduling", command=self.show_appointment_scheduling)
        view_menu.add_command(label="OPD Management", command=self.show_opd_management)
        view_menu.add_command(label="Reports", command=self.show_reporting)
        view_menu.add_command(label="Announcements", command=self.show_announcement_panel)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test Announcement", command=self.test_announcement)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_statistics)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Announcements", command=self.clear_announcements)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
    
    def create_main_layout(self):
        """Create main window layout"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create navigation frame
        nav_frame = ttk.LabelFrame(main_container, text="Navigation", padding="10")
        nav_frame.pack(fill='x', pady=(0, 5))
        
        # Navigation buttons
        nav_buttons = [
            ("Patient Management", self.show_patient_management),
            ("Appointments", self.show_appointment_scheduling),
            ("OPD Management", self.show_opd_management),
            ("Reports", self.show_reporting),
            ("Announcements", self.show_announcement_panel)
        ]
        
        for i, (text, command) in enumerate(nav_buttons):
            btn = ttk.Button(nav_frame, text=text, command=command, 
                           style='Navigation.TButton')
            btn.pack(side='left', padx=(0, 10))
        
        # Create content frame
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(fill='both', expand=True)
        
        # Create announcement display frame
        self.announcement_frame = ttk.LabelFrame(main_container, text="Latest Announcement", 
                                               padding="5")
        self.announcement_frame.pack(fill='x', pady=(5, 0))
        
        self.announcement_label = ttk.Label(self.announcement_frame, 
                                          text="No announcements yet...", 
                                          foreground='blue')
        self.announcement_label.pack()
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', side='bottom')
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side='left', padx=5)
        
        # Announcement status
        self.announcement_status_label = ttk.Label(self.status_frame, 
                                                  text="Announcements: Active")
        self.announcement_status_label.pack(side='right', padx=5)
        
        # Update status periodically
        self.update_status()
    
    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_frame = None
    
    def show_patient_management(self):
        """Show patient management module"""
        self.clear_content_frame()
        self.current_frame = PatientManagementFrame(self.content_frame, self.data_manager)
        self.status_label.config(text="Patient Management")
    
    def show_appointment_scheduling(self):
        """Show appointment scheduling module"""
        self.clear_content_frame()
        self.current_frame = AppointmentSchedulingFrame(self.content_frame, self.data_manager)
        self.status_label.config(text="Appointment Scheduling")
    
    def show_opd_management(self):
        """Show OPD management module"""
        self.clear_content_frame()
        self.current_frame = OPDManagementFrame(self.content_frame, self.data_manager, 
                                              self.announcement_system)
        self.status_label.config(text="OPD Management")
    
    def show_reporting(self):
        """Show reporting module"""
        self.clear_content_frame()
        self.current_frame = ReportingFrame(self.content_frame, self.data_manager)
        self.status_label.config(text="Reports")
    
    def show_announcement_panel(self):
        """Show announcement panel"""
        self.clear_content_frame()
        self.current_frame = AnnouncementPanelFrame(self.content_frame, self.data_manager, 
                                                   self.announcement_system)
        self.status_label.config(text="Announcement Panel")
    
    def display_announcement(self, message):
        """Display announcement in the main window"""
        self.announcement_label.config(text=message)
        self.root.update_idletasks()
        
        # Auto-clear after 30 seconds
        self.root.after(30000, lambda: self.announcement_label.config(text="No announcements yet..."))
    
    def update_status(self):
        """Update status bar information"""
        try:
            # Update announcement system status
            status = self.announcement_system.get_announcement_status()
            if status['is_running']:
                self.announcement_status_label.config(text="Announcements: Active")
            else:
                self.announcement_status_label.config(text="Announcements: Inactive")
            
            # Schedule next update
            self.root.after(5000, self.update_status)
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def create_backup(self):
        """Create data backup"""
        try:
            success = self.data_manager.create_backup()
            if success:
                messagebox.showinfo("Backup", "Backup created successfully!")
            else:
                messagebox.showerror("Backup", "Failed to create backup!")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Error creating backup:\n{str(e)}")
    
    def restore_backup(self):
        """Restore data from backup"""
        from tkinter import filedialog
        
        try:
            # Get backup files
            backup_files = self.data_manager.get_backup_files()
            
            if not backup_files:
                messagebox.showinfo("Restore", "No backup files found!")
                return
            
            # Ask user to select backup file
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
                        messagebox.showinfo("Restore", "Data restored successfully!")
                        # Refresh current view
                        if hasattr(self.current_frame, 'refresh'):
                            self.current_frame.refresh()
                    else:
                        messagebox.showerror("Restore", "Failed to restore backup!")
        except Exception as e:
            messagebox.showerror("Restore Error", f"Error restoring backup:\n{str(e)}")
    
    def show_settings(self):
        """Show application settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (200)
        y = (settings_window.winfo_screenheight() // 2) - (150)
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Settings form
        main_frame = ttk.Frame(settings_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Hospital name
        ttk.Label(main_frame, text="Hospital Name:").grid(row=0, column=0, sticky='w', pady=5)
        hospital_name_var = tk.StringVar(value=self.data_manager.get_setting('hospital_name', 'City Hospital'))
        hospital_name_entry = ttk.Entry(main_frame, textvariable=hospital_name_var, width=30)
        hospital_name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Announcement settings
        ttk.Label(main_frame, text="Enable Announcements:").grid(row=1, column=0, sticky='w', pady=5)
        announcement_var = tk.BooleanVar(value=self.data_manager.get_setting('announcement_enabled', True))
        announcement_check = ttk.Checkbutton(main_frame, variable=announcement_var)
        announcement_check.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Announcement interval
        ttk.Label(main_frame, text="Announcement Interval (seconds):").grid(row=2, column=0, sticky='w', pady=5)
        interval_var = tk.StringVar(value=str(self.data_manager.get_setting('announcement_interval', 30)))
        interval_entry = ttk.Entry(main_frame, textvariable=interval_var, width=10)
        interval_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Auto backup
        ttk.Label(main_frame, text="Enable Auto Backup:").grid(row=3, column=0, sticky='w', pady=5)
        backup_var = tk.BooleanVar(value=self.data_manager.get_setting('auto_backup_enabled', True))
        backup_check = ttk.Checkbutton(main_frame, variable=backup_var)
        backup_check.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_settings():
            try:
                # Validate interval
                interval = int(interval_var.get())
                if interval < 10:
                    raise ValueError("Interval must be at least 10 seconds")
                
                # Save settings
                settings = {
                    'hospital_name': hospital_name_var.get(),
                    'announcement_enabled': announcement_var.get(),
                    'announcement_interval': interval,
                    'auto_backup_enabled': backup_var.get()
                }
                
                self.data_manager.save_settings(settings)
                
                # Update announcement system
                self.announcement_system.set_announcement_interval(interval)
                
                messagebox.showinfo("Settings", "Settings saved successfully!")
                settings_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Settings Error", f"Invalid value: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side='left', padx=5)
    
    def test_announcement(self):
        """Test the announcement system"""
        test_message = "This is a test announcement. The system is working correctly."
        success = self.announcement_system.test_announcement(test_message)
        
        if success:
            messagebox.showinfo("Test", "Announcement test completed successfully!")
        else:
            messagebox.showwarning("Test", "Announcement test completed with warnings. Check console for details.")
    
    def show_data_statistics(self):
        """Show data statistics"""
        stats = self.data_manager.get_data_statistics()
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Data Statistics")
        stats_window.geometry("300x250")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Center the window
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (150)
        y = (stats_window.winfo_screenheight() // 2) - (125)
        stats_window.geometry(f"300x250+{x}+{y}")
        
        main_frame = ttk.Frame(stats_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Data Statistics", style='Title.TLabel').pack(pady=(0, 10))
        
        # Display statistics
        for key, value in stats.items():
            display_key = key.replace('_', ' ').title()
            ttk.Label(main_frame, text=f"{display_key}: {value}").pack(anchor='w', pady=2)
        
        ttk.Button(main_frame, text="Close", command=stats_window.destroy).pack(pady=10)
    
    def clear_announcements(self):
        """Clear announced patients list"""
        result = messagebox.askyesno("Clear Announcements", 
                                   "Clear the list of announced patients for today?")
        if result:
            self.announcement_system.clear_announced_patients()
            messagebox.showinfo("Clear Announcements", "Announced patients list cleared!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Hospital Management System v1.0

A comprehensive offline hospital management system for:
• Patient Management
• Appointment Scheduling  
• OPD Operations
• Reporting & Analytics
• Patient Announcements

Developed with Python and Tkinter
All data stored locally - no internet required

© 2024 Hospital Management System"""
        
        messagebox.showinfo("About", about_text)
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """Quick User Guide:

1. Patient Management: Register new patients, edit information, search records
2. Appointments: Schedule, reschedule, and manage patient appointments
3. OPD Management: Handle walk-in patients, record consultations
4. Reports: Generate various reports and export data
5. Announcements: Manage patient announcements and notifications

Navigation: Use the buttons at the top or the Modules menu

For backup: Use File > Create Backup regularly
For settings: Use File > Settings to configure the system

The announcement system automatically announces completed consultations."""
        
        messagebox.showinfo("User Guide", guide_text)
    
    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit the Hospital Management System?"):
            # Stop announcement system
            self.announcement_system.stop_announcement_service()
            
            # Auto backup if enabled
            if self.data_manager.get_setting('auto_backup_enabled', True):
                try:
                    self.data_manager.create_backup()
                except Exception as e:
                    print(f"Auto backup failed: {e}")
            
            self.root.destroy()
