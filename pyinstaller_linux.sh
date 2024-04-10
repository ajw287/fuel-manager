pyinstaller --noconfirm --log-level=WARN \
            --key=9791 \
            --onefile \
            --add-data=./resources/Oswald-Medium.ttf:resources \
            --add-data=./resources/NA1.wav:resources \
            --add-data=./resources/NA2.wav:resources \
            --add-data=./resources/NA3.wav:resources \
			--add-data=./resources/small-window-icon.png:resources \
            --key=7299205536 \
            FuelManager.py
