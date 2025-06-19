"""CT File Conversion Tool - Main Entry Point"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
from asset.ct_processor import CTProcessor
from asset.xlsx_processor import XLSXProcessor

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class FileConverter:
    """
    Main file conversion handler for CT2 file format processing.
    
    This class manages the conversion between different file formats while maintaining
    data integrity and type information. It supports both individual file processing
    and batch operations on directories.
    """
    
    SUPPORTED_EXTENSIONS = {'.ct', '.xlsx'}
    
    @staticmethod
    def get_smart_output_name(basename: str, target_extension: str) -> str:
        """
        Generates smart output filename without redundant '_converted' suffix.
        
        Args:
            basename (str): Base filename without extension
            target_extension (str): Target file extension (.xlsx or .ct)
            
        Returns:
            str: Smart output filename
            
        Example:
            >>> FileConverter.get_smart_output_name("CardInfo", ".xlsx")
            "CardInfo.xlsx"
            >>> FileConverter.get_smart_output_name("CardInfo_converted", ".ct")
            "CardInfo.ct"
        """
        # Remove '_converted' suffix if present
        if basename.endswith("_converted"):
            basename = basename[:-10]  # Remove '_converted'
        
        return f"{basename}{target_extension}"
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validates that the file path exists and is accessible.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if file exists and is readable, False otherwise
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and os.access(file_path, os.R_OK)
        except (OSError, PermissionError) as e:
            logger.error(f"File access error for {file_path}: {e}")
            return False
    
    @classmethod
    def process_file(cls, file_path: str) -> bool:
        """
        Automatically detects file type and performs appropriate conversion.
        
        Supported conversions:
        - .ct → .xlsx (CT binary format to Excel)
        - .xlsx → .ct (Excel to CT binary format)
        
        Args:
            file_path (str): Path to the file to process
            
        Returns:
            bool: True if conversion was successful, False otherwise
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            PermissionError: If there are insufficient permissions
            ValueError: If the file format is unsupported
        """
        if not cls.validate_file_path(file_path):
            logger.error(f"File not found or inaccessible: {file_path}")
            return False

        try:
            file_path_obj = Path(file_path)
            file_ext = file_path_obj.suffix.lower()
            basename = file_path_obj.stem
            
            logger.info(f"Processing file: {file_path}")
            
            if file_ext == ".ct":
                return cls._convert_ct_to_xlsx(file_path, basename)
            elif file_ext == ".xlsx":
                return cls._convert_xlsx_to_ct(file_path, basename)
            else:
                logger.error(f"Unsupported file type: {file_ext}. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
            return False
    
    @classmethod
    def _convert_ct_to_xlsx(cls, file_path: str, basename: str) -> bool:
        """Convert CT file to XLSX format."""
        try:
            ct_processor = CTProcessor(file_path, verbose=True)
            data = ct_processor.read()
            
            if not data or not data[0]:
                logger.error(f"Invalid or empty CT file: {file_path}")
                return False
                
            output_path = str(Path(file_path).parent / f"{cls.get_smart_output_name(basename, '.xlsx')}")
            xlsx_processor = XLSXProcessor(output_path, verbose=True)
            xlsx_processor.write(data)
            
            # Preserve the original CT timestamp in the XLSX file's filesystem timestamp
            # Use the CT file's filesystem timestamp to preserve the original file date
            try:
                file_stat = os.stat(file_path)
                os.utime(output_path, (file_stat.st_atime, file_stat.st_mtime))
                print(f"🔍 FileConverter: Preserved original CT file timestamp in XLSX file")
            except Exception as e:
                logger.warning(f"Could not preserve filesystem timestamp in XLSX file: {e}")
                # Fallback: try to use the CT header timestamp if available
                if hasattr(ct_processor, 'file_timestamp') and ct_processor.file_timestamp:
                    try:
                        from datetime import datetime
                        ct_time = datetime.strptime(ct_processor.file_timestamp, "%Y-%m-%d %H:%M:%S")
                        timestamp = ct_time.timestamp()
                        os.utime(output_path, (timestamp, timestamp))
                        print(f"🔍 FileConverter: Used CT header timestamp as fallback: {ct_processor.file_timestamp}")
                    except Exception as e2:
                        logger.warning(f"Could not use CT header timestamp as fallback: {e2}")
            
            logger.info(f"Successfully converted CT to XLSX: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting CT to XLSX: {e}")
            return False
    
    @classmethod
    def _convert_xlsx_to_ct(cls, file_path: str, basename: str) -> bool:
        """Convert XLSX file to CT format."""
        try:
            xlsx_processor = XLSXProcessor(file_path, verbose=True)
            data = xlsx_processor.read()
            
            if not data or not data[0]:
                logger.error(f"Invalid or empty XLSX file: {file_path}")
                return False
            
            # Extract the original timestamp from the XLSX file's filesystem timestamp
            preserve_timestamp = None
            try:
                from datetime import datetime
                file_stat = os.stat(file_path)
                file_time = datetime.fromtimestamp(file_stat.st_mtime)
                preserve_timestamp = file_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"🔍 FileConverter: Retrieved timestamp from XLSX file: {preserve_timestamp}")
            except Exception as e:
                logger.warning(f"Could not retrieve timestamp from XLSX file: {e}")
                
            output_path = str(Path(file_path).parent / f"{cls.get_smart_output_name(basename, '.ct')}")
            ct_processor = CTProcessor(output_path, verbose=True)
            ct_processor.write(data, preserve_timestamp)
            
            logger.info(f"Successfully converted XLSX to CT: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting XLSX to CT: {e}")
            return False

    @classmethod
    def process_folder(cls, folder_path: str, extensions: Optional[List[str]] = None) -> tuple[int, int]:
        """
        Processes all supported files in the given folder.
        
        Args:
            folder_path (str): Path to the folder containing files to process
            extensions (Optional[List[str]]): List of file extensions to process.
            Defaults to ['.ct'] for batch CT conversion.
        
        Returns:
            tuple[int, int]: (successful_conversions, total_files_processed)
        """
        if extensions is None:
            extensions = ['.ct']  # Default to processing CT files for batch operations
            
        try:
            folder_path_obj = Path(folder_path)
            if not folder_path_obj.exists() or not folder_path_obj.is_dir():
                logger.error(f"Folder not found or invalid: {folder_path}")
                return 0, 0

            # Find all files with specified extensions
            target_files: List[Path] = []
            for ext in extensions:
                target_files.extend(folder_path_obj.glob(f"*{ext}"))
            
            if not target_files:
                logger.info(f"No files with extensions {extensions} found in folder: {folder_path}")
                return 0, 0

            logger.info(f"Found {len(target_files)} files to process in {folder_path}")
            
            successful = 0
            total = len(target_files)
            
            for file_path in target_files:
                if cls.process_file(str(file_path)):
                    successful += 1
                    
            logger.info(f"Batch processing completed: {successful}/{total} files processed successfully")
            return successful, total
            
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}")
            return 0, 0


def print_usage():
    """Print usage information for the CLI."""
    print("""
