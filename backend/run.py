#!/usr/bin/env python3
"""
Simple script to run the BuzzBrief backend server
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add the backend directory to Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, backend_dir)
    
    # Set Supabase environment variables
    os.environ['SUPABASE_URL'] = 'https://ousfnryoohuxwhbhagdw.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im91c2Zucnlvb2h1eHdoYmhhZ2R3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5NTgxMzUsImV4cCI6MjA3NDUzNDEzNX0.fRUb-ZrSIMVBqHYwh79F85PtuzeP4TRr33Ufc0ssOCM'
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        reload_dirs=[backend_dir]
    )
