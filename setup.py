import sys
from cx_Freeze import setup, Executable
import os.path
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('CombatManager.py', base=base, icon="dndicon.ico")
]

options = {
    'build_exe': {
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
        "includes":[
            "bs4",
            "urllib",
        ],
    },
}

setup(name = 'Combat Manager',
      version = '1.0',
      description = 'Helps manage combate for DMs in DnD 5e',
      options = options,
      executables = executables
      )
