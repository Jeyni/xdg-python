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
from bang.xdg.applications import DesktopEntry, get_desktop_entry_for_name
from bang.xdg.constants import XDG_MENU_DIRECTORIES, XDG_DIRECTORY_DIRECTORIES, XDG_APPICATION_DIRECTORIES
from bang.xdg.core import XmlFile, IniFile, Renamer
from collections import Iterable
from os.path import join, isfile, isdir, dirname, split
from os import listdir
from re import match


class Evaluator(object):
    INCLUDE = 'include'
    EXCLUDE = 'exclude'
    def __init__(self, type, cond = [ ]):
        self.conditions = con

    def match(self, match):
        pass

    def __and__(self):
        pass

    def __or__(self):
        pass

    def __not__(self):
        pass

class Separator(object):
    def __init__(self):
        self.name = 'Separator'
        self.path = None

    def __str__(self):
        return self.name

class SubMenu(Iterable):
    def __init__(self, name = ' ', parent = None):
        self.parent = parent
        self.name = ' '
        self.layout = None
        self.directory = None
        self.includes = [ ]
        self.excludes = [ ]
        self.catagories = [ ]
        self.submenus = [ ]
        self.only_unallocated = False
        self.deleted = False

    def load_applications(self):
        pass

    def __str__(self):
        return self.name

    def __iter__(self):
        for item in self.submenus:
            yield item

class Menu(SubMenu):
    def __init__(self, path = None):
        SubMenu.__init__(self)
        self.app_directories = [ ]
        self.dir_directories = [ ]
        self.merge_directories = [ ]
        self.layout = None
        self.renamer = None
        self.file_info = None
        self.xml = XmlFile(path)
        if path != None: self.parse()

    def parse(self, path = None):
        if path != None: self.xml.parse(path)
        self.file_info = self.xml.info 
        if not self.xml.has_file: 
            raise Exception('No file is present')
        else:
            def process_dirs(name, layout):
                self.dirs = self.xml.get_all_by_name(name)
                if self.dirs != None:
                    for d in self.dirs:
                        layout.append(self.xml.get_text(d))
            process_dirs('AppDir', self.app_directories)
            process_dirs('DirectoryDir', self.dir_directories)
            process_dirs('LegacyDir', self.app_directories)
            if 'DefaultAppDirs' in self.xml:
                self.app_directories = self.app_directories + XDG_APPICATION_DIRECTORIES
            if 'DefaultDirectoryDirs' in self.xml:
                self.dir_directories = self.dir_directories + XDG_DIRECTORY_DIRECTORIES
            if 'DefaultMergeDirs' in self.xml:
                self.merge_directories = self.merge_directories + XDG_MENU_DIRECTORIES
            def handle_menu_element(menu, element_iter):
                for element in element_iter:
                    self.tag = element.tagName
                    if self.tag == 'Name':
                        menu.name = self.xml.get_text(element)
                    elif self.tag == 'Directory':
                        self.temp = self.xml.get_text(element)
                        for directory in self.dir_directories:
                            self.d = join(directory, self.temp)
                            if isfile(self.d):
                                menu.directory = DesktopEntry(self.d)
                            else:
                                continue
                    elif self.tag == 'OnlyUnallocated':
                        menu.only_unallocated = True
                    elif self.tag == 'NotOnlyUnallocated':
                        menu.only_unallocated = False
                    elif self.tag == 'Deleted':
                        menu.deleted = True
                    elif self.tag == 'NotDeleted':
                        menu.deleted = False
                    elif self.tag == 'Include' or self.tag == 'Exclude':
                        self.conditions = [ ]
                        def collect_conditions(elem):
                            for child in self.xml.node_iter(elem):
                                self.tag = child.tagName
                                self.has_children = child.hasChildNodes()
                                if self.xml.has_text(child):
                                    self.cond = (self.tag.lower(), self.xml.get_text(child))
                                    self.conditions.append(self.cond)
                                elif self.has_children:
                                    self.var = self.tag.lower()
                                    self.enter = (self.var, '__enter__')
                                    self.conditions.append(self.enter)
                                    collect_conditions(child)
                                    self.exit = (self.var, '__exit__')
                                    self.conditions.append(self.exit)
                        collect_conditions(element)
                        j = len(self.conditions) 
                        for i in range(j):
                            con, arg = self.conditions[i]
                            if arg == '__enter__':
                                self.entries = self.conditions.count((con, '__enter__'))
                                self.exits = self.conditions.count((con, '__exit__'))
                                if self.entries != self.exits:
                                    self.conditions[(j-1) - i] = (con, '__exit__')
                        if self.tag == 'Include':
                            menu.includes = self.conditions
                        else:
                            menu.excludes = self.conditions
                    elif self.tag == 'MergeFile':
                        self.attrib = element.getAttribute('type')
                        self.p = self.xml.get_text(element)
                        self.s = split(self.p) # os.path.split
                        self.d = self.s[0]
                        self.f = self.s[1]
                        self.temp = Menu()
                        if self.attrib == 'path' or self.attrib == ' ':
                            if not isfile(self.p):
                                self.p = join(menu.file_info.path_name, self.f)    
                        elif self.attrib == 'parent':
                            for d in self.merge_directories:
                                if d != menu.file_info.path_name and isfile(join(d, self.f)):
                                    self.p = join(d, self.f)
                        if isfile(self.p):
                            self.temp.parse(self.p)
                            self.temp = self.temp.as_submenu(menu.name, menu)
                            menu.submenus = menu.submenus + self.temp
                    elif self.tag == 'MergeDir':
                        self.d = self.xml.get_text(element)
                        if not isdir(self.d):
                            if isdir(join(menu.path, self.d)):
                                self.d = join(menu.path, self.d)
                            else:
                                continue
                        for f in listdir(self.d):
                            self.sub = Menu()
                            self.sub.parse(join(self.d, f))
                            self.sub = self.sub.as_submenu(menu.name, menu)
                            menu.submenus = menu.submenus + self.temp
                    elif self.tag == 'Move':
                        self.renamer = Renamer()
                        for child in self.xml.node_iter(element):
                            self.tag = self.child.tagName
                            self.old = None
                            self.new = None
                            if self.tag == 'Old':
                                self.old = self.xml.get_text(child)
                            elif self.tag == 'New':
                                self.new = self.xml.get_text(child)
                            if self.old != None and self.new != None:
                                self.renamer.append(self.old, self.new)
                    elif self.tag == 'Layout' or self.tag == 'DefaultLayout':
                        if self.tag == 'Layout':
                            self.layout = Layout()
                        elif self.tag == 'DefaultLayout':
                            self.layout = DefaultLayout()
                            self.layout.show_empty = self.xml.get_as(element, 'show_empty', bool)
                            self.layout.inline = self.xml.get_as(element, 'inline', bool)
                            self.layout.inline_limit = self.xml.get_as(element, 'inline_limit', int, 4)
                            self.layout.inline_header = self.xml.get_as(element, 'inline_header', bool)
                            self.layout.inline_alias = self.xml.get_as(element, 'inline_alias', bool)
                        for child in self.xml.node_iter(element):
                            self.tag = child.tagName
                            if self.tag == 'Filename':
                                self.e = self.xml.get_text(child)
                                self.d = get_desktop_entry_for_name(self.e)
                                self.layout.append(self.d)
                            elif self.tag == 'Menuname':
                                self.m_name = MenuName(self.xml.get_text(child))
                                self.m_name.show_empty = self.xml.get_as(child, 'show_empty', bool)
                                self.m_name.inline = self.xml.get_as(child, 'inline', bool)
                                self.m_name.inline_limit = self.xml.get_as(child, 'inline_limit', int, 4)
                                self.m_name.inline_header = self.xml.get_as(child, 'inline_header', bool)
                                self.m_name.inline_alias = self.xml.get_as(child, 'inline_alias', bool)
                                self.layout.append(self.m_name)
                            elif self.tag == 'Merge':
                                self.attrib = child.getAttribute('type')
                                self.layout.append(Merge(self.attrib))
                            elif self.tag == 'Separator':
                                self.layout.append(Separator())
                        else:
                            continue
                    elif self.tag == 'Menu':
                        self.menu = SubMenu(parent = menu)
                        menu.submenus.append(self.menu)
                        handle_menu_element(self.menu, self.xml.node_iter(element))
            handle_menu_element(self, self.xml)
            if self.layout != None:
                print(self.layout)

    def as_submenu(self, name = ' ', parent = None):
        self.temp = SubMenu(name, parent)
        self.temp.name = self.name
        self.temp.layout = self.layout
        self.temp.directory = self.directory
        self.temp.includes = self.includes
        self.temp.excludes = self.excludes
        self.temp.catagories = self.catagories
        self.temp.submenus = self.submenus
        self.temp.only_unallocated = self.only_unallocated
        return self.temp

