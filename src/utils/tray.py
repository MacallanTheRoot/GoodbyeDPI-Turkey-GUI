import pystray
from PIL import Image, ImageDraw

from utils.icon_generator import create_icon

class SystemTrayIcon:
    def __init__(self, app, show_callback, quit_callback):
        self.app = app
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.icon = None

    def run(self):
        image = create_icon()
        menu = (
             pystray.MenuItem('Show', self.on_show),
             pystray.MenuItem('Quit', self.on_quit)
        )
        self.icon = pystray.Icon("name", image, "GoodbyeDPI-Turkey GUI", menu)
        self.icon.run()

    def on_show(self, icon, item):
        self.show_callback()

    def on_quit(self, icon, item):
        self.icon.stop()
        self.quit_callback()
    
    def stop(self):
        if self.icon:
            self.icon.stop()
