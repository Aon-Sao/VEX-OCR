import shutil
import time
from enum import IntEnum
from pathlib import Path
from time import sleep
from typing import Literal

import psutil

class Units(IntEnum):
    # Technically, these are Kibibyte, Mebibyte, etc.
    BIT = 1
    NIBBLE = 4
    BYTE = 8
    KB = 8192
    MB = 8388608
    GB = 8589934592
    TB = 8796093022208

class DiskMonitor:
    def __init__(self, disk_location: Path):
        self.disk_location = disk_location
        self._total, self._used, self._free = None, None, None

    def update(self):
        info = shutil.disk_usage(self.disk_location)
        self._total = info.total * Units.BYTE.value
        self._used = info.used * Units.BYTE.value
        self._free = info.free * Units.BYTE.value
        return self

    def total(self, unit: Units = Units.BYTE):
        return round(self._total / unit.value, 2)

    def used(self, unit: Units = Units.BYTE):
        return round(self._used / unit.value, 2)

    def free(self, unit: Units = Units.BYTE):
        return round(self._free / unit.value, 2)

class CPUMonitor:
    def __init__(self):
        self.cpu_percents = []
        self.load_averages = []
        self._avg_is_ready = False
        self.cpu_count = psutil.cpu_count()

        # Must be run once and ignored, per the docs
        psutil.cpu_percent(percpu=True)
        # Must be run once and ignored, per the docs
        # Is ready after 5 seconds
        psutil.getloadavg()
        self.start_time = time.time()

    def update(self):
        self.cpu_percents = psutil.cpu_percent(percpu=True)
        self.load_averages = [(x / self.cpu_count) * 100 for x in psutil.getloadavg()]
        return self

    def percents(self, index: int | Literal["ALL"] = "ALL"):
        valid_ind = range(len(self.cpu_percents))
        if index == "ALL":
            return self.cpu_percents
        elif index in valid_ind:
            return self.cpu_percents[index]
        else:
            raise IndexError(f"CPUs are indexed {valid_ind[0]} through {valid_ind[-1]}")

    def averages(self):
        # If getloadavg is called within 5 seconds of its first call
        # it will not be ready yet, per the docs
        if not self._avg_is_ready:
            t = time.time()
            delta = t - self.start_time
            if delta < 5:
                sleep(5 - delta)
            self._avg_is_ready = True
        return self.load_averages

class RAMMonitor:
    def __init__(self):
        self._total_ram = None
        self._available_ram = None
        self._used_ram = None
        self._free_ram = None
        self._total_swap = None
        self._available_swap = None
        self._used_swap = None
        self._free_swap = None
        self.update()

    def update(self):
        info = psutil.virtual_memory()
        self._total_ram = info.total * Units.BYTE.value
        self._available_ram = info.available * Units.BYTE.value
        self._used_ram = info.used * Units.BYTE.value
        self._free_ram = info.free * Units.BYTE.value
        info = psutil.swap_memory()
        self._total_swap = info.total * Units.BYTE.value
        self._used_swap = info.used * Units.BYTE.value
        self._free_swap = info.free * Units.BYTE.value
        return self

    def total_ram(self, unit: Units = Units.BYTE):
        return self._total_ram / unit.value

    def available_ram(self, unit: Units = Units.BYTE):
        return self._available_ram / unit.value

    def used_ram(self, unit: Units = Units.BYTE):
        return self._used_ram / unit.value

    def free_ram(self, unit: Units = Units.BYTE):
        return self._free_ram / unit.value

    def total_swap(self, unit: Units = Units.BYTE):
        return self._total_swap / unit.value

    def available_swap(self, unit: Units = Units.BYTE):
        return self._available_swap / unit.value

    def used_swap(self, unit: Units = Units.BYTE):
        return self._used_swap / unit.value

    def free_swap(self, unit: Units = Units.BYTE):
        return self._free_swap / unit.value
