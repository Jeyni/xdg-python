#!python3
'''
Copyright (c) 2012, Christopher L. Ramsey <christopherlramsey@gmx.us>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met: Redistributions of
source code must retain the above copyright notice, this list of conditions and
the following disclaimer. Redistributions in binary form must reproduce the
above copyright notice, this list of conditions and the following disclaimer in
the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import bang.xdg.constants as constants
import bang.xdg.core as core
import subprocess
import os.path
import os
import re

# THIS IS SET ABOVE THE 'test' METHOD AT THE END OF THE FILE !!!!!
# IT IS A GLOBAL DICTIONARY OF EVERY APPLICATION '.desktop' FILE IN YOUR SYSTEM.
apps = {}


class DesktopEntry(object):
    def __init__(self, path = None):
        self.ini = core.IniFile(path)
        self.file_info = None
        if self.ini.has_file: self.parse()

    def parse(self, path = None):
        if path != None: self.ini.parse(path)
        self.file_info = self.ini.info
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

    def execute(self, params = [ ]):
        try:
            self.cmd = strip(self.app_exec) #'strip' defined below the class
            self.cmd = self.cmd + ' ' + ' '.join(params)
            self.cmd = self.cmd.strip()
            self.pid = subprocess.Popen(self.cmd)
            return None
        except:
            try:
                self.cmd = strip(self.try_exec) #'strip' defined below the class
                self.cmd = self.cmd + ' ' + ' '.join(params)
                self.cmd = self.cmd.strip()
                self.pid = subprocess.Popen(self.cmd)
                return None
            except:
                return (self.pid, self.name, self.file_info.name, self.cmd)

    def __str__(self):
        return '{} {}'.format(self.name, self.file_info.name)

def strip(args):
    args = args.split()
    for i in range(len(args)):
        if match('%[Uu]', args[i]):
            args.remove(args[i])
    return args

def get_desktop_file_for_name(name):
    if not re.match(r'.+\.desktop$', name):
        name = '{n}.desktop'.format(n = name)
    return apps[name]

def get_desktop_entry_for_name(name):
    path = get_desktop_file_for_name(name)
    return DesktopEntry(path)

def get_apps_by_category(category):
    return [e for e in apps if category in entry.categories]

#THIS CREATES THE GLOBAL APP LIST !!!!!!!!!
for ad in constants.XDG_APPICATION_DIRECTORIES:
    for f in os.listdir(ad):
        if re.match(r'.+\.desktop$', f):
            apps[f] = DesktopEntry(os.path.join(ad, f))

def test():
    pass