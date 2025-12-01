@echo off
call activate_environment.bat
call pyinstaller --name CoverflowVideoGenerator --onefile --windowed --copy-metadata imageio --copy-metadata imageio-ffmpeg --collect-data imageio_ffmpeg gui.py
pause
