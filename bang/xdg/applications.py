from core import IniFile
from constants import XDG_APPICATION_DIRECTORIES
from os.path import join
from os import listdir
from re import match

class DesktopEntry(object):
    def __init__(self, path = None):
        self.ini = IniFile(path)
        if self.ini.has_file: self.parse()

    def parse(self, path = None):
        if path != None: self.ini.parse(path)
        if not self.ini.has_file: 
            raise Exception('No file is present')
        else:
            self.section = self.ini.get_section('Desktop Entry')
            self.name = self.section.get_value('Name')
            self.generic_name = self.section.get_value('Generic Name')
            self.encoding = self.section.get_value('Encoding')
            self.type = self.section.get_value('Type')
            self.app_exec = self.section.get_value('Exec')
            self.try_exec = self.section.get_value('TryExec')
            self.icon = self.section.get_value('Icon')
            self.no_display = self.section.get_as('NoDisplay', bool)
            self.comment = self.section.get_value('Comment')
            self.hidden = self.section.get_as('Hidden', bool)
            self.terminal = self.section.get_as('Terminal', bool)
            self.only_show_in = self.section.get_as('OnlyShowIn', list)
            self.not_show_in = self.section.get_as('NotShowIn', list)
            self.mime_type = self.section.get_as('MimeType', list)
            self.categories = self.section.get_as('Categories', list)
            self.startup_notify = self.section.get_as('StartupNotify', bool)
            self.startup_wm_class = self.section.get_value('StartupWMClass')
            self.url = self.section.get_value('URL')

    def get_value(self, key):
        return self.section.get_value(key)

    def get_as(self, key, T):
        return self.section.get_as(key, T)

def get_desktop_file_for_name(name):
    if not match(r'\w+\.desktop', name):
        name = '{n}.desktop'.format(n = name)
    for ad in XDG_APPICATION_DIRECTORIES:
        for f in listdir(ad):
            if f == name:
                return join(ad, f)

def get_desktop_entry_for_name(name):
    path = get_desktop_file_for_name(name)
    return DesktopEntry(path)

class AppCollection(object):
    def __init__(self):
        self.database = {}
        for ad in XDG_APPICATION_DIRECTORIES:
            for f in listdir(ad):
                if match(r'\w+\.desktop', name):
                    self.entry = DesktopEntry(join(ad, f))
                    self.database[self.name] = entry

    def get_apps_by_category(self, category):
        self.collector = [ ]
        for entry in self.database:
            if category in entry.categories:
                self.collector.append(entry)
        return self.collector if self.collector == [ ] else None

    def get_app_by_name(self, name):
        return self.database[name]