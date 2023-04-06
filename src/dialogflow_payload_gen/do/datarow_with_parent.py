import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dataclasses import dataclass

from base_datarow import DataRow


@dataclass
class DataRowWithParent(DataRow):
    parent: str = ""
