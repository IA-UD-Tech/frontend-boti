# Check if conda is installed
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Output "Miniconda not found. Installing Miniconda..."
    # Download Miniconda installer
    Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -OutFile "miniconda.exe"
    # Install Miniconda
    Start-Process -Wait -FilePath "miniconda.exe" -ArgumentList "/InstallationType=JustMe", "/AddToPath=1", "/RegisterPython=0", "/S", "/D=$env:USERPROFILE\miniconda"
    # Initialize conda
    & "$env:USERPROFILE\miniconda\Scripts\conda.exe" init
} else {
    Write-Output "Miniconda is already installed."
}

# Create and activate the environment if it doesn't exist
if (-not (& conda env list | Select-String -Pattern "llm_front")) {
    Write-Output "Creating conda environment 'llm_front'..."
    & conda create -n llm_front python=3.8 -y
} else {
    Write-Output "Conda environment 'llm_front' already exists."
}

# Activate the environment
Write-Output "Activating conda environment 'llm_front'..."
& conda activate llm_front

# Install streamlit if not installed
if (-not (pip show streamlit -ErrorAction SilentlyContinue)) {
    Write-Output "Installing Streamlit..."
    pip install streamlit
} else {
    Write-Output "Streamlit is already installed."
}

# Run the Streamlit application
Write-Output "Running Streamlit application..."
streamlit run front_end/landing_page.py
