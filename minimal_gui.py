#!/usr/bin/env python3
import gi
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
        self.set_keep_above(True)
        self.set_size_request(800, 40)
        self.set_position(Gtk.WindowPosition.TOP)
        
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
        
        # Settings button
        settings_button = Gtk.Button()
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.MENU)
        settings_button.set_image(settings_icon)
        settings_button.connect("clicked", self.show_settings)
        self.main_box.pack_end(settings_button, False, False, 0)
        
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
        self.bg_color = [1, 1, 1, 0.5]  # RGBA: white with 50% transparency
        
    def on_draw(self, widget, cr):
        cr.set_source_rgba(*self.bg_color)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False
        
    def update_date_time(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d %I:%M%p")
        self.date_label.set_markup(f"<span color='white' font='12'>{date_str}</span>")
        return True
        
    def update_weather(self):
        # This would normally use a weather API
        # For demo purposes, we'll just use a sunny icon
        try:
            # Replace with actual API call
            weather_condition = "sunny"
            icon_name = "weather-clear"
            
            # Set the weather icon
            self.weather_icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        except Exception as e:
            print(f"Weather update error: {e}")
        return True
        
    def create_orb_pixbuf(self, size=24):
        # Create a pulsing orb animation frame
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        cr = cairo.Context(surface)
        
        # Animation based on time
        pulse = (time.time() % 2) / 2  # 0 to 1 over 2 seconds
        radius = size/2 * (0.8 + 0.2 * pulse)
        
        # Draw orb
        cr.set_source_rgba(0.2, 0.6, 1.0, 0.8)  # Blue with transparency
        cr.arc(size/2, size/2, radius, 0, 2 * 3.14159)
        cr.fill()
        
        # Convert to pixbuf
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, size, size)
        return pixbuf
        
    def update_ai_orb(self):
        self.ai_orb.set_from_pixbuf(self.create_orb_pixbuf())
        return True
        
    def show_settings(self, button):
        dialog = SettingsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Update background color
            r = dialog.r_scale.get_value() / 100
            g = dialog.g_scale.get_value() / 100
            b = dialog.b_scale.get_value() / 100
            a = dialog.a_scale.get_value() / 100
            self.bg_color = [r, g, b, a]
            self.queue_draw()
        dialog.destroy()

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Settings", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        
        self.set_default_size(300, 200)
        
        box = self.get_content_area()
        
        # Color settings
        color_frame = Gtk.Frame(label="Background Color")
        color_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        color_frame.add(color_box)
        
        # RGB sliders
        self.r_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.r_scale.set_value(parent.bg_color[0] * 100)
        self.g_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.g_scale.set_value(parent.bg_color[1] * 100)
        self.b_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.b_scale.set_value(parent.bg_color[2] * 100)
        self.a_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.a_scale.set_value(parent.bg_color[3] * 100)
        
        color_box.pack_start(Gtk.Label("Red"), False, False, 0)
        color_box.pack_start(self.r_scale, False, False, 0)
        color_box.pack_start(Gtk.Label("Green"), False, False, 0)
        color_box.pack_start(self.g_scale, False, False, 0)
        color_box.pack_start(Gtk.Label("Blue"), False, False, 0)
        color_box.pack_start(self.b_scale, False, False, 0)
        color_box.pack_start(Gtk.Label("Transparency"), False, False, 0)
        color_box.pack_start(self.a_scale, False, False, 0)
        
        box.pack_start(color_frame, True, True, 10)
        self.show_all()

if __name__ == "__main__":
    # Import cairo here to avoid issues with gi.require_version
    import cairo
    
    win = MinimalGUI()
    win.show_all()
    Gtk.main()