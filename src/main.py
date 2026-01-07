import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import os
import sys
import ctypes
import subprocess
# import winreg # No longer needed for startup, but might be needed for other things? No, only used for startup in previous code.

from PIL import ImageTk
from utils.icon_generator import create_icon

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.runner import DNSRunner
from utils.tray import SystemTrayIcon

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

import webbrowser
from utils.config import ConfigManager

# ... imports ...

class App(ctk.CTk):
    def __init__(self, start_minimized=False):
        super().__init__()
        
        self.title("GoodbyeDPI-Turkey GUI")
        self.geometry("450x550")
        
        # Initialize Config
        self.config_manager = ConfigManager(os.path.dirname(os.path.abspath(__file__)))

        # Set Window Icon
        try:
            self.iconphoto(False, ImageTk.PhotoImage(create_icon()))
        except Exception as e:
            print(f"Failed to set icon: {e}")

        # Modern Styling config
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.runner = DNSRunner(os.path.dirname(os.path.abspath(__file__)), self.log_message)
        self.is_running = False
        self.tray_icon = None

        self.create_widgets()
        
        # Override window close event
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # Check startup logic
        self.check_startup_status()

        if start_minimized:
            self.hide_window() # Will create tray icon
            self.start_service() # Auto-start if starting minimized implies auto-run
            self.log_message("Started automatically via startup.")

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1) # Log area expands

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")
        
        # Column 0: Empty (spacer) or Logo, Column 1: Status, Column 2: Info Button
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=2) # Center status
        self.header_frame.grid_columnconfigure(2, weight=0) # Right align button
        
        self.status_label = ctk.CTkLabel(self.header_frame, text="Status: STOPPED", 
                                       font=("Roboto Medium", 20),
                                       text_color="#FF5555") 
        self.status_label.grid(row=0, column=1)

        # Info Button (About)
        self.btn_info = ctk.CTkButton(self.header_frame, text="?", width=30, height=30,
                                      fg_color="#444", hover_color="#666",
                                      command=self.open_about_window)
        self.btn_info.grid(row=0, column=2, sticky="e")

        self.status_circle = ctk.CTkProgressBar(self, width=200, height=10)
        self.status_circle.set(0)
        self.status_circle.grid(row=1, column=0, pady=(0, 20))

        # --- Settings Area ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # DNS Selection
        ctk.CTkLabel(self.settings_frame, text="DNS Provider:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.dns_options = {
            "Turkey DNSRedir": ("77.88.8.8", "1253"),
            "Yandex (Standard)": ("77.88.8.8", "1253"),
            "Google": ("8.8.8.8", "53"),
            "Cloudflare": ("1.1.1.1", "53"),
            "OpenDNS": ("208.67.222.222", "53")
        }
        
        # Load saved preference
        saved_dns = self.config_manager.get("dns_provider")
        if saved_dns not in self.dns_options:
            saved_dns = "Turkey DNSRedir"

        self.dns_var = ctk.StringVar(value=saved_dns)
        self.dns_menu = ctk.CTkOptionMenu(self.settings_frame, 
                                        variable=self.dns_var,
                                        values=list(self.dns_options.keys()),
                                        command=self.save_dns_preference)
        self.dns_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Startup Switch
        self.startup_var = ctk.BooleanVar(value=False)
        self.startup_switch = ctk.CTkSwitch(self.settings_frame, text="Run on Startup", 
                                          command=self.toggle_startup,
                                          variable=self.startup_var)
        self.startup_switch.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # --- Action Buttons ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=3, column=0, pady=10)

        self.btn_start = ctk.CTkButton(self.btn_frame, text="ACTIVATE", 
                                     command=self.start_service,
                                     width=150, height=40,
                                     fg_color="#00C853", hover_color="#009624")
        self.btn_start.pack(side="left", padx=10)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="DEACTIVATE", 
                                    command=self.stop_service,
                                    state="disabled",
                                    width=150, height=40,
                                    fg_color="#D50000", hover_color="#B71C1C")
        self.btn_stop.pack(side="left", padx=10)

        # --- Logs ---
        ctk.CTkLabel(self, text="Logs:", font=("Arial", 12)).grid(row=4, column=0, padx=20, sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(self, font=("Consolas", 10))
        self.log_textbox.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # --- Footer ---
        self.footer_label = ctk.CTkLabel(self, text="Developed by MacallanTheRoot", 
                                       font=("Arial", 11), text_color="gray", cursor="hand2")
        self.footer_label.grid(row=6, column=0, pady=(0, 10))
        self.footer_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/MacallanTheRoot"))
        self.footer_label.bind("<Enter>", lambda e: self.footer_label.configure(text_color="#3B8ED0"))
        self.footer_label.bind("<Leave>", lambda e: self.footer_label.configure(text_color="gray"))

    def save_dns_preference(self, choice):
        self.config_manager.save_config("dns_provider", choice)

    def open_about_window(self):
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("300x250")
        about.grab_set() # Modal
        
        ctk.CTkLabel(about, text="GoodbyeDPI-Turkey GUI", font=("Roboto Medium", 16)).pack(pady=(20, 5))
        ctk.CTkLabel(about, text="v1.0.0", font=("Arial", 12), text_color="gray").pack()
        
        ctk.CTkLabel(about, text="A secure & private DNS solution.\nDeveloped by MacallanTheRoot", 
                     wraplength=250, justify="center").pack(pady=20)
        
        def open_github():
            webbrowser.open("https://github.com/MacallanTheRoot")
            
        link = ctk.CTkLabel(about, text="Visit GitHub", text_color="#3B8ED0", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: open_github())

        ctk.CTkButton(about, text="Close", command=about.destroy, width=100).pack(pady=20)

    # ... rest of methods (start_service, stop_service, etc) unchanged ...

    def start_service(self):
        dns_name = self.dns_var.get()
        addr, port = self.dns_options[dns_name]
        
        self.log_message(f"Starting service with {dns_name} ({addr}:{port})...")
        try:
            self.runner.start(dns_addr=addr, dns_port=port)
            self.is_running = True
            self.update_status(True)
        except Exception as e:
            self.log_message(f"Error starting: {e}")

    def stop_service(self):
        self.log_message("Stopping service...")
        self.runner.stop()
        self.is_running = False
        self.update_status(False)
        self.log_message("Service stopped.")

    def update_status(self, running):
        if running:
            self.status_label.configure(text="Status: SECURE", text_color="#00E676")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.status_circle.configure(progress_color="#00E676")
            self.status_circle.set(1)
            self.dns_menu.configure(state="disabled")
        else:
            self.status_label.configure(text="Status: STOPPED", text_color="#FF5555")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.status_circle.configure(progress_color="gray")
            self.status_circle.set(0)
            self.dns_menu.configure(state="normal")

    def log_message(self, message):
        def _log():
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
        self.after(0, _log)

    def hide_window(self):
        self.withdraw()
        if not self.tray_icon:
            self.tray_thread = threading.Thread(target=self.run_tray)
            self.tray_thread.daemon = True
            self.tray_thread.start()

    def run_tray(self):
        self.tray_icon = SystemTrayIcon(self, self.show_window_from_tray, self.quit_app)
        self.tray_icon.run()

    def show_window_from_tray(self):
        self.after(0, self.deiconify)

    def quit_app(self):
        self.stop_service()
        self.quit()

    # --- Startup Logic (Shortcut based) ---
    def get_startup_path(self):
        return os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup', 'GoodbyeDPI-Turkey GUI.lnk')

    def check_startup_status(self):
        if os.path.exists(self.get_startup_path()):
            self.startup_var.set(True)
        else:
            self.startup_var.set(False)

    def toggle_startup(self):
        lnk_path = self.get_startup_path()
        if self.startup_var.get():
            # Create Shortcut
            try:
                exe = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(exe): exe = sys.executable
                
                script = os.path.abspath(__file__)
                # Arguments: script path + minimized flag
                args = f'"{script}" --minimized'
                
                # PowerShell command to create shortcut
                ps_cmd = f'$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut("{lnk_path}"); $SC.TargetPath = "{exe}"; $SC.Arguments = \'{args}\'; $SC.Save()'
                
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
                self.log_message("Added to startup (Shortcut created).")
            except Exception as e:
                self.log_message(f"Error creating shortcut: {e}")
                self.startup_var.set(False)
        else:
            # Remove Shortcut
            try:
                if os.path.exists(lnk_path):
                    os.remove(lnk_path)
                    self.log_message("Removed from startup.")
            except Exception as e:
                 self.log_message(f"Error removing shortcut: {e}")
                 self.startup_var.set(True)

if __name__ == "__main__":
    start_minimized = "--minimized" in sys.argv
    
    # Admin Check logic for Windows
    if os.name == 'nt':
        if is_admin():
            app = App(start_minimized=start_minimized)
            app.mainloop()
        else:
            # Re-run the program with admin rights
            # Preserving args is important
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                sys.exit(0)
            except Exception as e:
                print(f"Failed to elevate privileges: {e}")
                input("Press Enter to exit...")
    else:
        app = App(start_minimized=start_minimized)
        app.mainloop()
