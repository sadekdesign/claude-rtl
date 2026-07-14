from cx_Freeze import setup, Executable
import sys

build_options = {
    "packages": ["webview", "ctypes", "re", "threading", "time", "html", "pystray", "PIL"],
    "excludes": ["tkinter", "unittest", "email", "xmlrpc", "pydoc"],
    "include_msvcr": True,
}

setup(
    name="ClaudeRTL",
    version="1.0",
    description="Claude RTL Popup",
    options={"build_exe": build_options},
    executables=[
        Executable(
            "claude_rtl.py",
            base="gui",
            target_name="ClaudeRTL.exe",
            icon="icon.ico",
        )
    ],
)