CT2 File Conversion Tool v2.0.0
================================

Usage:
    python main.py <file_or_folder_path>

Supported Operations:
    Single File:
        python main.py CardInfo.ct          # Convert CT to XLSX
        python main.py CardInfo.xlsx        # Convert XLSX to CT
        
    Batch Processing:
        python main.py ./data/              # Convert all .ct files in folder
        python main.py C:\\GameData\\Tables  # Process folder with absolute path

Supported Formats:
    • .ct   - Ragnarok Online 2 binary table format
    • .xlsx - Microsoft Excel format
    
Output:
    Converted files are saved with '_converted' suffix in the same directory.
    
Examples:
    CardInfo.ct → CardInfo_converted.xlsx
    data.xlsx   → data_converted.ct
""")


def main():
    """
    Main entry point for the CT2 file conversion tool.
    
    Handles command-line arguments and orchestrates the conversion process.
    Supports both single file and batch folder processing.
    """
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    
    target_path = sys.argv[1]
    converter = FileConverter()
    
    try:
        if os.path.isfile(target_path):
            # Process single file
            success = converter.process_file(target_path)
            sys.exit(0 if success else 1)
            
        elif os.path.isdir(target_path):
            # Process folder (CT files by default for batch operations)
            successful, total = converter.process_folder(target_path)
            if total == 0:
                logger.warning("No files were found to process")
                sys.exit(1)
            elif successful == total:
                logger.info("All files processed successfully")
                sys.exit(0)
            else:
                logger.warning(f"Some files failed to process: {successful}/{total} successful")
                sys.exit(1)
        else:
            logger.error(f"Invalid path: {target_path}. Path must be an existing file or directory.")
            print_usage()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()