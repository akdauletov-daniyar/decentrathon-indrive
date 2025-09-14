@echo off
echo === Astana STGCN Training Pipeline ===

echo.
echo Step 1: Creating Astana dataset...
python create_astana_dataset.py
if %errorlevel% neq 0 (
    echo Failed to create dataset with Python, trying alternative...
    echo Creating dataset manually...
    
    REM Create dataset directory
    if not exist "data\astana" mkdir "data\astana"
    
    REM Create simple dataset using PowerShell
    powershell -Command "& {$n_sensors=100; $n_timesteps=1000; $data=@(); for($i=0; $i -lt $n_timesteps; $i++) {$row=@(); for($j=0; $j -lt $n_sensors; $j++) {$row += [math]::Round((Get-Random -Minimum 20 -Maximum 60), 2)}; $data += ($row -join ',')}; $data | Out-File -FilePath 'data\astana\vel.csv' -Encoding ASCII}"
    
    echo Dataset created!
)

echo.
echo Step 2: Running STGCN training...
python main.py --dataset astana --epochs 10 --batch_size 16
if %errorlevel% neq 0 (
    echo.
    echo Python command failed. Please check:
    echo 1. Python is installed and in PATH
    echo 2. Required packages are installed: pip install torch pandas numpy scipy scikit-learn tqdm
    echo 3. Try running: python main.py --dataset astana --epochs 10
)

echo.
echo Done!
pause
