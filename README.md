# Python Project: File Conversion and Processing Tool

This repository contains a Python-based tool designed to process and convert `.ct` and `.csv` files for game data management.

---

## Features

### Key Functionalities:
- **File Conversion**: Automatically detects and converts `.ct` files to `.csv` format and vice versa.
- **Batch Processing**: Supports folder-level operations to process all `.ct` files in a directory.
- **Custom Delimiters**: Allows specifying delimiters (e.g., `||`) for `.csv` file handling.
- **Logging and Error Management**: Provides detailed logs and error handling to ensure smooth operations.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/JordanRO2/RO2_Toolkits.git
   cd RO2_Toolkits
   ```

---

## Usage

### Process a Single File
To process a `.ct` or `.csv` file, provide its path:
```bash
python main.py <file_path>
```

### Process All `.ct` Files in a Folder
To process an entire folder of `.ct` files:
```bash
python main.py <folder_path>
```

### Specify a Custom Delimiter
To use a custom delimiter for `.csv` files (default is `||`):
```bash
python main.py <file_or_folder_path> --delimiter "<custom_delimiter>"
```

---

## Project Structure

```plaintext
.
├── asset
│   ├── csv_processor.py   # Handles CSV file reading and writing.
│   ├── ct_processor.py    # Handles CT file reading and writing.
├── main.py                # Main entry point for processing files.
├── README.md              # Project documentation.
```

---

## Logging Example

Logs provide insights into operations and errors:
```plaintext
2023-12-28 14:23:10 - INFO - Converted CT to CSV: /path/to/Attendance_converted.csv
2023-12-28 14:23:15 - ERROR - File not found: /path/to/missing_file.ct
```

---

## Contributing

Contributions are welcome! Please submit pull requests or report issues in the repository's issue tracker.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
