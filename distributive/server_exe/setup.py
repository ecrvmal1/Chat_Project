import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "log", "server", "unit_tests"],
}
setup(
    name="msnger_server",
    version="1.0.0",
    description="msnger_server",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server.py',
                            # base='Win32GUI',
                            targetName='server.exe',
                            )]
)