class Layout(Iterable):
    def __init__(self):
        self.entries = [ ]

    def append(self, entry):
        self.entries.append(entry)

    def arrange(self, menu):
        self.temp_menu = [ ]
        for entry in self.entries:
            if isinstance(entry, DesktopEntry):
                self.temp_menu.append(entry)
            elif isinstance(entry, Separator):
                self.temp_menu.append(entry)
            elif isinstance(entry, Merge):
                if entry.type == 'files':
                    for sub in menu.submenus:
                        if isinstance(sub, DesktopEntry):
                            self.temp_menu.append(sub)
                elif entry.type == 'menu':
                    for sub in menu.submenus:
                        if isinstance(sub, SubMenu):
                            self.temp_menu.append(sub)
                elif entry.type == 'all':
                    self.temp_menu = self.temp_menu + menu.submenus
            elif isinstance(entry, MenuName):
                for sub in menu.submenus:
                    if entry.name == sub.name:
                        self.temp_menu = self.temp_menu + self.sub
                        break
        return self.temp_menu

    def __iter__(self):
        for item in self.entries:
            yield item

class Merge(object):
    def __init__(self, _type = ' '):
        self.type = _type

class MenuName(object):
    def __init__(self, name = ' '):
        self.name = name
        self.show_empty = False
        self.inline = False
        self.inline_limit = 4 
        self.inline_header= False 
        self.inline_alias = False

class DefaultLayout(MenuName, Layout):
    def __init__(self):
        MenuName.__init__(self)
        Layout.__init__(self)



def __test__():
    menu = Menu('/etc/xdg/menus/applications.menu')
    print('-------Main-------')
    print(menu.name)
    print(menu.app_directories)
    print(menu.dir_directories)
    print(menu.merge_directories)
    print(menu.includes)
    print(menu.excludes)
    print('-------Subs-------')
    for sub in menu.submenus:
        print(sub)
        print(sub.includes)
        print(sub.excludes)
        for subsub in sub.submenus:
            print('{0}->'.format(sub), subsub, subsub.submenus)
            print(subsub.includes)
            print(subsub.excludes)