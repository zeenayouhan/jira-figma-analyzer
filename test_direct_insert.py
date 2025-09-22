#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime

# Test direct insert
db_path = "ticket_storage/database/tickets.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

ticket_id = "TEST-789"
title = "Test Title Direct"
description = "Test Description"
analysis_data = json.dumps({"test": "data"})

print(f"Inserting: ticket_id={ticket_id}, title={title}")

try:
    cursor.execute('''
        INSERT OR REPLACE INTO tickets 
        (ticket_id, ticket_key, title, description, created_at, updated_at, analysis_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_id,
        ticket_id, 
        title,
        description,
        datetime.now().isoformat(),
        datetime.now().isoformat(),
        analysis_data
    ))
    
    conn.commit()
    print("✅ Direct insert successful!")
    
except Exception as e:
    print(f"❌ Direct insert failed: {e}")
    import traceback
    traceback.print_exc()

conn.close()
