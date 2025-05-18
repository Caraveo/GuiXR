#!/usr/bin/env python3
import gi
import cairo
import datetime
import requests
import threading
import time
import os
from PIL import Image, ImageDraw

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

class MinimalGUI(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Minimal GUI")
        self.set_decorated(False)
        self.set_keep_above(True)  # Keep window above others
        self.set_size_request(800, 40)
        self.set_position(Gtk.WindowPosition.NONE)

        # Position at the top of the screen
        screen = Gdk.Screen.get_default()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        self.move(geometry.width // 2 - 400, 10)  # Center horizontally, 10px from top

        # Make window transparent
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Main box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.main_box.set_margin_start(15)
        self.main_box.set_margin_end(15)
        self.main_box.set_margin_top(5)
        self.main_box.set_margin_bottom(5)
        self.add(self.main_box)

        # Date and time label
        self.date_label = Gtk.Label()
        self.date_label.set_markup("<span color='white' font='12'>Loading...</span>")
        self.main_box.pack_start(self.date_label, False, False, 0)

        # Weather icon
        self.weather_icon = Gtk.Image()
        self.main_box.pack_start(self.weather_icon, False, False, 0)

        # Spacer (expands to push AI orb to right)
        spacer = Gtk.Label()
        self.main_box.pack_start(spacer, True, True, 0)

        # AI orb
        self.ai_orb = Gtk.Image()
        self.main_box.pack_end(self.ai_orb, False, False, 0)

        # Initialize components
        self.update_date_time()
        self.update_weather()
        self.update_ai_orb()

        # Set up timers for updates
        GLib.timeout_add_seconds(1, self.update_date_time)
        GLib.timeout_add_seconds(300, self.update_weather)  # Update weather every 5 minutes
        GLib.timeout_add(100, self.update_ai_orb)  # Update AI orb animation

        # Connect signals
        self.connect("draw", self.on_draw)
        self.connect("destroy", Gtk.main_quit)

        # Background settings
        self.bg_color = [0.2, 0.2, 0.25, 0.85]  # RGBA: dark blue-gray with 85% opacity

    def on_draw(self, widget, cr):
        try:
            # Clear the surface with transparency
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.paint()
            cr.set_operator(cairo.OPERATOR_OVER)

            # Get the dimensions of the window
            width = self.get_allocated_width()
            height = self.get_allocated_height()

            # Set the background color
            cr.set_source_rgba(*self.bg_color)

            # Create moderately rounded rectangle
            radius = height / 4  # Half as rounded as before
            degrees = 3.14159 / 180.0

            # Draw the rounded rectangle
            cr.new_sub_path()
            cr.arc(width - radius, radius, radius, -90 * degrees, 0)
            cr.arc(width - radius, height - radius, radius, 0, 90 * degrees)
            cr.arc(radius, height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()

            # Add a subtle shadow
            cr.save()
            cr.set_source_rgba(0, 0, 0, 0.3)
            cr.set_line_width(1)
            cr.translate(0, 2)  # Offset for shadow
            cr.arc(width - radius, radius, radius, -90 * degrees, 0)
            cr.arc(width - radius, height - radius, radius, 0, 90 * degrees)
            cr.arc(radius, height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()
            cr.fill()
            cr.restore()

            # Fill the rounded rectangle with main color
            cr.set_source_rgba(*self.bg_color)
            cr.arc(width - radius, radius, radius, -90 * degrees, 0)
            cr.arc(width - radius, height - radius, radius, 0, 90 * degrees)
            cr.arc(radius, height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(radius, radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()
            cr.fill()
        except Exception as e:
            print(f"Error in on_draw: {e}")
        return False

    def update_date_time(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d %I:%M%p")
        self.date_label.set_markup(f"<span color='white' font='12' weight='bold'>{date_str}</span>")
        return True

    def update_weather(self):
        # This would normally use a weather API
        # For demo purposes, we'll just use a sunny icon
        try:
            # Replace with actual API call
            icon_name = "weather-clear-symbolic"  # Using symbolic icon for better visibility on dark background

            # Set the weather icon
            self.weather_icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)

            # Apply CSS to make the icon white
            style_context = self.weather_icon.get_style_context()
            style_provider = Gtk.CssProvider()
            css = b"""
            image {
                color: white;
            }
            """
            style_provider.load_from_data(css)
            style_context.add_provider(style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        except Exception as e:
            print(f"Weather update error: {e}")
        return True

    def create_orb_pixbuf(self, size=24):
        try:
            # Create a pulsing orb animation frame
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
            cr = cairo.Context(surface)

            # Animation based on time
            pulse = (time.time() % 2) / 2  # 0 to 1 over 2 seconds
            radius = size/2 * (0.8 + 0.2 * pulse)

            # Draw orb with gradient
            pattern = cairo.RadialGradient(size/2, size/2, radius * 0.5, size/2, size/2, radius)
            pattern.add_color_stop_rgba(0, 0.4, 0.8, 1.0, 1.0)  # Bright blue center
            pattern.add_color_stop_rgba(1, 0.1, 0.4, 0.8, 0.8)  # Darker blue edge

            cr.set_source(pattern)
            cr.arc(size/2, size/2, radius, 0, 2 * 3.14159)
            cr.fill()

            # Add a highlight
            cr.set_source_rgba(1, 1, 1, 0.4)
            cr.arc(size/2 - radius * 0.3, size/2 - radius * 0.3, radius * 0.2, 0, 2 * 3.14159)
            cr.fill()

            # Convert to pixbuf
            pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, size, size)
            return pixbuf
        except Exception as e:
            print(f"Error creating orb pixbuf: {e}")
            # Create a fallback pixbuf
            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, size, size)
            pixbuf.fill(0x3399FF80)  # RGBA: light blue with transparency
            return pixbuf

    def update_ai_orb(self):
        self.ai_orb.set_from_pixbuf(self.create_orb_pixbuf())
        return True



if __name__ == "__main__":
    import sys
    import platform

    # Check for macOS and XQuartz
    if platform.system() == 'Darwin':
        import subprocess
        import os

        # Check if XQuartz is installed
        xquartz_app = '/Applications/Utilities/XQuartz.app'
        if not os.path.exists(xquartz_app):
            print("Error: XQuartz is not installed. GTK applications on macOS require XQuartz.")
            print("Please install XQuartz from https://www.xquartz.org/")
            sys.exit(1)

        # Check if XQuartz is running
        try:
            result = subprocess.run(['pgrep', 'XQuartz'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Warning: XQuartz is installed but not running.")
                print("Please start XQuartz before running this application.")
                print("You can start it by running: open /Applications/Utilities/XQuartz.app")
                # Attempt to start XQuartz
                try:
                    subprocess.run(['open', xquartz_app])
                    print("Attempting to start XQuartz for you...")
                    # Give XQuartz time to start
                    import time
                    time.sleep(3)
                except Exception as e:
                    print(f"Failed to start XQuartz: {e}")
                    sys.exit(1)
        except Exception as e:
            print(f"Error checking XQuartz status: {e}")

    # Check if GTK can be initialized
    success, argv = Gtk.init_check(None)
    if not success:
        print("Error: GTK could not be initialized. Check your display settings.")
        print("If you're running this on a remote system, make sure X11 forwarding is enabled.")
        print("If you're on macOS, make sure XQuartz is installed and running.")
        sys.exit(1)

    # Set environment variables that might help with GTK on macOS
    if platform.system() == 'Darwin':
        os.environ['GDK_BACKEND'] = 'x11'

    # If initialization was successful, proceed
    try:
        win = MinimalGUI()
        win.show_all()
        Gtk.main()
    except Exception as e:
        print(f"Error running the application: {e}")
        sys.exit(1)