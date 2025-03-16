# File-Integrity-Monitor

A Python-based file integrity monitoring tool that checks for unauthorized file modifications, deletions, or corruptions. It uses a graphical interface to allow users to select or deselect files and directories, and it runs monitoring in the background with manual start/stop controls.

## Features

- **File Integrity Verification:**  
  Computes and compares file hashes (using SHA-256 by default) to detect unauthorized changes.
  
- **Logging:**  
  Logs file openings, modifications, deletions, and corruption events to a log file (`file_integrity.log`).

- **SQLite Database:**  
  Stores file paths, hash values, and timestamps in a SQLite database (`file_integrity.db`).

- **Graphical User Interface (GUI):**  
  Built using Tkinter, allowing users to easily select/deselect files and directories.

- **Background Monitoring:**  
  Runs the monitoring loop in a separate thread with manual start/stop control.

- **Startup Automation:**  
  Can be set to run automatically at system startup (instructions provided below).

## Requirements

- Python 3.x  
- Standard Python libraries: `hashlib`, `os`, `sqlite3`, `time`, `logging`, `threading`, and `tkinter`

> **Note:** Tkinter usually comes pre-installed with Python. If not, install it using your OS package manager.

  ```bash
  pip install hashlib os sqlite3 time logging threading tkinter
  ```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Kernel-Freak/File-Integrity-Monitor.git
   cd File-Integrity-Monitor
   ```

2. **(Optional) Create and Activate a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   This project uses only Python's standard libraries, so no extra packages are required.

## Usage

1. **Run the Application:**

   ```bash
   python file_integrity_monitor.py
   ```

2. **Using the GUI:**

   - **Add Files/Directories:**  
     Use the "Add Files" and "Add Directories" buttons to select the items you want to monitor.

   - **Remove Selected Items:**  
     Highlight and click "Remove Selected" to deselect files or directories.

   - **Start/Stop Monitoring:**  
     Click "Start Monitoring" to run the background file integrity check. You can stop the process anytime by clicking "Stop Monitoring".

3. **Log and Database:**

   - **Log File:**  
     Check the `file_integrity.log` file for detailed log information regarding file events.

   - **Database:**  
     The `file_integrity.db` SQLite database stores the file paths, hash values, and timestamps.

## (Optional) Running at System Startup

To run the monitor automatically when your system starts, consider these approaches:

### Windows

- **Convert to Executable:**  
  Use [PyInstaller](https://www.pyinstaller.org/) to convert your script to an executable.

- **Startup Folder:**  
  Place a shortcut of the executable in the Startup folder. Access it by pressing `Win+R`, typing `shell:startup`, and pasting the shortcut there.

### macOS

- **Login Items:**  
  Convert your script to an application (using [py2app](https://py2app.readthedocs.io/)) and add it to your Login Items in System Preferences.

- **Launch Agents:**  
  Create a Launch Agent (`.plist`) file in `~/Library/LaunchAgents` to run the script at startup.

### Linux

- **Systemd Service:**  
  Create a systemd service unit file to run the script on boot. Place the file in `/etc/systemd/system/` or `~/.config/systemd/user/` for user-level services, then enable it.

- **Cron @reboot:**  
  Add the following line to your crontab:
  
  ```bash
  @reboot /usr/bin/python3 /path/to/file_integrity_monitor.py
  ```

## Contributing

Contributions are welcome! Feel free to fork the repository, make improvements, and submit pull requests.


Feel free to adjust the content and instructions to better fit your project’s specifics and any additional details you want to provide.
