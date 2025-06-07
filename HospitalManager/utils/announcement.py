"""
Announcement System - Handles patient name announcements
"""

import threading
import time
from typing import List, Dict, Callable
from datetime import datetime

class AnnouncementSystem:
    """System for announcing patient names when visits are completed"""
    
    def __init__(self, data_manager, announcement_callback: Callable = None):
        """Initialize announcement system"""
        self.data_manager = data_manager
        self.announcement_callback = announcement_callback or self._default_announcement
        self.is_running = False
        self.announcement_thread = None
        self.pending_announcements = []
        self.announced_patients = set()
        self.announcement_interval = 30  # seconds
        
        # Try to import text-to-speech if available
        self.tts_available = False
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            # Configure TTS settings
            self.tts_engine.setProperty('rate', 150)    # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use the first available voice
                self.tts_engine.setProperty('voice', voices[0].id)
            self.tts_available = True
        except ImportError:
            print("Text-to-speech not available. Using callback method only.")
            self.tts_engine = None
    
    def _default_announcement(self, message: str):
        """Default announcement method - prints to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ANNOUNCEMENT: {message}")
    
    def start_announcement_service(self):
        """Start the announcement service in a separate thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.announcement_thread = threading.Thread(target=self._announcement_loop, daemon=True)
        self.announcement_thread.start()
        print("Announcement service started")
    
    def stop_announcement_service(self):
        """Stop the announcement service"""
        self.is_running = False
        if self.announcement_thread and self.announcement_thread.is_alive():
            self.announcement_thread.join(timeout=5)
        print("Announcement service stopped")
    
    def _announcement_loop(self):
        """Main announcement loop running in background thread"""
        while self.is_running:
            try:
                self._check_and_announce_completed_patients()
                time.sleep(self.announcement_interval)
            except Exception as e:
                print(f"Error in announcement loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _check_and_announce_completed_patients(self):
        """Check for completed patients and announce them"""
        # Get today's completed OPD visits
        today_visits = self.data_manager.get_todays_opd_visits()
        completed_visits = [visit for visit in today_visits if visit.status == "Completed"]
        
        for visit in completed_visits:
            # Check if this patient has already been announced
            announcement_key = f"{visit.patient_id}_{visit.visit_id}"
            if announcement_key not in self.announced_patients:
                # Get patient details
                patient = self.data_manager.get_patient_by_id(visit.patient_id)
                if patient:
                    self._announce_patient_completion(patient.name, visit.doctor_name)
                    self.announced_patients.add(announcement_key)
    
    def _announce_patient_completion(self, patient_name: str, doctor_name: str):
        """Announce that a patient's consultation is complete"""
        message = f"Patient {patient_name} consultation with {doctor_name} is complete. Please collect your prescription from the front desk."
        
        # Use callback method
        self.announcement_callback(message)
        
        # Use text-to-speech if available
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
    
    def add_manual_announcement(self, patient_name: str, custom_message: str = None):
        """Manually add a patient for announcement"""
        message = custom_message or f"Patient {patient_name}, please proceed to the front desk."
        
        # Announce immediately
        self.announcement_callback(message)
        
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
    
    def announce_patient_call(self, patient_name: str, room_number: str = None):
        """Announce patient call for appointment"""
        if room_number:
            message = f"Patient {patient_name}, please report to room {room_number} for your appointment."
        else:
            message = f"Patient {patient_name}, please report to the consultation room for your appointment."
        
        self.announcement_callback(message)
        
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
    
    def announce_queue_update(self, patient_name: str, position: int):
        """Announce queue position update"""
        if position == 1:
            message = f"Patient {patient_name}, you are next in line."
        else:
            message = f"Patient {patient_name}, you are number {position} in the queue."
        
        self.announcement_callback(message)
        
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
    
    def set_announcement_interval(self, interval_seconds: int):
        """Set the announcement check interval"""
        self.announcement_interval = max(10, interval_seconds)  # Minimum 10 seconds
    
    def clear_announced_patients(self):
        """Clear the list of announced patients (usually done daily)"""
        self.announced_patients.clear()
        print("Announced patients list cleared")
    
    def get_announcement_status(self) -> Dict:
        """Get current announcement system status"""
        return {
            'is_running': self.is_running,
            'tts_available': self.tts_available,
            'announcement_interval': self.announcement_interval,
            'announced_today': len(self.announced_patients),
            'pending_announcements': len(self.pending_announcements)
        }
    
    def test_announcement(self, test_message: str = None):
        """Test the announcement system"""
        message = test_message or "This is a test announcement. The announcement system is working properly."
        
        self.announcement_callback(f"TEST: {message}")
        
        if self.tts_available and self.tts_engine:
            try:
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
                return True
            except Exception as e:
                print(f"TTS test failed: {e}")
                return False
        return True

class AnnouncementQueue:
    """Queue management for patient announcements"""
    
    def __init__(self):
        """Initialize announcement queue"""
        self.queue = []
        self.current_position = 0
    
    def add_to_queue(self, patient_name: str, patient_id: str, priority: int = 0):
        """Add patient to announcement queue"""
        announcement_item = {
            'patient_name': patient_name,
            'patient_id': patient_id,
            'priority': priority,
            'added_at': datetime.now(),
            'announced': False
        }
        
        # Insert based on priority (higher priority first)
        inserted = False
        for i, item in enumerate(self.queue):
            if priority > item['priority']:
                self.queue.insert(i, announcement_item)
                inserted = True
                break
        
        if not inserted:
            self.queue.append(announcement_item)
    
    def get_next_announcement(self) -> Dict:
        """Get next patient to announce"""
        for item in self.queue:
            if not item['announced']:
                return item
        return None
    
    def mark_announced(self, patient_id: str):
        """Mark patient as announced"""
        for item in self.queue:
            if item['patient_id'] == patient_id and not item['announced']:
                item['announced'] = True
                item['announced_at'] = datetime.now()
                break
    
    def remove_from_queue(self, patient_id: str):
        """Remove patient from queue"""
        self.queue = [item for item in self.queue if item['patient_id'] != patient_id]
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        total = len(self.queue)
        announced = sum(1 for item in self.queue if item['announced'])
        pending = total - announced
        
        return {
            'total_in_queue': total,
            'announced': announced,
            'pending': pending,
            'queue_items': self.queue
        }
    
    def clear_queue(self):
        """Clear the entire queue"""
        self.queue.clear()
        self.current_position = 0
