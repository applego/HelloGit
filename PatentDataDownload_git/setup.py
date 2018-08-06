from cx_Freeze import setup, Executable
import sys

base = None

if sys.platform == 'win32':
    base = None
if sys.platform == "win64":
	base = "Win64GUI"

executables = [Executable("hello.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "CHOOSEFILE",
    options = options,
    version = "1.0",
    description = 'converter',
    executables = executables
)