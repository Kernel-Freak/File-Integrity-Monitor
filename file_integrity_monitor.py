import hashlib
import os
import sqlite3
import time
import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Configure logging
logging.basicConfig(
    filename='file_integrity.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# Database initialization
def initialize_db(db_path='file_integrity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_hashes (
                       file_path TEXT PRIMARY KEY,
                       hash_value TEXT NOT NULL,
                       last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )''')
    conn.commit()
    conn.close()

# Hashing function with error handling for corrupted files
def hash_file(file_path, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logging.error(f"Error reading file: {file_path}. Exception: {e}")
        return None

# Database operations
def store_hash(file_path, hash_value, db_path='file_integrity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO file_hashes (file_path, hash_value, last_checked)
                      VALUES (?, ?, CURRENT_TIMESTAMP)''', (file_path, hash_value))
    conn.commit()
    conn.close()

def get_stored_hash(file_path, db_path='file_integrity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT hash_value FROM file_hashes WHERE file_path = ?', (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def remove_file_entry(file_path, db_path='file_integrity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM file_hashes WHERE file_path = ?', (file_path,))
    conn.commit()
    conn.close()

# Get all files in directories
def get_all_files(paths):
    all_files = []
    for path in paths:
        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    all_files.append(os.path.join(root, file))
    return all_files

# Monitor files and directories
def monitor_files(paths, db_path='file_integrity.db', algorithm='sha256'):
    current_files = set(get_all_files(paths))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT file_path FROM file_hashes')
    stored_files = set(row[0] for row in cursor.fetchall())
    conn.close()
    
    # Handle deleted files: log as error
    deleted_files = stored_files - current_files
    for file_path in deleted_files:
        logging.error(f"File deleted: {file_path}")
        remove_file_entry(file_path, db_path)

    # Monitor each file
    for file_path in current_files:
        if os.path.isfile(file_path):
            current_hash = hash_file(file_path, algorithm)
            if current_hash is None:
                # Hashing failed: file might be corrupted or unreadable
                logging.error(f"File corrupted or unreadable: {file_path}")
                continue
            
            stored_hash = get_stored_hash(file_path, db_path)
            
            if stored_hash is None:
                logging.info(f"File opened: {file_path}. New file detected. Storing initial hash.")
                store_hash(file_path, current_hash, db_path)
            elif stored_hash != current_hash:
                # Log changes as warning instead of error
                logging.warning(f"Unauthorized change detected in: {file_path}")
                store_hash(file_path, current_hash, db_path)
            else:
                # File opened and no changes detected
                logging.info(f"File opened: {file_path}. No changes detected.")
        else:
            logging.error(f"File not found during scan: {file_path}.")

# GUI for selecting and deselecting files and directories with manual start/stop
class FileMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Integrity Monitor")
        self.selected_paths = []
        self.monitoring_thread = None
        self.stop_event = threading.Event()

        self.listbox = tk.Listbox(root, width=60, height=20, selectmode=tk.MULTIPLE)
        self.listbox.pack(padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        add_file_btn = tk.Button(btn_frame, text="Add Files", command=self.add_files)
        add_file_btn.grid(row=0, column=0, padx=5)

        add_dir_btn = tk.Button(btn_frame, text="Add Directories", command=self.add_directories)
        add_dir_btn.grid(row=0, column=1, padx=5)

        remove_btn = tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.grid(row=0, column=2, padx=5)

        self.start_monitor_btn = tk.Button(btn_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_monitor_btn.grid(row=0, column=3, padx=5)

        self.stop_monitor_btn = tk.Button(btn_frame, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_monitor_btn.grid(row=0, column=4, padx=5)

    def add_files(self):
        file_paths = filedialog.askopenfilenames()  # Allow multiple files to be selected
        for path in file_paths:
            if path not in self.selected_paths:
                self.selected_paths.append(path)
                self.listbox.insert(tk.END, path)

    def add_directories(self):
        dir_path = filedialog.askdirectory()  # Allow directory selection (one at a time)
        if dir_path and dir_path not in self.selected_paths:
            self.selected_paths.append(dir_path)
            self.listbox.insert(tk.END, dir_path)

    def remove_selected(self):
        selected_indices = list(self.listbox.curselection())
        for index in reversed(selected_indices):
            path_to_remove = self.listbox.get(index)
            self.selected_paths.remove(path_to_remove)
            self.listbox.delete(index)

    def monitoring_loop(self):
        # Loop until the stop event is set
        while not self.stop_event.is_set():
            monitor_files(self.selected_paths)
            # Wait for 60 seconds, but break early if stop_event is set
            for _ in range(60):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def start_monitoring(self):
        if not self.selected_paths:
            messagebox.showwarning("Warning", "No files or directories selected.")
            return
        initialize_db()
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.start_monitor_btn.config(state=tk.DISABLED)
        self.stop_monitor_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Monitoring Started", "File monitoring has started in the background.")

    def stop_monitoring(self):
        self.stop_event.set()
        if self.monitoring_thread is not None:
            self.monitoring_thread.join(timeout=2)
        self.start_monitor_btn.config(state=tk.NORMAL)
        self.stop_monitor_btn.config(state=tk.DISABLED)
        messagebox.showinfo("Monitoring Stopped", "File monitoring has been stopped.")

if __name__ == '__main__':
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.mainloop()
