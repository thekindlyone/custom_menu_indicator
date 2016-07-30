#!/usr/bin/env python

import appindicator
import gtk
from os.path import exists,expanduser, abspath, dirname, realpath
import ConfigParser
import os
import subprocess
import sys
import inspect

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

os.chdir(get_script_dir())


example_config='''
# the section title is the menu item text
[example 1]
# make sure file is executable
command = /home/thekindlyone/projects/example.py
icon = ~/projects/automation_indicator/icons/ACmode.png

[example 2]
command = python /home/thekindlyone/projects/example2.py 
icon = ~/projects/automation_indicator/icons/ACpower.png

[example 3]
command = /home/thekindlyone/projects/example.py 
# icon not mandatory
'''

conf_path = expanduser('~/.custom_menu/menu.cfg')

def read_conf():
    if not exists(conf_path):
        os.mkdir(dirname(conf_path))
        with open(conf_path,'w') as cf:
            cf.write(example_config)
    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    return config

class CustomIndicator:
    def __init__(self):
        config=read_conf()
        self.indicator=appindicator.Indicator('custom_menu',abspath('icons/menu.png'), appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status( appindicator.STATUS_ACTIVE )
        self.indicator.set_menu(self.build_menu(config))

    def build_image_item(self,name,icon):
        item=gtk.ImageMenuItem(name)
        img=gtk.Image()
        pixbuf=gtk.gdk.pixbuf_new_from_file(icon)
        pixbuf = pixbuf.scale_simple(25, 25, gtk.gdk.INTERP_BILINEAR)
        img.set_from_pixbuf(pixbuf)
        item.set_image(img)
        return item

    def build_menu(self,config):
        menu = gtk.Menu()
        for section in config.sections():
            if config.has_option(section,'icon'):
                icon=expanduser(config.get(section,'icon'))
                item=self.build_image_item(section,icon)
                menu.append(item)
            else:
                item=gtk.MenuItem(section)
                menu.append(item)

            if config.has_option(section,'command'):
                command=expanduser(config.get(section,'command'))
                item.connect('activate',self.execute,command)

        
        # Configure
        icon = abspath('icons/configure.png')
        item_conf = self.build_image_item('Configure',icon)
        menu.append(item_conf)
        item_conf.connect('activate',self.configure)
        
        # Rescan
        icon= abspath('icons/refresh.png')
        item_rescan=self.build_image_item('Reload',icon)
        menu.append(item_rescan)
        item_rescan.connect('activate',self.rescan_config)

        # QUIT        
        icon=abspath('icons/quit.png')
        item_quit = self.build_image_item('Quit',icon)
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)
        ####
       
        menu.show_all()
        return menu

    def execute(self,source,command):
        subprocess.Popen([c for c in command.split(' ') if c])

    def configure(self,source):
        subprocess.Popen(['xdg-open',conf_path])
     
    def rescan_config(self,source):
        config=read_conf()
        self.indicator.set_menu(self.build_menu(config))

    def quit(self,source):
        gtk.main_quit()
    



def main():
    indicator=CustomIndicator()    
    gtk.main()

if __name__ == "__main__":
    main()