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
from bang.xdg.applications import DesktopEntry, AppCollection, get_desktop_entry_for_name
from bang.xdg.constants import XDG_MENU_DIRECTORIES, XDG_DIRECTORY_DIRECTORIES, XDG_APPICATION_DIRECTORIES
from bang.xdg.core import XmlFile, Renamer
from collections import Iterable
from os.path import join, isfile, isdir, split
from os import listdir

apps = AppCollection()

class Separator(object):
    def __init__(self):
        self.name = 'Separator'
        self.path = None

    def __str__(self):
        return '-------sep-------'

class Evaluator(object):
    def __init__(self, stack):
        self.stack = stack
        self.node = None
        for con, arg in stack:
            if arg == '__enter__':
                if con == 'and':
                    if self.node == None:
                        self.node = And()
                    else:
                        self.node = And(self.node)
                if con == 'or':
                    if self.node == None:
                        self.node = Or()
                    else:
                        self.node = Or(self.node)
                if con == 'not':
                    if self.node == None:
                        self.node = Not()
                    else:
                        self.node = Not(self.node)
            elif con == 'filename' or con == 'category':
                if self.node == None:
                    self.node = Or()
                self.node.new_condition(con, arg)
        print(self.stack, self.node)
        if self.node != None:
            while self.node.parent != None:
                self.node = self.node.parent
            
    def eval(self, app):
        return self.node.eval(app) if self.node != None else False

