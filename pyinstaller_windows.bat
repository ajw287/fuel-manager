%userprofile%\AppData\Local\Programs\Python\Python39\Scripts\pyinstaller.exe --noconfirm --log-level=WARN ^
    --onefile --windowed ^
    --icon=.\resources\lpicon.ICO ^
    --add-data=.\resources\Oswald-Medium.ttf;resources ^
    --add-data=.\resources\NA2.wav;resources ^
    --add-data=.\resources\NA3.wav;resources ^
    --add-data=.\resources\NA1.wav;resources ^
	--add-data=.\resources\small-window-icon.png;resources ^
    --key=7299205536 ^
    FuelManager.py
