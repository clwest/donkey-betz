#!/usr/bin/env python
"""
Python Developer
Generated for job: rok_1096950 on 2025-09-21 05:06:39
"""

import uuid
from datetime import datetime

class ChargingSession:
    """Class to represent a charging session for an electric vehicle."""
    
    def __init__(self, vehicle_id):
        self.session_id = str(uuid.uuid4())  # Unique identifier for the session
        self.vehicle_id = vehicle_id
        self.start_time = None
        self.end_time = None
        self.status = 'stopped'  # Possible values: 'stopped', 'charging'

    def start(self):
        """Start the charging session."""
        if self.status == 'charging':
            raise RuntimeError("Charging session is already in progress.")
        self.start_time = datetime.now()
        self.status = 'charging'
        print(f"Charging session {self.session_id} started for vehicle {self.vehicle_id} at {self.start_time}.")

    def stop(self):
        """Stop the charging session."""
        if self.status == 'stopped':
            raise RuntimeError("No charging session is currently in progress.")
        self.end_time = datetime.now()
        self.status = 'stopped'
        print(f"Charging session {self.session_id} stopped for vehicle {self.vehicle_id} at {self.end_time}.")

    def get_status(self):
        """Get the current status of the charging session."""
        return {
            'session_id': self.session_id,
            'vehicle_id': self.vehicle_id,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

def main():
    """Main function to demonstrate the ChargingSession functionality."""
    try:
        # Example vehicle ID
        vehicle_id = "EV12345"
        
        # Create a new charging session
        session = ChargingSession(vehicle_id)
        
        # Start the charging session
        session.start()
        
        # Get and print the status of the charging session
        status = session.get_status()
        print(status)
        
        # Stop the charging session
        session.stop()
        
        # Get and print the final status of the charging session
        final_status = session.get_status()
        print(final_status)

    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()