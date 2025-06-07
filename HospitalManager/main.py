
"""
Hospital Management System - Main Application Entry Point
A comprehensive offline hospital management system with patient management,
appointment scheduling, OPD operations, and reporting capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.data_manager import DataManager

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def main():
    """Main application entry point"""
    try:
        # Create data directory
        create_data_directory()
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Create main window
        root = tk.Tk()
        app = MainWindow(root, data_manager)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Startup Error", 
                           f"Failed to start Hospital Management System:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
