import os
import struct
import logging
from asset.csv_processor import CSVProcessor
from asset.ct_processor import CTProcessor
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def add_converted_suffix(basename: str) -> str:
    """Adds '_converted' to the end of the basename if it isn't already there."""
    return basename if basename.endswith("_converted") else f"{basename}_converted"

def process_file(file_path: str, delimiter="||"):
    """Automatically detects the file type (.ct or .csv) and performs the appropriate conversion."""
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        return

    _, ext = os.path.splitext(file_path)
    file_ext = ext.lower()
    basename = os.path.splitext(file_path)[0]

    if file_ext == ".ct":
        ct = CTProcessor(file_path, verbose=True)
        data = ct.read()
        if not data or not data[0]:
            logger.error(f"Invalid or empty CT file: {file_path}")
            return
        new_file_name = f"{add_converted_suffix(basename)}.csv"
        CSVProcessor(new_file_name, delimiter=delimiter, verbose=True).write(data)
        logger.info(f"Converted CT to CSV: {new_file_name}")

    elif file_ext == ".csv":
        csv_in = CSVProcessor(file_path, delimiter=delimiter, verbose=True)
        data = csv_in.read()
        if not data or not data[0]:
            logger.error(f"Invalid or empty CSV file: {file_path}")
            return
        new_file_name = f"{add_converted_suffix(basename)}.ct"
        CTProcessor(new_file_name, verbose=True).write(data)
        logger.info(f"Converted CSV to CT: {new_file_name}")

    else:
        logger.error("Unsupported file type. Only .ct and .csv files are supported.")

def process_folder(folder_path: str, delimiter="||"):
    """Processes all .ct files in the given folder."""
    if not os.path.isdir(folder_path):
        logger.error(f"Folder not found: {folder_path}")
        return

    ct_files = [f for f in os.listdir(folder_path) if f.endswith(".ct")]
    if not ct_files:
        logger.info("No .ct files found in the folder.")
        return

    for ct_file in ct_files:
        file_path = os.path.join(folder_path, ct_file)
        logger.info(f"Processing file: {file_path}")
        process_file(file_path, delimiter=delimiter)

def main():
    """Main entry point for the program."""
    import sys
    delimiter = "|"  # Default delimiter for CSV files

    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.isfile(arg_path):
            process_file(arg_path, delimiter=delimiter)
        elif os.path.isdir(arg_path):
            process_folder(arg_path, delimiter=delimiter)
        else:
            logger.error("Invalid path provided. Please provide a valid file or folder path.")
    else:
        print("Usage: python main.py <file_or_folder_path>")

if __name__ == "__main__":
    main()
