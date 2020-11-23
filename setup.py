import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
includefiles = ['img']
packages = ["tkinter", "subprocess", "csv", "shutil", "os", "platform", "finder"]
build_exe_options = {"packages": packages, "include_files":includefiles}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
  base = "Win32GUI"

setup(name = "FinderMP",
  version = "0.1",
  description = "FinderMP!",
  options = {"build_exe": build_exe_options},
  executables = [Executable("finder-gui.py", base=base, targetName='FinderMP.exe', icon='img/binoculars.ico')])