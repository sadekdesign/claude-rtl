"""بناء ClaudeRTL.exe:  python setup_cx.py build"""

from cx_Freeze import setup, Executable

build_options = {
    "packages": ["webview", "pystray", "PIL", "ctypes", "json", "re", "threading",
                 "time", "html", "webbrowser", "tempfile"],
    "includes": ["mdrender", "settings", "ui", "winapi"],
    "excludes": ["tkinter", "unittest", "email", "xmlrpc", "pydoc", "test"],
    "include_files": [("icon.ico", "icon.ico")],
    "include_msvcr": True,
    "optimize": 1,
}

setup(
    name="ClaudeRTL",
    version="2.0",
    description="Claude RTL — قارئ عربي منبثق",
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
