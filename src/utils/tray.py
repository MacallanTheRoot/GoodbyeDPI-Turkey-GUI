from utils.icon_generator import create_icon

class SystemTrayIcon:
    def __init__(self, app, show_callback, quit_callback):
        self.app = app
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.icon = None

    def run(self):
        import pystray  # Backend discovery can fail on desktops without a tray.
        if pystray.Icon.__module__ == "pystray._xorg":
            from Xlib import display
            connection = display.Display()
            try:
                screen = connection.get_default_screen()
                selection = connection.intern_atom(f"_NET_SYSTEM_TRAY_S{screen}")
                if not connection.get_selection_owner(selection):
                    raise RuntimeError("No X11 system tray manager is available")
            finally:
                connection.close()
        image = create_icon()
        menu = (
             pystray.MenuItem('Show', self.on_show, default=True),
             pystray.MenuItem('Quit', self.on_quit)
        )
        self.icon = pystray.Icon("name", image, "GoodbyeDPI-Turkey GUI", menu)
        self.icon.run()

    def on_show(self, icon, item):
        self.show_callback()

    def on_quit(self, icon, item):
        self.quit_callback()
    
    def stop(self):
        if self.icon:
            self.icon.stop()
