#!/usr/bin/env python3
"""
Script to clear all stored tickets and reset the database
"""

import os
import sqlite3
import shutil
from pathlib import Path

def clear_all_tickets():
    print("🗑️ Clearing all stored tickets...")
    
    # Database paths
    db_paths = [
        'storage/tickets.db',
        'ticket_storage/tickets.db',
        'ticket_storage.db'
    ]
    
    # Clear databases
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Deleting database: {db_path}")
            os.remove(db_path)
    
    # Clear storage directories
    storage_dirs = [
        'storage',
        'ticket_storage',
        'analysis_outputs',
        'logs'
    ]
    
    for storage_dir in storage_dirs:
        if os.path.exists(storage_dir):
            print(f"Clearing directory: {storage_dir}")
            shutil.rmtree(storage_dir)
    
    # Recreate directories
    for storage_dir in storage_dirs:
        os.makedirs(storage_dir, exist_ok=True)
        print(f"Created directory: {storage_dir}")
    
    print("✅ All stored tickets cleared successfully!")
    print("✅ Database reset complete!")
    print("✅ Storage directories recreated!")

if __name__ == "__main__":
    clear_all_tickets()
