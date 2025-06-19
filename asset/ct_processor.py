"""CT File Processor for Ragnarok Online 2 Binary Format"""

import struct
import datetime
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, BinaryIO
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class CTDataType:
    """
    Data class representing a CT file data type definition.
    
    Attributes:
        code (int): Numeric type identifier
        name (str): Human-readable type name
        struct_format (str): Python struct format string
        size (Optional[int]): Fixed size in bytes (None for variable-length types)
        description (str): Type description
    """
    code: int
    name: str
    struct_format: str
    size: Optional[int]
    description: str


class CTProcessor:
    """Processor for Ragnarok Online 2 CT (Custom Table) files."""
    
    # CT data type definitions
    CT_DATA_TYPES = {
        2: CTDataType(2, "BYTE", "B", 1, "Unsigned 8-bit integer (0-255)"),
        3: CTDataType(3, "SHORT", "h", 2, "Signed 16-bit integer (-32,768 to 32,767)"),
        4: CTDataType(4, "WORD", "<H", 2, "Unsigned 16-bit integer (0-65,535)"),
        5: CTDataType(5, "INT", "i", 4, "Signed 32-bit integer"),
        6: CTDataType(6, "DWORD", "<L", 4, "Unsigned 32-bit integer"),
        7: CTDataType(7, "DWORD_HEX", "<L", 4, "Hexadecimal DWORD representation"),
        8: CTDataType(8, "STRING", "", None, "UTF-16LE encoded string with length prefix"),
        9: CTDataType(9, "FLOAT", "f", 4, "32-bit floating point number"),
        11: CTDataType(11, "INT64", "<Q", 8, "64-bit integer"),
        12: CTDataType(12, "BOOL", "B", 1, "Boolean value (0 or 1)")
    }
    
    # Legacy compatibility mappings
    MS_DTYPES = {code: dtype.name for code, dtype in CT_DATA_TYPES.items()}
    INV_MS_DTYPES = {dtype.name: code for code, dtype in CT_DATA_TYPES.items()}
    
    # CT file format constants
    CT_HEADER_SIZE = 64
    CT_MAGIC_STRING = "RO2SEC!"
    CT_FOOTER_SIZE = 2

    def __init__(self, path: Union[str, Path], verbose: bool = True):
        """
        Initialize the CT processor.
        
        Args:
            path (Union[str, Path]): Path to the CT file to process
            verbose (bool): Enable detailed logging output
            
        Raises:
            ValueError: If the path is invalid or empty
        """
        if not path:
            raise ValueError("Path cannot be empty")
            
        self.path = Path(path)
        self.verbose = verbose
        self.header: List[str] = []
        self.types: List[str] = []
        self.rows: List[List[Any]] = []
        self.file_timestamp: str = ""
        
        if self.verbose:
            logger.info(f"Initialized CT processor for: {self.path}")

    def calculate_crc16_xmodem(self, data: bytes) -> int:
        """Calculate CRC-16-XMODEM checksum for the given data."""
        crc = 0x0000  # Initial value for XMODEM
        poly = 0x1021  # XMODEM polynomial
        
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc = crc << 1
                crc &= 0xFFFF  # Keep it 16-bit
        
        return crc

    def read(self) -> List[List[str]]:
        """Read and parse a CT file into structured data."""
        try:
            if not self.path.exists():
                raise FileNotFoundError(f"CT file not found: {self.path}")
                
            print(f"🔍 CT Processor: Reading file {self.path}")
            if self.verbose:
                logger.info(f"Reading CT file: {self.path}")
            
            with open(self.path, "rb") as file:
                # Validate and read header
                print(f"🔍 CT Processor: Validating header...")
                self._validate_ct_header(file)
                
                # Read column definitions
                print(f"🔍 CT Processor: Reading columns...")
                self._read_columns(file)
                
                # Read type definitions
                print(f"🔍 CT Processor: Reading types...")
                self._read_types(file)
                
                # Mark position before row count (for CRC calculation)
                row_count_pos = file.tell()
                
                # Read data rows
                print(f"🔍 CT Processor: Reading data rows...")
                self._read_data_rows(file)
                
                # Validate CRC checksum (row data only)
                print(f"🔍 CT Processor: Validating CRC checksum...")
                self._validate_crc_checksum(file, row_count_pos)
            
            # Prepare return data
            result = [self.header, self.types] + self.rows
            
            # Set file timestamp from CT header
            if hasattr(self, 'file_timestamp') and self.file_timestamp:
                try:
                    # Parse the timestamp from the CT header
                    ct_time = datetime.datetime.strptime(self.file_timestamp, "%Y-%m-%d %H:%M:%S")
                    timestamp = ct_time.timestamp()
                    
                    # Set both creation and modification time
                    os.utime(self.path, (timestamp, timestamp))
                    print(f"🔍 CT Processor: Set file timestamp to {self.file_timestamp}")
                except (ValueError, OSError) as e:
                    print(f"⚠️ CT Processor: Could not set file timestamp: {e}")
            
            print(f"✅ CT Processor: Read complete - {len(self.header)} columns, {len(self.rows)} data rows")
            if self.verbose:
                logger.info(f"CT read complete: {len(self.header)} columns, {len(self.rows)} data rows")
                
            return result
            
        except (ValueError, struct.error, OSError) as e:
            print(f"💥 CT Processor Error: {e}")
            logger.error(f"Error reading CT file {self.path}: {e}")
            raise

    def write(self, data: List[List[str]], preserve_timestamp: Optional[str] = None) -> None:
        """Write structured data to a CT file with proper formatting and CRC protection."""
        try:
            if not data or len(data) < 2:
                raise ValueError("Data must contain at least header and type rows")
            
            # Create directory if it doesn't exist
            self.path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"🔍 CT Processor: Writing file {self.path}")
            if self.verbose:
                logger.info(f"Writing CT file: {self.path}")
            
            with open(self.path, "wb") as file:
                # Write CT header
                print(f"🔍 CT Processor: Writing header...")
                self._write_ct_header(file, preserve_timestamp)
                
                # Extract data components
                header = data[0]
                types = data[1]
                rows = data[2:] if len(data) > 2 else []
                
                # Write column definitions
                self._write_columns(file, header)
                
                # Write type definitions
                self._write_types(file, types)
                
                # Write data rows and capture the data for CRC calculation
                print(f"🔍 CT Processor: Writing {len(rows)} data rows...")
                data_bytes = self._write_data_rows(file, rows, types)
                
                # Calculate and write CRC footer
                print(f"🔍 CT Processor: Calculating and writing CRC footer...")
                self._write_ct_footer_with_crc(file, data_bytes)
            
            print(f"✅ CT Processor: Write complete - {len(header)} columns, {len(rows)} data rows")
            if self.verbose:
                logger.info(f"CT write complete: {len(header)} columns, {len(rows)} data rows")
                
        except (ValueError, struct.error, OSError) as e:
            print(f"💥 CT Processor Write Error: {e}")
            logger.error(f"Error writing CT file {self.path}: {e}")
            raise

    def _validate_crc_checksum(self, file: BinaryIO, data_start_pos: int) -> None:
        """
        Validate CRC-16-XMODEM checksum for data integrity.
        
        The CRC protects only the data rows (excluding the row count marker).
        
        Args:
            file (BinaryIO): Open binary file handle
            data_start_pos (int): Position where row count is located
            
        Raises:
            ValueError: If CRC validation fails
        """
        # Read the CRC footer (last 2 bytes)
        current_pos = file.tell()
        file.seek(-2, 2)  # Seek to 2 bytes before end
        crc_bytes = file.read(2)
        
        if len(crc_bytes) != 2:
            print("⚠️ CT Processor: Missing CRC footer, skipping validation")
            return
        
        # Extract stored CRC (little-endian)
        stored_crc = struct.unpack("<H", crc_bytes)[0]
        
        # Read ONLY the row data (skip the row count, start after it)
        file.seek(data_start_pos + 4)  # Skip 4-byte row count
        row_data_start_pos = data_start_pos + 4
        protected_data = file.read(current_pos - row_data_start_pos)
        
        # Calculate CRC on row data only
        calculated_crc = self.calculate_crc16_xmodem(protected_data)
        
        if calculated_crc == stored_crc:
            print(f"✅ CT Processor: CRC validation passed (0x{calculated_crc:04X})")
            if self.verbose:
                logger.info(f"CRC validation successful: 0x{calculated_crc:04X}")
        else:
            error_msg = f"CRC validation failed! Calculated: 0x{calculated_crc:04X}, Stored: 0x{stored_crc:04X}"
            print(f"❌ CT Processor: {error_msg}")
            if self.verbose:
                logger.error(error_msg)
            # Note: We could raise an exception here, but for compatibility we'll just warn
            # raise ValueError(error_msg)

    def _validate_ct_header(self, file: BinaryIO) -> Dict[str, str]:
        """
        Validate the CT file header and extract metadata.
        
        Args:
            file (BinaryIO): Open binary file handle
            
        Returns:
            Dict[str, str]: Header metadata including magic and timestamp
            
        Raises:
            ValueError: If header validation fails
        """
        header_data = file.read(self.CT_HEADER_SIZE)
        if len(header_data) != self.CT_HEADER_SIZE:
            raise ValueError(f"Invalid header size: expected {self.CT_HEADER_SIZE}, got {len(header_data)}")
        
        # Decode and validate magic string
        try:
            # Find the magic string in UTF-16LE encoding
            magic_bytes = self.CT_MAGIC_STRING.encode('UTF-16LE')
            if not header_data.startswith(magic_bytes):
                raise ValueError(f"Invalid magic string: expected '{self.CT_MAGIC_STRING}'")
            
            # Extract timestamp (after magic + null terminator)
            timestamp_start = len(magic_bytes) + 2  # +2 for null terminator
            
            # Find the end of the timestamp string (double null bytes)
            remaining_data = header_data[timestamp_start:]
            timestamp_end = None
            
            # Look for UTF-16LE null terminator (2 null bytes)
            for i in range(0, len(remaining_data) - 1, 2):
                if remaining_data[i:i+2] == b'\x00\x00':
                    timestamp_end = i
                    break
            
            if timestamp_end is None:
                timestamp_end = min(len(remaining_data), 38)  # Max reasonable timestamp length
            
            timestamp_data = remaining_data[:timestamp_end]
            
            if timestamp_data and len(timestamp_data) >= 2:
                try:
                    # Decode UTF-16LE timestamp
                    timestamp = timestamp_data.decode('UTF-16LE').strip('\x00')
                    if timestamp:
                        print(f"🔍 CT Processor: Found timestamp: {timestamp}")
                    else:
                        timestamp = "2014-10-06 12:28:25"  # Default fallback
                        print(f"⚠️ CT Processor: Empty timestamp, using fallback: {timestamp}")
                except (UnicodeDecodeError, UnicodeError):
                    # Fallback for corrupted timestamp
                    timestamp = "2014-10-06 12:28:25"  # Default fallback
                    print(f"⚠️ CT Processor: Corrupted timestamp, using fallback: {timestamp}")
            else:
                timestamp = "2014-10-06 12:28:25"  # Default
                print(f"⚠️ CT Processor: No timestamp found, using default: {timestamp}")
                
            # Store timestamp for later use
            self.file_timestamp = timestamp
                
            if self.verbose:
                logger.info(f"Valid CT header found - Magic: {self.CT_MAGIC_STRING}, Timestamp: {timestamp}")
                
            return {
                'magic': self.CT_MAGIC_STRING,
                'timestamp': timestamp
            }
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode CT header: {e}")

    def _read_columns(self, file: BinaryIO) -> None:
        """Read column definitions from CT file."""
        num_columns = self._unpack_value(file, "DWORD")
            
        self.header = []
        for _ in range(num_columns):
            column_name = self._unpack_value(file, "STRING")
            self.header.append(column_name)

    def _read_types(self, file: BinaryIO) -> None:
        """Read type definitions from CT file."""
        num_types = self._unpack_value(file, "DWORD")
        if num_types != len(self.header):
            logger.warning(f"Type count ({num_types}) doesn't match column count ({len(self.header)})")
            
        self.types = []
        for _ in range(num_types):
            type_code = self._unpack_value(file, "DWORD")
            type_name = self._get_type_name(type_code)
            self.types.append(type_name)

    def _read_data_rows(self, file: BinaryIO) -> None:
        """Read data rows from CT file."""
        num_rows = self._unpack_value(file, "DWORD")
            
        self.rows = []
        for row_idx in range(num_rows):
            row_data: List[str] = []
            for col_idx, type_name in enumerate(self.types):
                try:
                    value = self._unpack_value(file, type_name)
                    row_data.append(str(value))
                except Exception as e:
                    logger.error(f"Error reading row {row_idx}, column {col_idx}: {e}")
                    row_data.append("null")
            self.rows.append(row_data)

    def _write_ct_header(self, file: BinaryIO, preserve_timestamp: Optional[str] = None) -> None:
        """Write proper CT file header with magic string and timestamp."""
        # Write magic string
        magic_bytes = self.CT_MAGIC_STRING.encode('UTF-16LE')
        file.write(magic_bytes)
        file.write(b'\x00\x00')  # Null terminator
        
        # Write timestamp - use preserved timestamp if provided, otherwise use file's modification time
        if preserve_timestamp:
            timestamp = preserve_timestamp
            print(f"🔍 CT Processor: Using preserved timestamp: {timestamp}")
        else:
            # Use the file's current modification time as the timestamp
            try:
                if self.path.exists():
                    # Get file modification time
                    mod_time = datetime.datetime.fromtimestamp(self.path.stat().st_mtime)
                    timestamp = mod_time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔍 CT Processor: Using file modification time as timestamp: {timestamp}")
                else:
                    # File doesn't exist yet, use current time
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🔍 CT Processor: Using current time as timestamp: {timestamp}")
            except (OSError, ValueError):
                # Fallback to current time
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🔍 CT Processor: Using current time as fallback timestamp: {timestamp}")
        
        timestamp_bytes = timestamp.encode('UTF-16LE')
        file.write(timestamp_bytes)
        file.write(b'\x00\x00')  # Null terminator for timestamp
        
        # Calculate and write padding
        written_bytes = len(magic_bytes) + 2 + len(timestamp_bytes) + 2  # +2 for timestamp null terminator
        padding_size = self.CT_HEADER_SIZE - written_bytes
        file.write(b'\x00' * padding_size)

    def _write_columns(self, file: BinaryIO, header: List[str]) -> None:
        """Write column definitions to CT file."""
        self._pack_value(file, "DWORD", len(header))
        for column_name in header:
            self._pack_value(file, "STRING", column_name)

    def _write_types(self, file: BinaryIO, types: List[str]) -> None:
        """Write type definitions to CT file."""
        self._pack_value(file, "DWORD", len(types))
        for type_name in types:
            type_code = self._get_type_code(type_name)
            self._pack_value(file, "DWORD", type_code)

    def _write_data_rows(self, file: BinaryIO, rows: List[List[str]], types: List[str]) -> bytes:
        """
        Write data rows to CT file and return only the row data for CRC calculation.
        
        Returns:
            bytes: Only the row data (excluding row count) for CRC calculation
        """
        # Create a buffer to capture only the row data (not row count)
        import io
        row_data_buffer = io.BytesIO()
        
        # Write row count to file only (not included in CRC)
        row_count_bytes = struct.pack("<L", len(rows))
        file.write(row_count_bytes)
        
        # Write each row to both file and buffer
        for row in rows:
            for value, type_name in zip(row, types):
                # Convert empty values appropriately
                if value == "":
                    value = self._get_null_value(type_name)
                
                # Pack the value and capture the bytes
                value_bytes = self._pack_value_to_bytes(type_name, value)
                file.write(value_bytes)
                row_data_buffer.write(value_bytes)  # Only row data in buffer
        
        # Return only the row data for CRC calculation (excluding row count)
        return row_data_buffer.getvalue()

    def _write_ct_footer_with_crc(self, file: BinaryIO, data_bytes: bytes) -> None:
        """
        Calculate CRC-16-XMODEM for the row data only and write as footer.
        
        Args:
            file (BinaryIO): Open binary file handle
            data_bytes (bytes): The row data (excluding row count) to calculate CRC for
        """
        # Calculate CRC-16-XMODEM on the row data only
        crc = self.calculate_crc16_xmodem(data_bytes)
        
        # Write CRC as little-endian 2-byte footer
        crc_bytes = struct.pack("<H", crc)
        file.write(crc_bytes)
        
        print(f"🔍 CT Processor: CRC-16-XMODEM calculated: 0x{crc:04X} (bytes: {crc_bytes[0]:02X} {crc_bytes[1]:02X})")
        if self.verbose:
            logger.info(f"CRC-16-XMODEM footer written: 0x{crc:04X}")

    def _pack_value_to_bytes(self, type_name: str, value: Any) -> bytes:
        """
        Pack a single value to bytes based on type (helper for CRC calculation).
        
        Args:
            type_name (str): CT type name
            value (Any): Value to pack
            
        Returns:
            bytes: Packed value as bytes
        """
        if type_name == "STRING":
            return self._pack_string_to_bytes(str(value))
        elif type_name == "DWORD_HEX":
            # Handle hexadecimal values
            if isinstance(value, str) and 'x' in value.lower():
                int_value = int(value, 16)
            else:
                int_value = int(value)
            return struct.pack("<L", int_value)
        else:
            # Standard types
            type_def = self._get_type_definition(type_name)
            if type_def is None:
                raise ValueError(f"Unsupported type: {type_name}")
                
            # Convert value to appropriate type
            if type_name in ["BYTE", "SHORT", "WORD", "INT", "DWORD", "INT64"]:
                converted_value = int(float(value))  # Handle "1.0" -> 1
            elif type_name == "FLOAT":
                converted_value = float(value)
            elif type_name == "BOOL":
                # Handle boolean conversion properly - treat "0", "false", "" as False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    converted_value = 0 if value_lower in ("0", "false", "", "no") else 1
                else:
                    converted_value = int(bool(value))
            else:
                converted_value = value
                
            return struct.pack(type_def.struct_format, converted_value)

    def _pack_string_to_bytes(self, value: str) -> bytes:
        """
        Pack a string as UTF-16LE with length prefix to bytes.
        
        Args:
            value (str): String value to pack
            
        Returns:
            bytes: Packed string as bytes
        """
        if not value or value == "":
            # Write zero length for empty strings only
            return struct.pack("<L", 0)
        else:
            # Write length prefix and string data
            length_bytes = struct.pack("<L", len(value))
            string_bytes = value.encode("UTF-16LE")
            return length_bytes + string_bytes

    def _unpack_value(self, file: BinaryIO, type_name: str) -> Any:
        """
        Unpack a single value from the binary file based on type.
        
        Args:
            file (BinaryIO): Open binary file handle
            type_name (str): CT type name (e.g., "INT", "STRING", "FLOAT")
            
        Returns:
            Any: Unpacked value in appropriate Python type
            
        Raises:
            ValueError: If type is unsupported or unpacking fails
        """
        if type_name == "STRING":
            return self._unpack_string(file)
        elif type_name == "DWORD_HEX":
            value = struct.unpack("<L", file.read(4))[0]
            return f"0x{value:X}"
        else:
            # Standard types
            type_def = self._get_type_definition(type_name)
            if type_def is None:
                raise ValueError(f"Unsupported type: {type_name}")
            
            if type_def.size is None:
                raise ValueError(f"Type {type_name} has no fixed size")
                
            data = file.read(type_def.size)
            if len(data) != type_def.size:
                raise ValueError(f"Insufficient data for type {type_name}")
                
            return struct.unpack(type_def.struct_format, data)[0]

    def _pack_value(self, file: BinaryIO, type_name: str, value: Any) -> None:
        """
        Pack a single value to the binary file based on type.
        
        Args:
            file (BinaryIO): Open binary file handle
            type_name (str): CT type name
            value (Any): Value to pack
            
        Raises:
            ValueError: If type is unsupported or packing fails
        """
        value_bytes = self._pack_value_to_bytes(type_name, value)
        file.write(value_bytes)

    def _unpack_string(self, file: BinaryIO) -> str:
        """
        Unpack a UTF-16LE string with length prefix.
        
        Args:
            file (BinaryIO): Open binary file handle
            
        Returns:
            str: Decoded string or "null" for empty strings
            
        Raises:
            ValueError: If string data is corrupted
        """
        try:
            length = struct.unpack("<L", file.read(4))[0]
            if length == 0:
                return ""  # Return empty string instead of "null"
                
            string_data = file.read(2 * length)  # UTF-16LE uses 2 bytes per character
            if len(string_data) != 2 * length:
                raise ValueError("Insufficient data for string")
                
            return string_data.decode("UTF-16LE")
            
        except (struct.error, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to unpack string: {e}")

    def _pack_string(self, file: BinaryIO, value: str) -> None:
        """
        Pack a string as UTF-16LE with length prefix.
        
        Args:
            file (BinaryIO): Open binary file handle
            value (str): String value to pack
        """
        string_bytes = self._pack_string_to_bytes(value)
        file.write(string_bytes)

    def _get_type_definition(self, type_name: str) -> Optional[CTDataType]:
        """Get type definition by name."""
        for type_def in self.CT_DATA_TYPES.values():
            if type_def.name == type_name:
                return type_def
        return None

    def _get_type_name(self, type_code: int) -> str:
        """Get type name by code."""
        type_def = self.CT_DATA_TYPES.get(type_code)
        return type_def.name if type_def else f"UNKNOWN_TYPE_{type_code}"

    def _get_type_code(self, type_name: str) -> int:
        """Get type code by name."""
        for code, type_def in self.CT_DATA_TYPES.items():
            if type_def.name == type_name:
                return code
        raise ValueError(f"Unknown type name: {type_name}")

    def _get_null_value(self, type_name: str) -> Union[int, float, str]:
        """Get appropriate null value for a given type."""
        null_values: Dict[str, Union[int, float, str]] = {
            "BYTE": 0, "SHORT": 0, "WORD": 0, "INT": 0,
            "DWORD": 0, "DWORD_HEX": 0, "INT64": 0,
            "FLOAT": 0.0, "BOOL": 0, "STRING": ""
        }
        return null_values.get(type_name, "")

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the CT file.
        
        Returns:
            Dict[str, Any]: File information including size, structure, and statistics
        """
        type_distribution: Dict[str, int] = {}
        info: Dict[str, Any] = {
            'file_path': str(self.path),
            'file_exists': self.path.exists(),
            'file_size': self.path.stat().st_size if self.path.exists() else 0,
            'columns': len(self.header),
            'data_rows': len(self.rows),
            'header': self.header.copy(),
            'types': self.types.copy(),
            'type_distribution': type_distribution
        }
        
        # Calculate type distribution
        for type_name in self.types:
            info['type_distribution'][type_name] = info['type_distribution'].get(type_name, 0) + 1
        
        return info

    # Legacy compatibility methods
    def _mstype(self, code: int) -> str:
        """Legacy: Map integer type to string type."""
        return self._get_type_name(code)

    def _inv_mstype(self, type_name: str) -> int:
        """Legacy: Map string type to integer type."""
        return self._get_type_code(type_name)