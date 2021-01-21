import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
includefiles = ['img']
packages = ['glob', 'fnmatch', 'os', 'platform', 'subprocess', 'shutil']
build_exe_options = {"packages": packages, "include_files":includefiles}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
  base = "Win32GUI"

setup(name = "BuscadorMP",
  version = "0.1",
  description = "Busca y gestiona archivos",
  options = {"build_exe": build_exe_options},
  executables = [Executable("finder_gui.py", shortcutName='BuscadorMP',shortcutDir='StartMenuFolder', base=base, target_name='BuscadorMP.exe', icon=r'img\binoculars.ico')])