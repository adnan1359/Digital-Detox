import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import subprocess
import json
import os
import time
import threading
import psutil
from datetime import datetime, timedelta
import winreg
import ctypes
import re
import socket

class DigitalDetoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Detox")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set application icon and theme
        self.root.iconbitmap(default="")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Define colors
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#6b8cae"
        self.accent_color = "#e67a45"
        self.bg_color = "#f5f5f5"
        self.text_color = "#333333"
        
        # Configure styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TButton", background=self.primary_color, foreground="white", font=("Arial", 10, "bold"))
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white", font=("Arial", 10, "bold"))
        
        # Initialize data structures
        self.blocked_apps = []
        self.routine_blocks = []
        self.internet_blocks = []
        self.cooling_period_minutes = 15
        self.block_threads = {}
        self.internet_block_active = False
        
        # Load saved data
        self.data_file = os.path.join(os.path.expanduser("~"), "digital_detox_data.json")
        self.load_data()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create Dashboard tab
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Create Apps tab
        self.apps_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_tab, text="Block Apps")
        
        # Create Internet tab
        self.internet_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.internet_tab, text="Block Internet")
        
        # Create Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Set up each tab
        self.setup_dashboard()
        self.setup_apps_tab()
        self.setup_internet_tab()
        self.setup_settings_tab()
        
        # Start a watchdog thread to enforce blocks
        self.watchdog_thread = threading.Thread(target=self.block_watchdog, daemon=True)
        self.watchdog_thread.start()
        
        # Schedule data saving
        self.schedule_data_saving()
        
        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                self.blocked_apps = data.get("blocked_apps", [])
                self.routine_blocks = data.get("routine_blocks", [])
                self.internet_blocks = data.get("internet_blocks", [])
                self.cooling_period_minutes = data.get("cooling_period_minutes", 15)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load saved data: {e}")
    
    def save_data(self):
        try:
            data = {
                "blocked_apps": self.blocked_apps,
                "routine_blocks": self.routine_blocks,
                "internet_blocks": self.internet_blocks,
                "cooling_period_minutes": self.cooling_period_minutes
            }
            with open(self.data_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
    
    def schedule_data_saving(self):
        self.save_data()
        self.root.after(60000, self.schedule_data_saving)  # Save every minute
    
    def setup_dashboard(self):
        # Create header
        header_frame = ttk.Frame(self.dashboard_tab)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(header_frame, text="Digital Detox Dashboard", font=("Arial", 16, "bold"))
        title.pack(side=tk.LEFT)
        
        # Create content frame
        content_frame = ttk.Frame(self.dashboard_tab)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Active blocks section
        active_frame = ttk.LabelFrame(content_frame, text="Active Blocks", padding=10)
        active_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a treeview for active blocks
        self.active_blocks_tree = ttk.Treeview(active_frame, columns=("Type", "Target", "End Time", "Actions"), show="headings")
        self.active_blocks_tree.heading("Type", text="Type")
        self.active_blocks_tree.heading("Target", text="Target")
        self.active_blocks_tree.heading("End Time", text="End Time")
        self.active_blocks_tree.heading("Actions", text="Actions")
        
        self.active_blocks_tree.column("Type", width=100)
        self.active_blocks_tree.column("Target", width=200)
        self.active_blocks_tree.column("End Time", width=150)
        self.active_blocks_tree.column("Actions", width=100)
        
        self.active_blocks_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for active blocks
        scrollbar = ttk.Scrollbar(active_frame, orient=tk.VERTICAL, command=self.active_blocks_tree.yview)
        self.active_blocks_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Upcoming blocks section
        upcoming_frame = ttk.LabelFrame(content_frame, text="Upcoming Routine Blocks", padding=10)
        upcoming_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a treeview for upcoming blocks
        self.upcoming_blocks_tree = ttk.Treeview(upcoming_frame, columns=("Type", "Target", "Start Time", "End Time", "Days"), show="headings")
        self.upcoming_blocks_tree.heading("Type", text="Type")
        self.upcoming_blocks_tree.heading("Target", text="Target")
        self.upcoming_blocks_tree.heading("Start Time", text="Start Time")
        self.upcoming_blocks_tree.heading("End Time", text="End Time")
        self.upcoming_blocks_tree.heading("Days", text="Days")
        
        self.upcoming_blocks_tree.column("Type", width=100)
        self.upcoming_blocks_tree.column("Target", width=150)
        self.upcoming_blocks_tree.column("Start Time", width=100)
        self.upcoming_blocks_tree.column("End Time", width=100)
        self.upcoming_blocks_tree.column("Days", width=150)
        
        self.upcoming_blocks_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for upcoming blocks
        scrollbar_upcoming = ttk.Scrollbar(upcoming_frame, orient=tk.VERTICAL, command=self.upcoming_blocks_tree.yview)
        self.upcoming_blocks_tree.configure(yscroll=scrollbar_upcoming.set)
        scrollbar_upcoming.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Stats section
        stats_frame = ttk.LabelFrame(content_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stats content
        self.stats_label = ttk.Label(stats_frame, text="No blocks active")
        self.stats_label.pack(pady=10)
        
        # Quick actions
        actions_frame = ttk.Frame(self.dashboard_tab)
        actions_frame.pack(fill=tk.X, pady=20)
        
        quick_block_btn = ttk.Button(actions_frame, text="Quick Block App", command=self.quick_block_app)
        quick_block_btn.pack(side=tk.LEFT, padx=5)
        
        quick_internet_btn = ttk.Button(actions_frame, text="Quick Block Internet", command=self.quick_block_internet)
        quick_internet_btn.pack(side=tk.LEFT, padx=5)
        
        # Schedule dashboard updates
        self.update_dashboard()
    
    def update_dashboard(self):
        # Clear existing items
        for item in self.active_blocks_tree.get_children():
            self.active_blocks_tree.delete(item)
        for item in self.upcoming_blocks_tree.get_children():
            self.upcoming_blocks_tree.delete(item)
        
        current_time = datetime.now()
        active_blocks = 0
        current_day = current_time.strftime("%A")
        
        # Add quick app blocks to active treeview
        for app in self.blocked_apps:
            if "end_time" in app and datetime.fromisoformat(app["end_time"]) > current_time:
                active_blocks += 1
                end_time_str = datetime.fromisoformat(app["end_time"]).strftime("%H:%M:%S %d/%m/%Y")
                self.active_blocks_tree.insert("", "end", values=("Quick App", app["name"], end_time_str, "Remove"), 
                                             tags=(f"app_{app['name']}",))
        
        # Add routine blocks to active and upcoming treeviews
        for routine in self.routine_blocks:
            start_time = routine["start_time"]  # e.g., "09:00"
            end_time = routine["end_time"]      # e.g., "17:00"
            days = routine["days"]              # e.g., ["Monday", "Tuesday"]
            apps = routine["apps"]              # e.g., ["notepad.exe", "chrome.exe"]
            
            # Check if routine is active now
            current_time_str = current_time.strftime("%H:%M")
            is_active_day = current_day in days
            is_active_time = start_time <= current_time_str < end_time
            
            if is_active_day and is_active_time:
                active_blocks += len(apps)
                for app in apps:
                    # Calculate end time for today
                    end_datetime = datetime.strptime(f"{current_time.date()} {end_time}", "%Y-%m-%d %H:%M")
                    if end_datetime < current_time:
                        end_datetime += timedelta(days=1)
                    end_time_str = end_datetime.strftime("%H:%M:%S %d/%m/%Y")
                    self.active_blocks_tree.insert("", "end", values=("Routine App", app, end_time_str, "Remove"),
                                                 tags=(f"app_{app}",))
            
            # Add to upcoming blocks if within the next 7 days
            for i in range(7):
                future_date = current_time + timedelta(days=i)
                future_day = future_date.strftime("%A")
                if future_day in days:
                    start_datetime = datetime.strptime(f"{future_date.date()} {start_time}", "%Y-%m-%d %H:%M")
                    end_datetime = datetime.strptime(f"{future_date.date()} {end_time}", "%Y-%m-%d %H:%M")
                    if end_datetime < start_datetime:
                        end_datetime += timedelta(days=1)
                    if start_datetime > current_time:
                        days_str = ", ".join(days)
                        apps_str = ", ".join(apps)
                        self.upcoming_blocks_tree.insert("", "end", 
                                                       values=("Routine App", apps_str, 
                                                               start_datetime.strftime("%H:%M %d/%m/%Y"),
                                                               end_datetime.strftime("%H:%M %d/%m/%Y"),
                                                               days_str))
        
        # Add internet blocks to active treeview
        for block in self.internet_blocks:
            if "end_time" in block and datetime.fromisoformat(block["end_time"]) > current_time:
                active_blocks += 1
                end_time_str = datetime.fromisoformat(block["end_time"]).strftime("%H:%M:%S %d/%m/%Y")
                self.active_blocks_tree.insert("", "end", values=("Internet", "All websites", end_time_str, "Remove"),
                                             tags=("internet",))
        
        # Update stats
        if active_blocks > 0:
            self.stats_label.config(text=f"{active_blocks} active block(s)")
        else:
            self.stats_label.config(text="No blocks active")
        
        # Refresh every second
        self.root.after(1000, self.update_dashboard)
    
    def quick_block_app(self):
        running_apps = self.get_running_applications()
        if not running_apps:
            messagebox.showinfo("Info", "No applications detected")
            return
        
        app_selection = simpledialog.askstring(
            "Select Application", 
            "Choose an application to block:\n" + "\n".join([f"{i+1}. {app}" for i, app in enumerate(running_apps)])
        )
        
        if not app_selection:
            return
        
        try:
            idx = int(app_selection) - 1
            if 0 <= idx < len(running_apps):
                app_name = running_apps[idx]
            else:
                messagebox.showerror("Error", "Invalid selection")
                return
        except ValueError:
            # Try to match by name
            matching = [app for app in running_apps if app_selection.lower() in app.lower()]
            if len(matching) == 1:
                app_name = matching[0]
            elif len(matching) > 1:
                messagebox.showerror("Error", "Multiple matches found. Please be more specific.")
                return
            else:
                messagebox.showerror("Error", "No matching application found")
                return
        
        duration = simpledialog.askinteger("Block Duration", "Enter duration in minutes:", minvalue=1, maxvalue=1440)
        if duration:
            self.block_app(app_name, duration)
    
    def quick_block_internet(self):
        duration = simpledialog.askinteger("Block Internet", "Enter duration in minutes:", minvalue=1, maxvalue=1440)
        if duration:
            self.block_internet(duration)
    
    def setup_apps_tab(self):
        # Create container for app blocking
        app_frame = ttk.Frame(self.apps_tab, padding=10)
        app_frame.pack(fill=tk.BOTH, expand=True)
        
        # Quick Block Section
        quick_frame = ttk.LabelFrame(app_frame, text="Quick Block", padding=10)
        quick_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Running applications label
        ttk.Label(quick_frame, text="Running Applications:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Search bar
        search_frame = ttk.Frame(quick_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_app_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Create frame for app list and scrollbar
        list_frame = ttk.Frame(quick_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # App listbox with scrollbar
        self.app_listbox = tk.Listbox(list_frame, height=10, selectmode=tk.SINGLE)
        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.app_listbox.yview)
        self.app_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = ttk.Frame(quick_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Refresh button
        refresh_btn = ttk.Button(buttons_frame, text="Refresh Application List", command=self.refresh_app_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Choose app by path button
        choose_path_btn = ttk.Button(buttons_frame, text="Choose App by Path", command=self.choose_app_by_path)
        choose_path_btn.pack(side=tk.LEFT, padx=5)
        
        # Block controls frame
        block_frame = ttk.Frame(quick_frame)
        block_frame.pack(fill=tk.X, pady=10)
        
        # Duration input
        ttk.Label(block_frame, text="Block Duration (minutes):").pack(side=tk.LEFT, padx=5)
        self.duration_var = tk.StringVar(value="60")
        duration_entry = ttk.Entry(block_frame, textvariable=self.duration_var, width=5)
        duration_entry.pack(side=tk.LEFT, padx=5)
        
        # Block button
        block_btn = ttk.Button(
            block_frame, 
            text="Block Selected App", 
            command=self.block_selected_app,
            style="Accent.TButton"
        )
        block_btn.pack(side=tk.LEFT, padx=20)
        
        # Routine Block Section
        routine_frame = ttk.LabelFrame(app_frame, text="Routine Block", padding=10)
        routine_frame.pack(fill=tk.X, pady=5)
        
        # Routine block button
        routine_btn = ttk.Button(
            routine_frame, 
            text="Set Up Routine Block", 
            command=self.setup_routine_block,
            style="Accent.TButton"
        )
        routine_btn.pack(pady=10)
        
        # Store full app list for filtering
        self.full_app_list = []
        
        # Populate app list
        self.refresh_app_list()
    
    def setup_routine_block(self):
        # Step 1: Select Apps
        wizard = tk.Toplevel(self.root)
        wizard.title("Routine Block Setup")
        wizard.geometry("400x500")
        wizard.resizable(False, False)
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Center the window
        wizard.update_idletasks()
        width = wizard.winfo_width()
        height = wizard.winfo_height()
        x = (wizard.winfo_screenwidth() // 2) - (width // 2)
        y = (wizard.winfo_screenheight() // 2) - (height // 2)
        wizard.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ttk.Frame(wizard, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Select Applications to Block:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # App listbox for selection
        app_listbox = tk.Listbox(frame, height=10, selectmode=tk.MULTIPLE)
        for app in self.get_running_applications():
            app_listbox.insert(tk.END, app)
        app_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=app_listbox.yview)
        app_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def next_step():
            selected_apps = [app_listbox.get(i) for i in app_listbox.curselection()]
            if not selected_apps:
                messagebox.showinfo("Info", "Please select at least one application")
                return
            wizard.destroy()
            self.setup_routine_time(selected_apps)
        
        ttk.Button(button_frame, text="Next", command=next_step, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=wizard.destroy).pack(side=tk.RIGHT, padx=5)
    
    def setup_routine_time(self, selected_apps):
        # Step 2: Select Time and Days
        wizard = tk.Toplevel(self.root)
        wizard.title("Routine Block Setup")
        wizard.geometry("400x500")
        wizard.resizable(False, False)
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Center the window
        wizard.update_idletasks()
        width = wizard.winfo_width()
        height = wizard.winfo_height()
        x = (wizard.winfo_screenwidth() // 2) - (width // 2)
        y = (wizard.winfo_screenheight() // 2) - (height // 2)
        wizard.geometry(f"{width}x{height}+{x}+{y}")
        
        frame = ttk.Frame(wizard, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Set Block Schedule:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Start time
        ttk.Label(frame, text="Start Time (HH:MM):").pack(anchor=tk.W, padx=5)
        start_time_var = tk.StringVar(value="09:00")
        start_time_entry = ttk.Entry(frame, textvariable=start_time_var, width=10)
        start_time_entry.pack(anchor=tk.W, padx=5, pady=5)
        
        # End time
        ttk.Label(frame, text="End Time (HH:MM):").pack(anchor=tk.W, padx=5)
        end_time_var = tk.StringVar(value="17:00")
        end_time_entry = ttk.Entry(frame, textvariable=end_time_var, width=10)
        end_time_entry.pack(anchor=tk.W, padx=5, pady=5)
        
        # Days of the week
        ttk.Label(frame, text="Active Days:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        days_frame = ttk.Frame(frame)
        days_frame.pack(fill=tk.X, padx=5)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_vars = {day: tk.BooleanVar(value=False) for day in days}
        
        for day in days:
            ttk.Checkbutton(days_frame, text=day, variable=day_vars[day]).pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def save_routine():
            # Validate time format
            time_pattern = r"^\d{2}:\d{2}$"
            start_time = start_time_var.get()
            end_time = end_time_var.get()
            
            if not (re.match(time_pattern, start_time) and re.match(time_pattern, end_time)):
                messagebox.showerror("Error", "Time must be in HH:MM format")
                return
            
            try:
                datetime.strptime(start_time, "%H:%M")
                datetime.strptime(end_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid time format")
                return
            
            # Get selected days
            selected_days = [day for day, var in day_vars.items() if var.get()]
            if not selected_days:
                messagebox.showerror("Error", "Please select at least one day")
                return
            
            # Save routine block
            routine = {
                "apps": selected_apps,
                "start_time": start_time,
                "end_time": end_time,
                "days": selected_days
            }
            self.routine_blocks.append(routine)
            self.save_data()
            
            # Show confirmation
            wizard.destroy()
            apps_str = ", ".join(selected_apps)
            days_str = ", ".join(selected_days)
            messagebox.showinfo("Success", 
                               f"Routine block set for {apps_str}\n"
                               f"From {start_time} to {end_time} on {days_str}")
        
        ttk.Button(button_frame, text="Save", command=save_routine, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=wizard.destroy).pack(side=tk.RIGHT, padx=5)
    
    def refresh_app_list(self):
        self.app_listbox.delete(0, tk.END)
        self.full_app_list = self.get_running_applications()
        for app in self.full_app_list:
            self.app_listbox.insert(tk.END, app)
    
    def filter_app_list(self, *args):
        search_term = self.search_var.get().lower()
        self.app_listbox.delete(0, tk.END)
        for app in self.full_app_list:
            if search_term in app.lower():
                self.app_listbox.insert(tk.END, app)
    
    def choose_app_by_path(self):
        file_path = filedialog.askopenfilename(
            title="Select Application",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            app_name = os.path.basename(file_path)
            duration = simpledialog.askinteger("Block Duration", f"Enter duration in minutes for {app_name}:", minvalue=1, maxvalue=1440)
            if duration:
                self.block_app(app_name, duration)
    
    def get_running_applications(self):
        running_apps = set()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = proc.info
                if proc_info['name'] and proc_info['name'].endswith('.exe'):
                    running_apps.add(proc_info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return sorted(list(running_apps))
    
    def block_selected_app(self):
        if not self.app_listbox.curselection():
            messagebox.showinfo("Info", "Please select an application to block")
            return
        
        app_name = self.app_listbox.get(self.app_listbox.curselection())
        
        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return
        
        self.block_app(app_name, duration)
    
    def block_app(self, app_name, duration):
        # Check if app is already blocked
        for app in self.blocked_apps:
            if app["name"] == app_name and "end_time" in app:
                end_time = datetime.fromisoformat(app["end_time"])
                if end_time > datetime.now():
                    response = messagebox.askyesno(
                        "App Already Blocked", 
                        f"{app_name} is already blocked until {end_time.strftime('%H:%M:%S %d/%m/%Y')}. Do you want to extend the block?"
                    )
                    if not response:
                        return
                    # Remove existing block
                    self.blocked_apps = [a for a in self.blocked_apps if a["name"] != app_name]
                    break
        
        end_time = datetime.now() + timedelta(minutes=duration)
        
        # Add to blocked apps list
        self.blocked_apps.append({
            "name": app_name,
            "start_time": datetime.now().isoformat(),
            "end_time": end_time.isoformat()
        })
        
        # Save data
        self.save_data()
        
        # Kill current instances of the app
        self.kill_app(app_name)
        
        # Start a blocking thread
        if app_name in self.block_threads:
            self.block_threads[app_name].stop()
        
        thread = AppBlockThread(app_name, end_time)
        thread.start()
        self.block_threads[app_name] = thread
        
        messagebox.showinfo("Success", f"{app_name} has been blocked until {end_time.strftime('%H:%M:%S %d/%m/%Y')}")
    
    def kill_app(self, app_name):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == app_name:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    def setup_internet_tab(self):
        # Create container for internet blocking
        internet_frame = ttk.Frame(self.internet_tab, padding=10)
        internet_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(internet_frame, text="Block Internet Access", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(internet_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.internet_status_var = tk.StringVar(value="Not Blocked")
        status_label = ttk.Label(status_frame, textvariable=self.internet_status_var, font=("Arial", 10, "bold"))
        status_label.pack(side=tk.LEFT, padx=5)
        
        # Block controls frame
        block_frame = ttk.Frame(internet_frame)
        block_frame.pack(fill=tk.X, pady=20)
        
        # Duration input
        ttk.Label(block_frame, text="Block Duration (minutes):").pack(side=tk.LEFT, padx=5)
        self.internet_duration_var = tk.StringVar(value="30")
        duration_entry = ttk.Entry(block_frame, textvariable=self.internet_duration_var, width=5)
        duration_entry.pack(side=tk.LEFT, padx=5)
        
        # Block button
        self.block_internet_btn = ttk.Button(
            block_frame, 
            text="Block Internet", 
            command=self.block_internet_action,
            style="Accent.TButton"
        )
        self.block_internet_btn.pack(side=tk.LEFT, padx=20)
        
        # Information
        info_frame = ttk.LabelFrame(internet_frame, text="Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        info_text = (
            "When you block internet access:\n\n"
            "• All network connections will be disabled\n"
            "• You won't be able to access any websites or online services\n"
            "• The block will remain active for the specified duration\n"
            "• If you try to remove the block early, you'll need to wait for the cooling period\n\n"
            "This feature requires administrator privileges to modify network settings."
        )
        
        info_label = ttk.Label(info_frame, text=info_text, wraplength=500, justify=tk.LEFT)
        info_label.pack(fill=tk.BOTH, expand=True)
        
        # Update internet status
        self.update_internet_status()
    
    def update_internet_status(self):
        current_time = datetime.now()
        active_block = None
        
        for block in self.internet_blocks:
            if "end_time" in block:
                end_time = datetime.fromisoformat(block["end_time"])
                if end_time > current_time:
                    active_block = block
                    break
        
        if active_block:
            end_time = datetime.fromisoformat(active_block["end_time"])
            remaining = end_time - current_time
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            else:
                time_str = f"{minutes}m {seconds}s"
                
            self.internet_status_var.set(f"Blocked (Remaining: {time_str})")
            self.block_internet_btn.config(text="Extend Block", command=self.extend_internet_block)
        else:
            self.internet_status_var.set("Not Blocked")
            self.block_internet_btn.config(text="Block Internet", command=self.block_internet_action)
        
        # Update every second
        self.root.after(1000, self.update_internet_status)
    
    def block_internet_action(self):
        try:
            duration = int(self

            .internet_duration_var.get())
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return
        
        # Check if we need to elevate privileges
        if not self.is_admin():
            messagebox.showinfo("Admin Required", "This action requires administrator privileges. The application will restart with elevated privileges.")
            self.restart_as_admin()
            return
        
        self.block_internet(duration)
    
    def block_internet(self, duration):
        end_time = datetime.now() + timedelta(minutes=duration)
        
        # Add to internet blocks list
        self.internet_blocks.append({
            "start_time": datetime.now().isoformat(),
            "end_time": end_time.isoformat()
        })
        
        # Save data
        self.save_data()
        
        # Disable network adapters
        try:
            self.disable_network_adapters()
            self.internet_block_active = True
            messagebox.showinfo("Success", f"Internet has been blocked until {end_time.strftime('%H:%M:%S %d/%m/%Y')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to block internet: {e}")
    
    def extend_internet_block(self):
        try:
            additional_duration = int(self.internet_duration_var.get())
            if additional_duration <= 0:
                messagebox.showerror("Error", "Duration must be positive")
                return
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number")
            return
        
        # Find current active block
        current_time = datetime.now()
        active_block = None
        active_index = -1
        
        for i, block in enumerate(self.internet_blocks):
            if "end_time" in block:
                end_time = datetime.fromisoformat(block["end_time"])
                if end_time > current_time:
                    active_block = block
                    active_index = i
                    break
        
        if active_block:
            # Extend the end time
            current_end_time = datetime.fromisoformat(active_block["end_time"])
            new_end_time = current_end_time + timedelta(minutes=additional_duration)
            
            # Update the block
            self.internet_blocks[active_index]["end_time"] = new_end_time.isoformat()
            
            # Save data
            self.save_data()
            
            messagebox.showinfo("Success", f"Internet block extended until {new_end_time.strftime('%H:%M:%S %d/%m/%Y')}")
        else:
            # No active block, create a new one
            self.block_internet(additional_duration)
    
    def disable_network_adapters(self):
        subprocess.run(["netsh", "interface", "set", "interface", "name=*", "admin=disabled"], check=True)
    
    def enable_network_adapters(self):
        subprocess.run(["netsh", "interface", "set", "interface", "name=*", "admin=enabled"], check=True)
    
    def setup_settings_tab(self):
        # Create container for settings
        settings_frame = ttk.Frame(self.settings_tab, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(settings_frame, text="Settings", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 20))
        
        # Cooling period settings
        cooling_frame = ttk.LabelFrame(settings_frame, text="Cooling Period", padding=10)
        cooling_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(cooling_frame, text="Wait time before removing blocks (minutes):").pack(side=tk.LEFT, padx=5)
        
        self.cooling_period_var = tk.StringVar(value=str(self.cooling_period_minutes))
        cooling_entry = ttk.Entry(cooling_frame, textvariable=self.cooling_period_var, width=5)
        cooling_entry.pack(side=tk.LEFT, padx=5)
        
        save_cooling_btn = ttk.Button(cooling_frame, text="Save", command=self.save_cooling_period)
        save_cooling_btn.pack(side=tk.LEFT, padx=20)
        
        # Auto-start settings
        autostart_frame = ttk.LabelFrame(settings_frame, text="Start with Windows", padding=10)
        autostart_frame.pack(fill=tk.X, pady=10)
        
        self.autostart_var = tk.BooleanVar(value=self.check_autostart())
        autostart_check = ttk.Checkbutton(
            autostart_frame, 
            text="Start Digital Detox when Windows boots", 
            variable=self.autostart_var,
            command=self.toggle_autostart
        )
        autostart_check.pack(anchor=tk.W, padx=5)
        
        # About section
        about_frame = ttk.LabelFrame(settings_frame, text="About", padding=10)
        about_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        about_text = (
            "Digital Detox - v1.0.0\n\n"
            "This application helps you manage your digital habits by:\n\n"
            "• Blocking distracting applications for set periods\n"
            "• Disabling internet access when you need to focus\n"
            "• Enforcing a cooling period to prevent impulsive unblocking\n\n"
            "Thank you for using Digital Detox!"
        )
        
        about_label = ttk.Label(about_frame, text=about_text, wraplength=500, justify=tk.LEFT)
        about_label.pack(fill=tk.BOTH, expand=True)
    
    def save_cooling_period(self):
        try:
            period = int(self.cooling_period_var.get())
            if period < 0:
                messagebox.showerror("Error", "Cooling period must be non-negative")
                return
            
            self.cooling_period_minutes = period
            self.save_data()
            messagebox.showinfo("Success", "Cooling period updated")
        except ValueError:
            messagebox.showerror("Error", "Cooling period must be a number")
    
    def check_autostart(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, "DigitalDetox")
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except WindowsError:
            return False
    
    def toggle_autostart(self):
        enabled = self.autostart_var.get()
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_WRITE
            )
            
            if enabled:
                # Add to startup
                winreg.SetValueEx(
                    key, 
                    "DigitalDetox", 
                    0, 
                    winreg.REG_SZ, 
                    os.path.abspath(sys.argv[0])
                )
                messagebox.showinfo("Success", "Digital Detox will start with Windows")
            else:
                # Remove from startup
                try:
                    winreg.DeleteValue(key, "DigitalDetox")
                    messagebox.showinfo("Success", "Digital Detox will not start with Windows")
                except WindowsError:
                    pass
                
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update startup settings: {e}")
    
    def block_watchdog(self):
        """Thread to continuously enforce blocks"""
        while True:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")
            current_day = current_time.strftime("%A")
            
            # Check quick app blocks
            for app in self.blocked_apps:
                if "end_time" in app:
                    end_time = datetime.fromisoformat(app["end_time"])
                    if end_time > current_time:
                        self.kill_app(app["name"])
            
            # Check routine blocks
            for routine in self.routine_blocks:
                start_time = routine["start_time"]
                end_time = routine["end_time"]
                days = routine["days"]
                apps = routine["apps"]
                
                if current_day in days and start_time <= current_time_str < end_time:
                    for app in apps:
                        self.kill_app(app)
                        # Ensure a blocking thread is running
                        if app not in self.block_threads or not self.block_threads[app].is_alive():
                            # Use end of day as end time for thread
                            end_datetime = datetime.strptime(f"{current_time.date()} {end_time}", "%Y-%m-%d %H:%M")
                            if end_datetime < current_time:
                                end_datetime += timedelta(days=1)
                            thread = AppBlockThread(app, end_datetime)
                            thread.start()
                            self.block_threads[app] = thread
            
            # Check internet blocks
            internet_should_be_blocked = False
            for block in self.internet_blocks:
                if "end_time" in block:
                    end_time = datetime.fromisoformat(block["end_time"])
                    if end_time > current_time:
                        internet_should_be_blocked = True
                        break
            
            # Enforce internet block if needed
            if internet_should_be_blocked and not self.internet_block_active:
                try:
                    self.disable_network_adapters()
                    self.internet_block_active = True
                except Exception:
                    pass
            elif not internet_should_be_blocked and self.internet_block_active:
                try:
                    self.enable_network_adapters()
                    self.internet_block_active = False
                except Exception:
                    pass
            
            # Sleep for a short time
            time.sleep(2)
    
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def restart_as_admin(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart with admin privileges: {e}")
    
    def attempt_unblock(self, block_type, target=None):
        """Handle unblock attempts with cooling period"""
        # Check if there are any active blocks
        current_time = datetime.now()
        active_blocks = []
        
        if block_type == "app" and target:
            for app in self.blocked_apps:
                if app["name"] == target and "end_time" in app:
                    end_time = datetime.fromisoformat(app["end_time"])
                    if end_time > current_time:
                        active_blocks.append(app)
        elif block_type == "internet":
            for block in self.internet_blocks:
                if "end_time" in block:
                    end_time = datetime.fromisoformat(block["end_time"])
                    if end_time > current_time:
                        active_blocks.append(block)
        
        if not active_blocks:
            messagebox.showinfo("Info", "No active blocks to remove")
            return
        
        # Ask user to confirm with cooling period warning
        response = messagebox.askyesno(
            "Cooling Period", 
            f"Removing this block requires a {self.cooling_period_minutes} minute cooling period. Proceed?"
        )
        
        if not response:
            return
        
        # Create cooling period window
        cooling_window = tk.Toplevel(self.root)
        cooling_window.title("Cooling Period")
        cooling_window.geometry("300x150")
        cooling_window.resizable(False, False)
        cooling_window.transient(self.root)
        cooling_window.grab_set()
        
        # Center the window
        cooling_window.update_idletasks()
        width = cooling_window.winfo_width()
        height = cooling_window.winfo_height()
        x = (cooling_window.winfo_screenwidth() // 2) - (width // 2)
        y = (cooling_window.winfo_screenheight() // 2) - (height // 2)
        cooling_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add content to cooling window
        frame = ttk.Frame(cooling_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        message_label = ttk.Label(
            frame, 
            text=f"Please wait {self.cooling_period_minutes} minutes before removing the block",
            wraplength=250,
            justify=tk.CENTER
        )
        message_label.pack(pady=10)
        
        # Timer variables
        end_time = datetime.now() + timedelta(minutes=self.cooling_period_minutes)
        timer_var = tk.StringVar(value="")
        
        timer_label = ttk.Label(frame, textvariable=timer_var, font=("Arial", 14, "bold"))
        timer_label.pack(pady=10)
        
        # Cancel button
        cancel_btn = ttk.Button(frame, text="Cancel", command=cooling_window.destroy)
        cancel_btn.pack(pady=10)
        
        # Timer update function
        def update_timer():
            remaining = end_time - datetime.now()
            if remaining.total_seconds() <= 0:
                # Time's up, allow unblocking
                cooling_window.destroy()
                self.perform_unblock(block_type, target)
                return
            
            # Update timer text
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            timer_var.set(f"{minutes:02d}:{seconds:02d}")
            cooling_window.after(1000, update_timer)
        
        # Start timer update
        update_timer()
    
    def perform_unblock(self, block_type, target=None):
        """Actually perform the unblock after cooling period"""
        if block_type == "app" and target:
            # Remove app from quick blocked list
            self.blocked_apps = [app for app in self.blocked_apps if app["name"] != target]
            
            # Stop blocking thread if exists
            if target in self.block_threads:
                self.block_threads[target].stop()
                del self.block_threads[target]
            
            messagebox.showinfo("Success", f"{target} has been unblocked")
        
        elif block_type == "internet":
            # Remove all internet blocks
            self.internet_blocks = [block for block in self.internet_blocks 
                                  if "end_time" not in block or 
                                  datetime.fromisoformat(block["end_time"]) <= datetime.now()]
            
            # Enable network adapters
            try:
                self.enable_network_adapters()
                self.internet_block_active = False
                messagebox.showinfo("Success", "Internet has been unblocked")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to unblock internet: {e}")
        
        # Save data
        self.save_data()
    
    def on_closing(self):
        """Handle window closing"""
        # Check if there are active blocks
        current_time = datetime.now()
        has_active_blocks = False
        
        for app in self.blocked_apps:
            if "end_time" in app and datetime.fromisoformat(app["end_time"]) > current_time:
                has_active_blocks = True
                break
        
        for block in self.internet_blocks:
            if "end_time" in block and datetime.fromisoformat(block["end_time"]) > current_time:
                has_active_blocks = True
                break
        
        if has_active_blocks:
            # Warn the user about active blocks
            response = messagebox.askyesno(
                "Warning", 
                "There are active blocks that will continue running in the background. "
                "Would you like to minimize to system tray instead?"
            )
            
            if response:
                # Minimize to system tray
                self.root.withdraw()
                return
        
        # Exit application
        self.save_data()
        self.root.destroy()


class AppBlockThread(threading.Thread):
    """Thread for blocking a specific application"""
    
    def __init__(self, app_name, end_time):
        super().__init__(daemon=True)
        self.app_name = app_name
        self.end_time = end_time
        self._stop_event = threading.Event()
    
    def run(self):
        while not self._stop_event.is_set() and datetime.now() < self.end_time:
            # Check if the application is running and kill it
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == self.app_name:
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            # Sleep for a short time
            time.sleep(1)
    
    def stop(self):
        self._stop_event.set()


def main():
    # Check if we need to run as admin
    if 'runas' in sys.argv:
        # We're running with admin privileges
        pass
    
    # Create main window
    root = tk.Tk()
    app = DigitalDetoxApp(root)
    root.mainloop()


if __name__ == "__main__":
    import sys
    main()