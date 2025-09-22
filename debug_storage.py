#!/usr/bin/env python3

import json
from ticket_storage_system import TicketStorageSystem

# Create test data similar to what the app is sending
test_data = {
    "id": "TEST-123",
    "ticket_key": "TEST-123", 
    "title": "Test Title",
    "description": "Test Description",
    "questions": ["Question 1", "Question 2"],
    "test_cases": ["Test case 1", "Test case 2"],
    "analysis": {
        "suggested_questions": ["Q1", "Q2"],
        "design_questions": ["DQ1", "DQ2"],
        "business_questions": ["BQ1"],
        "technical_considerations": ["TC1"],
        "risk_areas": ["Risk 1"],
        "test_cases": ["TC1", "TC2"],
        "figma_designs": [],
        "pdf_designs": []
    },
    "report": "Test report content"
}

print("Test data types:")
for key, value in test_data.items():
    print(f"  {key}: {type(value)} = {value}")

print("\nTesting storage...")
storage = TicketStorageSystem()

try:
    result = storage.store_ticket(test_data)
    print(f"✅ Storage successful: {result}")
except Exception as e:
    print(f"❌ Storage failed: {e}")
    import traceback
    traceback.print_exc()
