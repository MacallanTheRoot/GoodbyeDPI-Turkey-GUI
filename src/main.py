import customtkinter as ctk
import threading
import queue
import os
import sys
import ctypes
import subprocess

from PIL import ImageTk
from utils.icon_generator import create_icon

from utils.runner import DNSRunner
from utils.tray import SystemTrayIcon
from utils import startup
from utils.theme import COLORS, FONT, SPACE, RADIUS

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

import webbrowser
from utils.config import ConfigManager

class App(ctk.CTk):
    def __init__(self, start_minimized=False):
        super().__init__()
        
        self.title("GoodbyeDPI Turkey")
        self.geometry("480x720")
        self.minsize(390, 480)
        
        # Initialize Config
        self.config_manager = ConfigManager()

        # Set Window Icon
        try:
            self.iconphoto(False, ImageTk.PhotoImage(create_icon()))
        except Exception as e:
            print(f"Failed to set icon: {e}")

        # Modern Styling config
        ctk.set_appearance_mode(self.config_manager.get("theme"))
        ctk.set_default_color_theme("blue")
        
        self.runner = DNSRunner(log_callback=self.log_message)
        self.is_running = False
        self.tray_icon = None
        self.tray_thread = None
        self._ui_events = queue.Queue()
        self._shutting_down = False

        self.create_widgets()
        self.after(50, self._process_ui_events)
        self.after(1000, self._poll_process)
        
        # Override window close event
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # Check startup logic
        self.check_startup_status()

        if start_minimized:
            self.hide_window() # Will create tray icon
            self.start_service() # Auto-start if starting minimized implies auto-run
            self.log_message("Started automatically via startup.")

    def create_widgets(self):
        self.configure(fg_color=COLORS["background"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACE["lg"], pady=(SPACE["lg"], SPACE["md"]))
        header.grid_columnconfigure(1, weight=1)
        self.header_icon = ctk.CTkImage(light_image=create_icon(128), dark_image=create_icon(128), size=(40, 40))
        ctk.CTkLabel(header, text="", image=self.header_icon, width=40).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ctk.CTkLabel(header, text="GoodbyeDPI Turkey", font=(FONT, 20, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(header, text="Network protection", font=(FONT, 12),
                     text_color=COLORS["muted"]).grid(row=1, column=1, sticky="nw")
        ctk.CTkButton(header, text="About", width=56, height=32, corner_radius=RADIUS["control"],
                      fg_color="transparent", hover_color=COLORS["surface_alt"],
                      text_color=COLORS["accent"], command=self.open_about_window).grid(row=0, column=2, rowspan=2)

        protection = self._card(content, 1)
        ctk.CTkLabel(protection, text="PROTECTION", font=(FONT, 11, "bold"),
                     text_color=COLORS["muted"]).grid(row=0, column=0, sticky="w")
        status_row = ctk.CTkFrame(protection, fg_color="transparent")
        status_row.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.status_dot = ctk.CTkLabel(status_row, text="●", width=24, font=(FONT, 19),
                                      text_color=COLORS["muted"])
        self.status_dot.pack(side="left")
        self.status_label = ctk.CTkLabel(status_row, text="Not protected", font=(FONT, 23, "bold"),
                                         text_color=COLORS["text"])
        self.status_label.pack(side="left", padx=(4, 0))
        self.status_detail = ctk.CTkLabel(protection, text="Protection is off.", font=(FONT, 12),
                                          text_color=COLORS["muted"], anchor="w", justify="left",
                                          wraplength=350)
        self.status_detail.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        self.primary_button = ctk.CTkButton(
            protection, text="ACTIVATE", height=44, corner_radius=RADIUS["control"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["accent_text"], font=(FONT, 13, "bold"),
            command=self.start_service)
        self.primary_button.grid(row=3, column=0, sticky="ew")

        dns = self._card(content, 2)
        ctk.CTkLabel(dns, text="DNS Provider", font=(FONT, 15, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.dns_options = {
            "Turkey DNSRedir": ("77.88.8.8", "1253"),
            "Yandex (Standard)": ("77.88.8.8", "1253"),
            "Google": ("8.8.8.8", "53"),
            "Cloudflare": ("1.1.1.1", "53"),
            "OpenDNS": ("208.67.222.222", "53"),
        }
        saved_dns = self.config_manager.get("dns_provider")
        if saved_dns not in self.dns_options:
            saved_dns = "Turkey DNSRedir"
        self.dns_var = ctk.StringVar(value=saved_dns)
        self.dns_menu = ctk.CTkOptionMenu(
            dns, variable=self.dns_var, values=list(self.dns_options),
            command=self.save_dns_preference, height=38,
            fg_color=COLORS["surface_alt"], button_color=COLORS["surface_alt"],
            button_hover_color=COLORS["border"], text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"], dropdown_text_color=COLORS["text"])
        self.dns_menu.grid(row=1, column=0, sticky="ew")
        if os.name != "nt":
            ctk.CTkLabel(dns, text="Linux uses a local proxy at 127.0.0.1:8080. Configure your browser to use it.",
                         font=(FONT, 11), text_color=COLORS["muted"], anchor="w",
                         justify="left", wraplength=350).grid(row=2, column=0, sticky="ew", pady=(10, 0))

        preferences = self._card(content, 3)
        ctk.CTkLabel(preferences, text="Preferences", font=(FONT, 15, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.startup_var = ctk.BooleanVar(value=False)
        self.startup_switch = ctk.CTkSwitch(
            preferences, text="Run on startup", variable=self.startup_var,
            command=self.toggle_startup, font=(FONT, 13), text_color=COLORS["text"],
            progress_color=COLORS["accent"])
        self.startup_switch.grid(row=1, column=0, sticky="w", pady=(0, 12))
        theme_row = ctk.CTkFrame(preferences, fg_color="transparent")
        theme_row.grid(row=2, column=0, sticky="ew")
        theme_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(theme_row, text="Appearance", font=(FONT, 13),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w")
        self.theme_var = ctk.StringVar(value=self.config_manager.get("theme"))
        ctk.CTkOptionMenu(theme_row, variable=self.theme_var, values=["System", "Light", "Dark"],
                          command=self.save_theme_preference, width=110,
                          fg_color=COLORS["surface_alt"], button_color=COLORS["surface_alt"],
                          button_hover_color=COLORS["border"], text_color=COLORS["text"]).grid(row=0, column=1)

        activity = self._card(content, 4)
        self.activity_button = ctk.CTkButton(activity, text="Activity  ▾", anchor="w", height=30,
                                             font=(FONT, 14, "bold"), fg_color="transparent",
                                             hover_color=COLORS["surface_alt"],
                                             text_color=COLORS["text"], command=self.toggle_activity)
        self.activity_button.grid(row=0, column=0, sticky="ew")
        self.log_textbox = ctk.CTkTextbox(activity, height=135, font=("Consolas" if os.name == "nt" else "monospace", 11),
                                          fg_color=COLORS["surface_alt"], text_color=COLORS["text"])
        self.log_textbox.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.log_textbox.grid_remove()
        self.activity_open = False

        footer = ctk.CTkLabel(content, text="GitHub  ·  MacallanTheRoot", font=(FONT, 11),
                              text_color=COLORS["muted"], cursor="hand2")
        footer.grid(row=5, column=0, pady=(8, SPACE["lg"]))
        footer.bind("<Button-1>", lambda _event: webbrowser.open("https://github.com/MacallanTheRoot/GoodbyeDPI-Turkey-GUI"))

    def _card(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=RADIUS["card"],
                            border_width=1, border_color=COLORS["border"])
        card.grid(row=row, column=0, sticky="ew", padx=SPACE["lg"], pady=(0, SPACE["md"]))
        card.grid_columnconfigure(0, weight=1)
        # Internal padding stays on children by using a nested content frame.
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=0, column=0, sticky="ew", padx=SPACE["md"], pady=SPACE["md"])
        inner.grid_columnconfigure(0, weight=1)
        return inner

    def toggle_activity(self):
        self.activity_open = not self.activity_open
        if self.activity_open:
            self.log_textbox.grid()
            self.activity_button.configure(text="Activity  ▴")
        else:
            self.log_textbox.grid_remove()
            self.activity_button.configure(text="Activity  ▾")

    def save_theme_preference(self, choice):
        ctk.set_appearance_mode(choice)
        self.config_manager.save_config("theme", choice)

    def save_dns_preference(self, choice):
        self.config_manager.save_config("dns_provider", choice)

    def open_about_window(self):
        about = ctk.CTkToplevel(self)
        about.title("About")
        about.geometry("300x250")
        about.grab_set() # Modal
        
        ctk.CTkLabel(about, text="GoodbyeDPI Turkey", font=(FONT, 16, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(about, text="v1.0.0", font=(FONT, 12), text_color=COLORS["muted"]).pack()
        
        ctk.CTkLabel(about, text="A secure & private DNS solution.\nDeveloped by MacallanTheRoot", 
                     wraplength=250, justify="center", font=(FONT, 12)).pack(pady=20)
        
        def open_github():
            webbrowser.open("https://github.com/MacallanTheRoot")
            
        link = ctk.CTkLabel(about, text="Visit GitHub", text_color=COLORS["accent"], cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: open_github())

        ctk.CTkButton(about, text="Close", command=about.destroy, width=100).pack(pady=20)

    def start_service(self):
        if self._shutting_down or self.is_running:
            return
        dns_name = self.dns_var.get()
        addr, port = self.dns_options[dns_name]
        
        self.log_message(f"Starting service with {dns_name} ({addr}:{port})...")
        try:
            self.runner.start(dns_addr=addr, dns_port=port)
            self.is_running = True
            self.update_status(True)
        except Exception as e:
            self.log_message(f"Error starting: {e}")
            self.status_detail.configure(text=str(e))

    def stop_service(self):
        if self._shutting_down:
            return
        self.log_message("Stopping service...")
        self.runner.stop()
        self.is_running = False
        self.update_status(False)
        self.log_message("Service stopped.")

    def update_status(self, running):
        if running:
            self.status_label.configure(text="Protected" if os.name == "nt" else "Proxy running")
            self.status_dot.configure(text_color=COLORS["success"])
            self.status_detail.configure(text="Protection is active." if os.name == "nt" else
                                         "Local proxy active. Use 127.0.0.1:8080 in your browser.")
            self.primary_button.configure(text="DEACTIVATE", command=self.stop_service)
            self.dns_menu.configure(state="disabled")
        else:
            self.status_label.configure(text="Not protected")
            self.status_dot.configure(text_color=COLORS["muted"])
            self.status_detail.configure(text="Protection is off.")
            self.primary_button.configure(text="ACTIVATE", command=self.start_service)
            self.dns_menu.configure(state="normal")

    def _poll_process(self):
        if self._shutting_down:
            return
        if self.is_running and self.runner.process and self.runner.process.poll() is not None:
            self.runner.stop()
            self.is_running = False
            self.update_status(False)
            self.status_detail.configure(text="The engine exited. Open Activity for details.")
        self.after(1000, self._poll_process)

    def log_message(self, message):
        self._ui_events.put(("log", message))

    def _process_ui_events(self):
        while True:
            try:
                action, value = self._ui_events.get_nowait()
            except queue.Empty:
                break
            if action == "log" and not self._shutting_down:
                self.log_textbox.insert("end", value + "\n")
                self.log_textbox.see("end")
            elif action == "show":
                self.show_window_from_tray()
            elif action == "quit":
                self.quit_app()
            elif action == "tray_failed" and not self._shutting_down:
                self.tray_icon = None
                self.show_window_from_tray()
                self.log_textbox.insert("end", f"System tray unavailable: {value}\n")
        if not self._shutting_down:
            self.after(50, self._process_ui_events)

    def hide_window(self):
        if self._shutting_down:
            return
        self.withdraw()
        if not self.tray_icon:
            self.tray_icon = SystemTrayIcon(
                self, lambda: self._ui_events.put(("show", None)),
                lambda: self._ui_events.put(("quit", None)))
            self.tray_thread = threading.Thread(target=self.run_tray, name="tray")
            self.tray_thread.daemon = True
            self.tray_thread.start()

    def run_tray(self):
        try:
            self.tray_icon.run()
        except Exception as exc:
            self._ui_events.put(("tray_failed", str(exc)))

    def show_window_from_tray(self):
        if self._shutting_down:
            return
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        self.primary_button.configure(state="disabled")
        self.dns_menu.configure(state="disabled")
        self.startup_switch.configure(state="disabled")
        try:
            self.runner.close()
            self.is_running = False
        finally:
            if self.tray_icon:
                self.tray_icon.stop()
            if self.tray_thread and self.tray_thread is not threading.current_thread():
                self.tray_thread.join(timeout=2)
            self.destroy()

    # --- User-level autostart ---
    def get_startup_path(self):
        return str(startup.startup_path())

    def check_startup_status(self):
        self.startup_var.set(startup.is_enabled())

    def toggle_startup(self):
        enabled = self.startup_var.get()
        try:
            startup.set_enabled(enabled)
            self.log_message("Autostart enabled." if enabled else "Autostart disabled.")
        except Exception as exc:
            self.startup_var.set(not enabled)
            self.log_message(f"Could not change autostart: {exc}")

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
            arguments = sys.argv[1:] if getattr(sys, "frozen", False) else [os.path.abspath(sys.argv[0]), *sys.argv[1:]]
            params = subprocess.list2cmdline(arguments)
            try:
                result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                if result <= 32:
                    raise OSError(f"Elevation was declined or failed ({result})")
                sys.exit(0)
            except Exception as e:
                print(f"Failed to elevate privileges: {e}")
    else:
        app = App(start_minimized=start_minimized)
        app.mainloop()
