from cx_Freeze import setup, Executable

setup(
    name="DigitalDetox",
    version="1.0",
    description="Digital Detox App",
    executables=[Executable("digital_detox.py", base="Win32GUI", icon="icon.ico")]
)
