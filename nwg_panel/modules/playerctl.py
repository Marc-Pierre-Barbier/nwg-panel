#!/usr/bin/env python3

from gi.repository import GLib

import subprocess
import threading

from nwg_panel.tools import check_key, update_image, player_status, player_metadata
from nwg_panel.common import icons_path

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk, Gdk, GdkPixbuf


class Playerctl(Gtk.EventBox):
    def __init__(self, settings):
        self.settings = settings
        Gtk.EventBox.__init__(self)
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.box.set_property("name", "task-box")
        self.add(self.box)
        self.image = Gtk.Image.new_from_icon_name("wtf", Gtk.IconSize.MENU)
        self.label = Gtk.Label("")
        self.icon_path = None
        self.play_pause_btn = Gtk.Button()
        self.status = ""

        check_key(settings, "interval", 0)
        check_key(settings, "css-name", "")
        check_key(settings, "icon-size", 16)
        check_key(settings, "buttons", True)
        check_key(settings, "buttons-position", "left")
        check_key(settings, "chars", 30)

        if settings["css-name"]:
            self.label.set_property("name", settings["css-name"])
        else:
            self.label.set_property("name", "executor-label")

        self.build_box()

        self.refresh()

        if settings["interval"] > 0:
            Gdk.threads_add_timeout_seconds(GLib.PRIORITY_LOW, settings["interval"], self.refresh)

    def update_widget(self, status, metadata):
        if status in ["Playing", "Paused"]:
            if not self.get_visible():
                self.show()
            
            if not self.status == status:
                if status == "Playing":
                    update_image(self.play_pause_btn.get_image(), "media-playback-pause-symbolic", self.settings["icon-size"])
                elif status == "Paused":
                    update_image(self.play_pause_btn.get_image(), "media-playback-start-symbolic", self.settings["icon-size"])
                    metadata = "{} - paused".format(metadata)
        
            self.label.set_text(metadata)
        else:
            if self.get_visible():
                self.hide()

        return False

    def get_output(self):
        status, metadata = "", ""
        try:
            status = player_status()
            if status in ["Playing", "Paused"]:
                metadata = player_metadata()[:self.settings["chars"]]
            GLib.idle_add(self.update_widget, status, metadata)
        except Exception as e:
            print(e)

    def refresh(self):
        thread = threading.Thread(target=self.get_output)
        thread.daemon = True
        thread.start()
        return True

    def build_box(self):
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        img = Gtk.Image()
        update_image(img, "media-skip-backward-symbolic", self.settings["icon-size"])
        btn = Gtk.Button()
        btn.set_image(img)
        btn.connect("clicked", self.launch, "playerctl previous")
        button_box.pack_start(btn, False, False, 1)

        img = Gtk.Image()
        update_image(img, "media-playback-start-symbolic", self.settings["icon-size"])
        self.play_pause_btn.set_image(img)
        self.play_pause_btn.connect("clicked", self.launch, "playerctl play-pause")
        button_box.pack_start(self.play_pause_btn, False, False, 1)

        img = Gtk.Image()
        update_image(img, "media-skip-forward-symbolic", self.settings["icon-size"])
        btn = Gtk.Button()
        btn.set_image(img)
        btn.connect("clicked", self.launch, "playerctl next")
        button_box.pack_start(btn, False, False, 1)

        if self.settings["buttons-position"] == "left":
            self.box.pack_start(button_box, False, False, 2)
            self.box.pack_start(self.label, False, False, 10)
        else:
            self.box.pack_start(self.label, False, False, 2)
            self.box.pack_start(button_box, False, False, 10)
        
        self.show_all()

    def launch(self, button, cmd):
        print("Executing '{}'".format(cmd))
        subprocess.Popen('exec {}'.format(cmd), shell=True)