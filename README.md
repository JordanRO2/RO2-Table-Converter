# RO2 Table Converter - Community Tool

> Community-driven tool for Ragnarok Online 2 Compiled Table (CT) file conversion

## Overview

Community-developed tool for converting between Ragnarok Online 2's proprietary CT (Compiled Table) format and Excel spreadsheets. Created by RO2 enthusiasts and community members working to revitalize the game through private servers, client modifications, and community initiatives. 

This project represents the collaborative efforts of passionate players dedicated to preserving and improving RO2. We welcome collaboration with Gravity Interactive, WarpPortal, and all community members interested in keeping RO2 alive and thriving.

## Functionality

### Conversion Capabilities
- **Bidirectional Conversion**: CT ↔ Excel with complete data preservation
- **Type Preservation**: All CT data types maintained during conversion
- **Batch Processing**: Process entire directories of files
- **Data Integrity**: CRC-16 XMODEM checksum validation

### Community Applications
- **Private Server Development**: Extract and modify game data tables
- **Client Modifications**: Edit game content and configurations
- **Data Analysis**: Study game mechanics and balance
- **Content Creation**: Develop custom items, skills, and features
- **Research & Documentation**: Reverse engineer game systems

### Available Interfaces
- **Web Interface**: Browser-based tool with format documentation
- **Command Line**: CLI for automation and scripting
- **Cross-Platform**: Windows, macOS, and Linux compatible

## Setup

### Requirements
- Python 3.8+
- pip package manager

### Installation
```bash
git clone <repository-url>
cd RO2-TableConverter
pip install -r requirements.txt
```

## Usage

### Web Interface
```bash
python app.py
```
Access at `http://localhost:5000` for:
- File conversion via drag-and-drop
- CT file format technical documentation
- Conversion results

### Command Line
```bash
# Convert single files
python main.py CardInfo.ct          # CT → Excel
python main.py CardInfo.xlsx        # Excel → CT

# Convert directories
python main.py ./game_data/         # Process all CT files
```

## CT File Format Specification

### Binary Structure Overview
```
Offset   Size    Description
------   ----    -----------
0x00     16      Magic signature: "RO2SEC!" (UTF-16LE + null)
0x10     var     Timestamp string (UTF-16LE + null)
         var     Padding to 64-byte header boundary
0x40     4       Column count (DWORD)
         var     Column names (STRING array)
         4       Type count (DWORD)  
         var     Type codes (DWORD array)
         4       Row count (DWORD)
         var     Data rows (binary encoded)
EOF-2    2       CRC-16 XMODEM checksum
```

### Header Structure (64 bytes)
- **Magic String**: "RO2SEC!" encoded in UTF-16LE
- **Null Terminator**: 2-byte null terminator after magic
- **Timestamp**: File creation/modification time in UTF-16LE format "YYYY-MM-DD HH:MM:SS"
- **Null Terminator**: 2-byte null terminator after timestamp
- **Padding**: Null bytes to pad header to exactly 64 bytes

### Data Type System
| Code | Type Name  | Size | Struct Format | Description |
|------|------------|------|---------------|-------------|
| 2    | BYTE       | 1    | B             | Unsigned 8-bit integer (0-255) |
| 3    | SHORT      | 2    | h             | Signed 16-bit integer (-32,768 to 32,767) |
| 4    | WORD       | 2    | <H            | Unsigned 16-bit integer (0-65,535) |
| 5    | INT        | 4    | i             | Signed 32-bit integer |
| 6    | DWORD      | 4    | <L            | Unsigned 32-bit integer |
| 7    | DWORD_HEX  | 4    | <L            | DWORD displayed as hexadecimal (0x format) |
| 8    | STRING     | Var  | -             | UTF-16LE string with DWORD length prefix |
| 9    | FLOAT      | 4    | f             | IEEE 754 single precision floating point |
| 11   | INT64      | 8    | <Q            | 64-bit unsigned integer |
| 12   | BOOL       | 1    | B             | Boolean value (0 = false, 1 = true) |

### String Encoding Details
- **Length Prefix**: 4-byte DWORD indicating string length in characters
- **Encoding**: UTF-16LE (Little Endian)
- **Termination**: No null termination within the data (length-prefixed)
- **Empty Strings**: Length = 0, no data bytes follow

### CRC-16 Integrity Check
- **Algorithm**: CRC-16 with XMODEM polynomial (0x1021)
- **Initial Value**: 0x0000
- **Data Coverage**: Only row data (excludes headers and row count)
- **Position**: Last 2 bytes of file
- **Purpose**: Data integrity verification only

### Excel Output Format
- **Row 1**: Data type definitions for each column
- **Row 2**: Column headers/names
- **Row 3+**: Actual data rows
- **Formatting**: Excel table with auto-sized columns and type preservation
- **Metadata**: Original CT timestamp preserved in file properties

## Implementation

### Project Structure
```
RO2-TableConverter/
├── app.py                 # Web interface
├── main.py                # Command line interface
├── asset/
│   ├── ct_processor.py    # CT format handler
│   └── xlsx_processor.py  # Excel processor
├── templates/
│   └── index.html         # Web UI
├── static/                # CSS/JS assets
└── requirements.txt       # Dependencies
```

### Programming Interface

**CT Format Handler:**
```python
from asset.ct_processor import CTProcessor
processor = CTProcessor("file.ct")
data = processor.read()
```

**Excel Handler:**
```python
from asset.xlsx_processor import XLSXProcessor
processor = XLSXProcessor("file.xlsx")
data = processor.read()
```

## Community & Collaboration

This tool is developed by the RO2 community for the RO2 community. Our goals include:

- **Preserving RO2**: Keeping the game alive through community servers and modifications
- **Knowledge Sharing**: Documenting game formats and systems for future developers
- **Open Collaboration**: Working with anyone passionate about RO2's future
- **Official Partnership**: Open to collaboration with Gravity Interactive and WarpPortal

File format specifications are based on community reverse engineering efforts and research into the RO2 client and game data files.

### Contributing

We welcome contributions from:
- **Private Server Developers**: Share improvements and discoveries
- **Client Modders**: Contribute format insights and tools
- **Data Researchers**: Help document game systems and formats
- **RO2 Enthusiasts**: Test tools and provide feedback

### Contact & Collaboration

For collaboration opportunities, including potential partnerships with official RO2 stakeholders, please reach out through our GitHub repository or community channels.

---

**Community Tool Documentation v1.0**  
*Built with ❤️ by the RO2 Community*
