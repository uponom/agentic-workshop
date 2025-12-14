#!/usr/bin/env python3
"""
Streamlit Agent Application Launcher

Simple launcher script that can be run from the root directory
to start the Streamlit Agent application.

Usage:
    python launch_streamlit_agent.py [OPTIONS]
    
This script will automatically change to the streamlit_agent directory
and launch the application with the startup script.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Path to the streamlit_agent directory
    streamlit_agent_dir = script_dir / "streamlit_agent"
    
    # Check if streamlit_agent directory exists
    if not streamlit_agent_dir.exists():
        print("Error: streamlit_agent directory not found")
        print(f"Expected location: {streamlit_agent_dir}")
        sys.exit(1)
    
    # Path to the startup script
    startup_script = streamlit_agent_dir / "start.py"
    
    # Check if startup script exists
    if not startup_script.exists():
        print("Error: startup script not found")
        print(f"Expected location: {startup_script}")
        sys.exit(1)
    
    # Change to the streamlit_agent directory
    os.chdir(streamlit_agent_dir)
    
    # Build command to run the startup script
    cmd = [sys.executable, "start.py"] + sys.argv[1:]
    
    print("=" * 60)
    print("  Streamlit Agent Application Launcher")
    print("=" * 60)
    print(f"Working directory: {streamlit_agent_dir}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        # Run the startup script
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nApplication shutdown requested by user")
    except subprocess.CalledProcessError as e:
        print(f"Error: Application failed to start (exit code: {e.returncode})")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error: Unexpected error during startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()