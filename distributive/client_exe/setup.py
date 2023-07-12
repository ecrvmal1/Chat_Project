import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "log", "client", "unit_tests"],
}
setup(
    name="msnger_client",
    version="0.8.8",
    description="msnger_client",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            # base='Win32GUI',
                            targetName='client.exe',
                            )]
)
