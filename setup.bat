@echo off
cd /d "%~dp0"

mkdir configs 2>nul
echo Downloading Python 3.12.8 embedded package...
curl -L "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip" -o python_embed.zip

echo Extracting
powershell -command "Expand-Archive -Force python_embed.zip runtime"
del python_embed.zip

echo Creating directories
if not exist "runtime\Lib" mkdir "runtime\Lib"
if not exist "runtime\Lib\site-packages" mkdir "runtime\Lib\site-packages"
if not exist "runtime\Scripts" mkdir "runtime\Scripts"
(echo python312.zip & echo . & echo import site) > runtime\python312._pth

echo Installing pip...
curl -L "https://bootstrap.pypa.io/get-pip.py" -o runtime\get-pip.py
runtime\python.exe runtime\get-pip.py
del runtime\get-pip.py

echo Installing Packages
:: Install packages
runtime\python.exe -m pip install --no-warn-script-location torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
runtime\python.exe -m pip install --no-warn-script-location python-dotenv==1.0.1
runtime\python.exe -m pip install --no-warn-script-location sounddevice==0.5.1
runtime\python.exe -m pip install --no-warn-script-location local-attention==1.9.15
runtime\python.exe -m pip install --no-warn-script-location faiss-cpu==1.9.0.post1
runtime\python.exe -m pip install --no-warn-script-location customtkinter==5.2.2
runtime\python.exe -m pip install --no-warn-script-location pyrnnoise==0.2.7
runtime\python.exe -m pip install --no-warn-script-location librosa==0.10.2.post1
runtime\python.exe -m pip install --no-warn-script-location transformers==4.47.1
runtime\python.exe -m pip install --no-warn-script-location pywin32==308
runtime\python.exe -m pip install --no-warn-script-location pedalboard==0.9.16
runtime\python.exe -m pip install --no-warn-script-location CTkMessagebox==2.7
runtime\python.exe -m pip install --no-warn-script-location silero-vad==5.1.2
runtime\python.exe -m pip install --no-warn-script-location keyboard==0.13.5
runtime\python.exe -m pip install --no-warn-script-location pydub==0.25.1

echo Extracting Tkinter
powershell -command "Expand-Archive -Force zips\tkinter3128.zip runtime"

rem // Updated assets download and extraction block using a flag
set "download_assets=false"
if not exist "assets/contentvec/pytorch_model.bin" set "download_assets=true"
if not exist "assets/contentvec/config.json" set "download_assets=true"
if not exist "assets/fcpe/fcpe_c_v001.pt" set "download_assets=true"
if "%download_assets%"=="false" (
echo Assets already exist, skipping assets download.
) else (
echo Downloading assets...
curl -L "https://huggingface.co/datasets/dr87/vc-assets/resolve/main/assets.zip" -o assets.zip
echo Extracting assets...
powershell -command "Expand-Archive -Force assets.zip ."
del assets.zip
)

echo Downloading FFmpeg...
if exist "ffmpeg.exe" (
echo ffmpeg.exe already exists, skipping FFmpeg download.
) else (
curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip" -o ffmpeg.zip
echo Extracting ffmpeg.exe...
powershell -command "Expand-Archive -Force ffmpeg.zip temp_ffmpeg"
move /Y temp_ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe .
rd /s /q temp_ffmpeg
del ffmpeg.zip
)

echo Setup complete!
pause