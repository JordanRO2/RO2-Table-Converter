#!/bin/bash

# RO2 Table Converter - Linux/Unix Setup Script
# Community tool for converting RO2 CT files to Excel format

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_banner() {
    echo -e ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW} RO2 Table Converter - Community Tool${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo -e ""
}

show_help() {
    show_banner
    echo -e "${GREEN}USAGE:${NC}"
    echo -e "  ./setup.sh install    Install dependencies"
    echo -e "  ./setup.sh run        Start the web interface"
    echo -e "  ./setup.sh help       Show this help"
    echo -e ""
    echo -e "${GREEN}REQUIREMENTS:${NC}"
    echo -e "  - Python 3.8 or higher"
    echo -e "  - pip (Python package manager)"
    echo -e ""
    echo -e "${GREEN}REPOSITORY:${NC}"
    echo -e "  ${BLUE}https://github.com/JordanRO2/RO2-Table-Converter${NC}"
    echo -e ""
    echo -e "${CYAN}This is a community-driven tool for Ragnarok Online 2${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
        echo -e "${YELLOW}💡 Please install Python 3.8 or higher${NC}"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "${CYAN}🐍 Found Python ${python_version}${NC}"
    
    # Check if version is >= 3.8
    if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        echo -e "${RED}❌ Python 3.8 or higher is required${NC}"
        echo -e "${YELLOW}💡 Current version: ${python_version}${NC}"
        exit 1
    fi
}

install_dependencies() {
    show_banner
    echo -e "${YELLOW}🔧 Installing dependencies...${NC}"
    
    check_python
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${CYAN}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo -e "${CYAN}🔄 Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Upgrade pip
    echo -e "${CYAN}⬆️  Upgrading pip...${NC}"
    pip install --upgrade pip
    
    # Install dependencies
    echo -e "${CYAN}📥 Installing required packages...${NC}"
    pip install -r requirements.txt
    
    echo -e ""
    echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
    echo -e "${YELLOW}💡 Run './setup.sh run' to start the web interface${NC}"
}

run_application() {
    show_banner
    echo -e "${GREEN}🚀 Starting RO2 Table Converter...${NC}"
    echo -e "${CYAN}📍 Web interface: http://localhost:5000${NC}"
    echo -e "${YELLOW}⏹️  Press Ctrl+C to stop${NC}"
    echo -e ""
    
    check_python
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Virtual environment not found${NC}"
        echo -e "${YELLOW}💡 Run './setup.sh install' first${NC}"
        exit 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if Flask is installed
    if ! python3 -c 'import flask' 2>/dev/null; then
        echo -e "${RED}❌ Dependencies not installed${NC}"
        echo -e "${YELLOW}💡 Run './setup.sh install' first${NC}"
        exit 1
    fi
    
    # Run the application
    python3 app.py
}

# Make script executable
chmod +x "$0"

# Main script logic
case "${1:-help}" in
    "install")
        install_dependencies
        ;;
    "run")
        run_application
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
