# Atlas-GUI: Per-user launcher and configuration

This folder contains a lightweight Windows `launch.bat` wrapper to start the Streamlit UI for Atlas.

Important security & setup notes

- Per-user customization
  - `launch.bat` is intended as a per-user convenience script. Edit it to set your machine hostname or other local preferences.
  - The script includes a hostname check to help prevent accidental execution on other machines. Replace `YourHTPCName` with your hostname.

- Local-first usage
  - The default behavior is to run the UI locally on your machine only. Do not change networking settings unless you intentionally expose the UI and understand the security tradeoffs.

- Installing dependencies
  - From PowerShell (recommended):

```powershell
cd "c:\path\to\Atlas-GUI"
pip install -r requirements.txt
```

- Launching the UI
  - Double-click `launch.bat` from File Explorer (it will set its working directory correctly). Or run from PowerShell:

```powershell
cd "c:\path\to\Atlas-GUI"
.\launch.bat
```

- Multi-user hosts
  - If several users share a machine, each should run Atlas under a separate OS account and maintain separate configuration files and working directories.

- Troubleshooting
  - If YAML config files are not loaded, confirm you're running the script from the repository root (the script sets its working directory to its own folder). If you need to run from elsewhere, update paths in the script.

This file is a lightweight guide — for full operator guidance see `README.md` and `SECURITY.md` in the repository root.
