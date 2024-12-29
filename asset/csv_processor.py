import os
import csv
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVProcessor:
    """
    Comma-separated values file format for Ragnarok Online 2 assets.
    Allows customization of the delimiter.
    """

    def __init__(self, path, delimiter=",", verbose=False):
        self.path = path
        self.delimiter = delimiter
        self.verbose = verbose
        self.header = []
        self.types = []
        self.rows = []

    def read(self) -> List[List[str]]:
        """
        Parse CSV file to list using the specified delimiter.

        :return: Parsed CSV data
        :rtype: list
        """
        with open(self.path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            self.header = next(reader)
            self.types = next(reader)
            self.rows = [row for row in reader]

        if self.verbose:
            logger.info("CSV read of \"%s\" complete!", self.path)

        return [self.header] + [self.types] + self.rows

    def write(self, data: List[List[str]]) -> None:
        """
        Write list to CSV using the specified delimiter.

        :param list data: Decoded list to write on CSV file
        """
        dir_path = os.path.dirname(self.path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(self.path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            writer.writerow(data[0])  # Header
            writer.writerow(data[1])  # Types
            writer.writerows(data[2:])  # Rows

        if self.verbose:
            logger.info("CSV write to \"%s\" complete!", self.path)
