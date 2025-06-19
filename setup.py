#!/usr/bin/env python3
"""
RO2 Table Converter Setup Script
Community tool for converting RO2 CT files to Excel format

Usage:
    python setup.py install    # Install dependencies
    python setup.py run        # Run the web interface
    python setup.py --help     # Show help
"""

import sys
import subprocess

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_application():
    """Run the Flask web application"""
    print("🚀 Starting RO2 Table Converter...")
    print("📍 Web interface will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError:
        print("❌ Failed to import Flask app. Make sure dependencies are installed.")
        print("💡 Run: python setup.py install")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return True

def show_help():
    """Show help information"""
    help_text = """
🔧 RO2 Table Converter - Setup & Run Script

COMMANDS:
    install     Install required dependencies
    run         Start the web interface
    --help      Show this help message

EXAMPLES:
    python setup.py install    # First-time setup
    python setup.py run        # Start the web server

REQUIREMENTS:
    - Python 3.8 or higher
    - Internet connection (for dependency installation)

REPOSITORY:
    https://github.com/JordanRO2/RO2-Table-Converter

COMMUNITY:
    This is a community-driven tool for Ragnarok Online 2
    Join us in preserving and improving RO2!
    """
    print(help_text)

def main():
    """Main setup script entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_dependencies()
    elif command == "run":
        run_application()
    elif command in ["--help", "-h", "help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