class Node(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.conditions = [ ]
        self.children = [ ]
        if self.parent != None: self.parent.children.append(self)

    def append_child(self, node):
        self.children.append(node)
        return node

    def eval(self, var):
        pass

    def new_condition(self, con, arg):
        self.conditions.append((con, arg))

class And(Node):
    def __init__(self, parent = None):
        super(And, self).__init__(parent)

    def eval(self, var):
        self._bools = [ ]
        if self.conditions == [ ]:
            self._bool = False
        else:
            for con, arg in self.conditions:
                if con == 'filename':
                    self._bools.append(var.file_info.name == arg)
                elif con == 'category':
                    self._bools.append(arg in var.categories)                    
            self._bool = False if False in self._bools else True
        if self.children == [ ]:
            return self._bool
        else:
            self._check = [child.eval(var) for child in self.children]
            self._children = False if False in self._check else True
            return self._bool and self._children

class Or(Node):
    def __init__(self, parent = None):
        super(Or, self).__init__(parent)

    def eval(self, var):
        self._bools = [ ]
        if self.conditions == [ ]:
            self._bool = False
        else:
            for con, arg in self.conditions:
                if con == 'filename':
                    self._bools.append(var.file_info.name == arg)
                elif con == 'category':
                    self._bools.append(arg in var.categories)                    
            self._bool = True if True in self._bools else False
        if self.children == [ ]:
            return self._bool
        else:
            self._check = [child.eval(var) for child in self.children]
            self._children = True if True in self._check else False
            return self._bool or self._children

class Not(Node):
    def __init__(self, parent = None):
        super(Not, self).__init__(parent)

    def eval(self, var):
        self._bools = [ ]
        if self.conditions == [ ]:
            self._bool = False
        else:
            for con, arg in self.conditions:
                if con == 'filename':
                    self._bools.append(var.file_info.name == arg)
                elif con == 'category':
                    self._bools.append(arg in var.categories)                   
            self._bool = True if True in self._bools else False
        if self.children == [ ]:
            return not self._bool
        else:
            self._check = [child.eval(var) for child in self.children]
            self._children = True if True in self._check else False
            return not self._bool or self._children

def cond_test():
    for app in apps:
        print(app, app.categories, _cond.eval(app))
        print(Separator())


def condition_printer(cond):
    if cond != None:
        print('con: ', cond.node.conditions)
        print('parent: ', cond.node.parent)
        print('children: ', cond.node.children)

class SubMenu(Iterable):
    def __init__(self, name = ' ', parent = None):
        self.parent = parent
        self.name = ' '
        self.layout = None
        self.directory = None
        self.includes = None
        self.excludes = None
        self.entries = [ ]
        self.submenus = [ ]
        self.only_unallocated = False
        self.deleted = False

    def load_applications(self):
        global apps
        for app in apps:
            if self._included(app) and not self._excluded(app):
                self.entries.append(app)

    def _included(self, app):
        return self._matched(app, self.includes)

    def _excluded(self, app):
        return self._matched(app, self.excludes)

    def _matched(self, app, conditions):
        if conditions != None:
            return conditions.eval(app)
        else:
            return False

    def _apply_layout(self):
        if self.layout != None:
            self.submenus = self.entries
            self.entries = self.layout.arrange(self)

    def _sort_entries(self):
        pass

    def __str__(self):
        return self.name

    def __iter__(self):
        for item in self.entries:
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
            self._process_dirs('AppDir', self.app_directories)
            self._process_dirs('DirectoryDir', self.dir_directories)
            self._process_dirs('LegacyDir', self.app_directories)
            if 'DefaultAppDirs' in self.xml:
                self.app_directories = self.app_directories + XDG_APPICATION_DIRECTORIES
            if 'DefaultDirectoryDirs' in self.xml:
                self.dir_directories = self.dir_directories + XDG_DIRECTORY_DIRECTORIES
            if 'DefaultMergeDirs' in self.xml:
                self.merge_directories = self.merge_directories + XDG_MENU_DIRECTORIES
            self._handle_menu_elements(self, self.xml, False)
            self._stack = self.xml.get_children_by_name('Menu')
            for element in self._stack:
                self._submenu = SubMenu(parent = self)
                self._handle_menu_elements(self._submenu, self.xml.node_iter(element))
                self._submenu.load_applications()
                self._submenu._apply_layout()
                self.submenus.append(self._submenu)
            self.entries = self.submenus
            self._apply_layout()

    def _process_dirs(self, name, directories):
        self.dirs = self.xml.get_all_by_name(name)
        if self.dirs != None:
            for d in self.dirs:
                directories.append(self.xml.get_text(d))

    def _handle_menu_elements(self, menu, elements, handle_submenus = True):
        for element in elements:
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
            elif self.tag == 'Include':
                self.conditions = []
                menu.includes = self._collect_conditions(element)
            elif self.tag == 'Exclude':
                self.conditions = []
                menu.excludes = self._collect_conditions(element)
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
                    menu.entries = menu.entries + self.temp
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
                    menu.entries = menu.entries + self.temp
            elif self.tag == 'Move':
                self.renamer = Renamer()
                self.old = None
                self.new = None
                for child in self.xml.node_iter(element):
                    self.tag = self.child.tagName
                    if self.tag == 'Old':
                        self.old = self.xml.get_text(child)
                    elif self.tag == 'New':
                        self.new = self.xml.get_text(child)
                    if self.old != None and self.new != None:
                        self.renamer.append(self.old, self.new)
                        self.old = None
                        self.new = None
            elif self.tag == 'Layout' or self.tag == 'DefaultLayout':
                if self.tag == 'Layout':
                    menu.layout = Layout()
                elif self.tag == 'DefaultLayout':
                    menu.layout = DefaultLayout()
                    menu.layout.show_empty = self.xml.get_as(element, 'show_empty', bool)
                    menu.layout.inline = self.xml.get_as(element, 'inline', bool)
                    menu.layout.inline_limit = self.xml.get_as(element, 'inline_limit', int, 4)
                    menu.layout.inline_header = self.xml.get_as(element, 'inline_header', bool)
                    menu.layout.inline_alias = self.xml.get_as(element, 'inline_alias', bool)
                for child in self.xml.node_iter(element):
                    self.tag = child.tagName
                    if self.tag == 'Filename':
                        self.e = self.xml.get_text(child)
                        self.d = get_desktop_entry_for_name(self.e)
                        menu.layout.append(self.d)
                    elif self.tag == 'Menuname':
                        self.m_name = MenuName(self.xml.get_text(child))
                        self.m_name.show_empty = self.xml.get_as(child, 'show_empty', bool)
                        self.m_name.inline = self.xml.get_as(child, 'inline', bool)
                        self.m_name.inline_limit = self.xml.get_as(child, 'inline_limit', int, 4)
                        self.m_name.inline_header = self.xml.get_as(child, 'inline_header', bool)
                        self.m_name.inline_alias = self.xml.get_as(child, 'inline_alias', bool)
                        menu.layout.append(self.m_name)
                    elif self.tag == 'Merge':
                        self.attrib = child.getAttribute('type')
                        menu.layout.append(Merge(self.attrib))
                    elif self.tag == 'Separator':
                        menu.layout.append(Separator())
                else:
                    continue
            elif self.tag == 'Menu':
                if handle_submenus == True:
                    self.menu = SubMenu(parent = menu)
                    menu.entries.append(self.menu)
                    self._handle_menu_elements(self.menu, self.xml.node_iter(element))

    def _collect_conditions(self, elem):
        def recurse(e):
            for child in self.xml.node_iter(e):
                self._tag = child.tagName
                self.has_children = child.hasChildNodes()
                if self.xml.has_text(child):
                    self.cond = (self._tag.lower(), self.xml.get_text(child))
                    self.conditions.append(self.cond)
                elif self.has_children:
                    self.var = self._tag.lower()
                    self.enter = (self.var, '__enter__')
                    self.conditions.append(self.enter)
                    recurse(child)
                    self.exit = (self.var, '__exit__')
                    self.conditions.append(self.exit)
        recurse(elem)
        j = len(self.conditions)
        for i in range(j):
            con, arg = self.conditions[i]
            if arg == '__enter__':
                self.entries = self.conditions.count((con, '__enter__'))
                self.exits = self.conditions.count((con, '__exit__'))
                if self.entries != self.exits:
                    self.conditions[(j-1) - i] = (con, '__exit__')
        return Evaluator(self.conditions)

    def as_submenu(self, name = ' ', parent = None):
        self.temp = SubMenu(name, parent)
        self.temp.name = self.name
        self.temp.layout = self.layout
        self.temp.directory = self.directory
        self.temp.includes = self.includes
        self.temp.excludes = self.excludes
        self.temp.catagories = self.catagories
        self.temp.entries = self.entries
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
                if entry.ini.has_file:
                    self.temp_menu.append(entry)
            elif isinstance(entry, Separator):
                self.temp_menu.append(entry)
            elif isinstance(entry, MenuName):
                for sub in menu.submenus:
                    if entry.name == sub.name:
                        self.temp_menu.append(sub)
                        break
            if isinstance(entry, Merge):
                if entry.type == 'menus':
                    for sub in menu.submenus:
                        if isinstance(sub, SubMenu):
                            self.temp_menu.append(sub)
                elif entry.type == 'files':
                    for sub in menu.submenus:
                        if isinstance(sub, DesktopEntry):
                            if sub.ini.has_file:
                                self.temp_menu.append(sub)
                elif entry.type == 'all':
                    self.temp_menu = self.temp_menu + menu.entries
        return self.temp_menu

    def __iter__(self):
        for item in self.entries:
            yield item

    def __str__(self):
        return self.entries.__str__()

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



def test():
    menu = Menu('/etc/xdg/menus/xfce-applications.menu')
    print('-------Main-------')
    print(menu.name)
    print(menu.app_directories)
    print(menu.dir_directories)
    print(menu.merge_directories)
    print(menu.includes)
    print(menu.excludes)
    print('-------Subs-------')
    for sub in menu.entries:
        if isinstance(sub, Separator):
            print(sub)
        elif isinstance(sub, DesktopEntry):
            print(sub)
        else:
            print(sub)
            print(sub.includes)
            print(sub.excludes)
            print(sub.layout)
            for subsub in sub.entries:
                if isinstance(subsub, Separator):
                    print('{0}->'.format(sub), subsub)
                elif isinstance(subsub, DesktopEntry):
                    print('{0}->'.format(sub), subsub)
                else:
                    print('{0}->'.format(sub), subsub, subsub.entries)
                    print(subsub.includes)
                    print(subsub.excludes)
    print('--------End--------')