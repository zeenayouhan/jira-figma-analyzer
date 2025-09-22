#!/usr/bin/env python3
"""
Database Export Endpoint for Railway Production
Add this to your Streamlit app to access database data
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
import io
from datetime import datetime

def database_export_section():
    """Add this section to your Streamlit app for database access"""
    
    st.header("🗄️ Database Export (Production)")
    st.warning("⚠️ This section is for production database access only")
    
    # Database paths
    db_paths = {
        'tickets': 'storage/tickets.db',
        'feedback': 'feedback_storage/feedback.db',
        'confluence': 'confluence_knowledge/database/confluence_docs.db'
    }
    
    # Select database
    selected_db = st.selectbox("Select Database", list(db_paths.keys()))
    db_path = db_paths[selected_db]
    
    if st.button("Check Database Status"):
        try:
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                st.success(f"✅ Database found: {size:,} bytes")
                
                # Show tables
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                st.write("**Tables:**")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    st.write(f"- {table_name}: {count} rows")
                
                conn.close()
            else:
                st.error(f"❌ Database not found: {db_path}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Export options
    st.subheader("Export Data")
    
    if st.button("Export to JSON"):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            export_data = {}
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Convert to list of dictionaries
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                
                export_data[table_name] = table_data
            
            conn.close()
            
            # Create download
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{selected_db}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
    
    # Query interface
    st.subheader("Custom Query")
    query = st.text_area("Enter SQL Query", height=100)
    
    if st.button("Execute Query"):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create DataFrame
                df = pd.DataFrame(results, columns=columns)
                st.dataframe(df)
                
                # Show count
                st.info(f"Found {len(results)} rows")
            else:
                st.info("No results found")
            
            conn.close()
            
        except Exception as e:
            st.error(f"❌ Query failed: {str(e)}")

# Add this to your complete_streamlit_app.py
def add_database_export_to_app():
    """
    Add this function call to your main Streamlit app
    """
    with st.expander("🗄️ Database Export (Production Access)", expanded=False):
        database_export_section()
