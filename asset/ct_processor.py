import os
import struct

class CTProcessor:

    MS_DTYPES = {
        2: "BYTE",
        3: "SHORT",
        4: "WORD",
        5: "INT",
        6: "DWORD",
        7: "DWORD_HEX",
        8: "STRING",
        9: "FLOAT",
        11: "INT64",
        12: "BOOL"
    }

    INV_MS_DTYPES = {v: k for k, v in MS_DTYPES.items()}

    def __init__(self, path, verbose=True):
        self.path = path
        self.verbose = verbose
        self.ct = None

    def read(self):
        """Reads a .ct file and parses its contents."""
        try:
            with open(self.path, "rb") as ct:
                ct.seek(64)  # Skip header padding

                # Read header
                num_columns = self._unpack(ct, "DWORD")
                self.header = [self._unpack(ct, "STRING") for _ in range(num_columns)]

                # Read types
                num_types = self._unpack(ct, "DWORD")
                self.types = [self._mstype(self._unpack(ct, "DWORD")) for _ in range(num_types)]

                # Read rows
                num_rows = self._unpack(ct, "DWORD")
                self.rows = [
                    [self._unpack(ct, mstype) for mstype in self.types]
                    for _ in range(num_rows)
                ]

            if self.verbose:
                print(f"\nCT read of \"{self.path}\" complete!\n")

            return [self.header, self.types] + self.rows

        except (ValueError, struct.error, OSError) as e:
            print(f"Error reading CT file: {e}")
            return []

    def write(self, data):
        """Writes data to a .ct file."""
        try:
            with open(self.path, "wb") as ct:
                ct.write(b'\x00' * 64)  # Padding

                # Write header
                self._pack(ct, "DWORD", len(data[0]))  # Number of columns
                for column in data[0]:
                    self._pack(ct, "STRING", column)

                # Write types
                self._pack(ct, "DWORD", len(data[1]))  # Number of column types
                for mstype in data[1]:
                    self._pack(ct, "DWORD", self._inv_mstype(mstype))

                # Write rows
                self._pack(ct, "DWORD", len(data) - 2)  # Number of rows
                for row in data[2:]:
                    for value, mstype in zip(row, data[1]):
                        self._pack(ct, mstype, value)

            if self.verbose:
                print(f"\nCT write of \"{self.path}\" complete!\n")

        except (ValueError, struct.error, OSError) as e:
            print(f"Error writing CT file: {e}")

    def _unpack(self, file, dtyp="DWORD"):
        """Unpacks data from the binary file."""
        unpack_methods = {
            "BYTE": lambda: struct.unpack("B", file.read(1))[0],
            "SHORT": lambda: struct.unpack("h", file.read(2))[0],
            "WORD": lambda: struct.unpack("<H", file.read(2))[0],
            "INT": lambda: struct.unpack("i", file.read(4))[0],
            "DWORD": lambda: struct.unpack("<L", file.read(4))[0],
            "DWORD_HEX": lambda: f"0x{struct.unpack('<L', file.read(4))[0]:X}",
            "STRING": lambda: self._unpack_string(file),
            "FLOAT": lambda: struct.unpack("f", file.read(4))[0],
            "INT64": lambda: struct.unpack("<Q", file.read(8))[0],
            "BOOL": lambda: struct.unpack("B", file.read(1))[0],
        }
        if dtyp not in unpack_methods:
            raise ValueError(f"Unsupported unpack type: {dtyp}")
        try:
            return unpack_methods[dtyp]()
        except struct.error as e:
            raise ValueError(f"Failed to unpack {dtyp}: {e}")

    def _unpack_string(self, file):
        """
        Unpacks a UTF-16 string, ensuring sufficient buffer size before decoding.
        """
        try:
            length = struct.unpack("<L", file.read(4))[0]  # Read the length of the string
            if length == 0:
                return "null"
            string_data = file.read(2 * length)
            if len(string_data) < 2 * length:
                raise struct.error("Buffer too small for string data.")
            return string_data.decode("UTF-16LE")
        except struct.error as e:
            raise ValueError(f"Failed to unpack STRING: {e}")

    def _pack(self, file, dtyp, value):
        """Packs data into the binary file."""
        pack_methods = {
            "BYTE": lambda: file.write(struct.pack("B", int(value))),
            "SHORT": lambda: file.write(struct.pack("h", int(value))),
            "WORD": lambda: file.write(struct.pack("<H", int(value))),
            "INT": lambda: file.write(struct.pack("i", int(value))),
            "DWORD": lambda: file.write(struct.pack("<L", int(value))),
            "DWORD_HEX": lambda: file.write(struct.pack("<L", int(value, 16) if 'x' in value else int(value))),
            "STRING": lambda: (self._pack(file, "DWORD", len(value)), file.write(value.encode("UTF-16LE"))),
            "FLOAT": lambda: file.write(struct.pack("f", float(value))),
            "INT64": lambda: file.write(struct.pack("<Q", int(value))),
            "BOOL": lambda: file.write(struct.pack("B", int(value))),
        }
        if dtyp not in pack_methods:
            raise ValueError(f"Unsupported pack type: {dtyp}")
        try:
            pack_methods[dtyp]()
        except struct.error as e:
            raise ValueError(f"Failed to pack {dtyp}: {e}")

    def _mstype(self, s):
        """Maps integer type to string type."""
        return self.MS_DTYPES.get(s, f"UNKNOWN_TYPE_{s}")

    def _inv_mstype(self, s):
        """Maps string type to integer type."""
        return self.INV_MS_DTYPES.get(s, f"UNKNOWN_TYPE_{s}")
