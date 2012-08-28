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
from bang.xdg.applications import DesktopEntry
import bang.xdg.applications as applications
import bang.xdg.constants as constants
import bang.xdg.core as core
import os.path as p
import os




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
        self.size = len(stack)
        self.end = self.size - 1
        for index in range(self.size):
            con, arg = stack[index]
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
            elif arg == '__exit__':
                if self.node.parent != None:
                    self.node = self.node.parent
                else: #parent == None
                    if index != self.end:
                        self.node = self.node.attach_parent(Or())
        if self.node != None:
            while self.node.parent != None:
                self.node = self.node.parent
        #print(self.stack, self.node, self.node.conditions, [c.conditions for c in self.node.children])
            
    def eval(self, app):
        return self.node.eval(app) if self.node != None else False

class Node(object):
    def __init__(self, parent = None):
        self.parent = parent
        self.conditions = [ ]
        self.children = [ ]
        if self.parent != None: self.parent.children.append(self)

    def attach_parent(self, node):
        self.parent = node
        self.parent.children.append(self)
        return node

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
    for app in applications.apps:
        print(app, app.categories, _cond.eval(app))
        print(Separator())

class SubMenu(object):
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
        if self.entries == [ ]: self.entries = self.submenus
        for app in applications.apps.values():
            if self._included(app) and not self._excluded(app):
                if self.layout == None:
                    self.entries.append(app)
                elif app not in self.layout.entries:
                    self.entries.append(app)
        for sub in self.entries:
            if isinstance(sub, SubMenu): sub.load_applications()

    def _included(self, app):
        if self.includes != None:
            return self.includes.eval(app)
        else:
            return False

    def _excluded(self, app):
        if self.excludes != None:
            return self.excludes.eval(app)
        else:
            return False

    def apply_layout(self):
        if self.layout != None:
            if self.entries == [ ]: self.entries = self.submenus
            self.entries = self.layout.arrange(self)
        else:
            if self.entries == [ ]: self.entries = self.submenus

    def clean(self):
        self.map = [m.name for m in self.entries if isinstance(m, SubMenu) and m.entries == []]
        self.entries = [m for m in self.entries if m.name not in self.map]
        for entry in self.entries:
            if isinstance(entry, SubMenu): entry.clean()

    def __str__(self):
        return self.name

    def __iter__(self):
        for item in self.entries:
            yield item

class Menu(SubMenu):
    def __init__(self, path = None, load = True):
        SubMenu.__init__(self)
        self.app_directories = [ ]
        self.dir_directories = [ ]
        self.merge_directories = [ ]
        self.layout = None
        self.renamer = None
        self.file_info = None
        self.xml = core.XmlFile(path)
        if path != None: self.parse(load = load)

    def parse(self, path = None, load = True):
        if path != None: self.xml.parse(path)
        self.file_info = self.xml.info 
        if not self.xml.has_file: 
            raise Exception('No file is present')
        else:
            self._process_dirs('AppDir', self.app_directories)
            self._process_dirs('DirectoryDir', self.dir_directories)
            self._process_dirs('LegacyDir', self.app_directories)
            if 'DefaultAppDirs' in self.xml:
                self.app_directories = self.app_directories + constants.XDG_APPICATION_DIRECTORIES
            if 'DefaultDirectoryDirs' in self.xml:
                self.dir_directories = self.dir_directories + constants.XDG_DIRECTORY_DIRECTORIES
            if 'DefaultMergeDirs' in self.xml:
                self.merge_directories = self.merge_directories + constants.XDG_MENU_DIRECTORIES
            self._handle_menu_elements(self, self.xml, False)
            self._stack = self.xml.get_children_by_name('Menu')
            for element in self._stack:
                self._submenu = SubMenu(parent = self)
                self._handle_menu_elements(self._submenu, self.xml.node_iter(element))
                self._submenu.apply_layout()
                self.submenus.append(self._submenu)
            for directory in self.merge_directories:
                if 'applications-merged' in directory:
                    for f in os.listdir(directory):
                        f = p.join(directory, f)
                        self._merged = Menu(f, load = False)
                        self.submenus.extend(self._merged.submenus)
            if load == True:
                self.apply_layout()
                self.load_applications()
                self.clean()

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
                    self.d = p.join(directory, self.temp)
                    if p.isfile(self.d):
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
                self.s = p.split(self.p)
                self.d = self.s[0]
                self.f = self.s[1]
                self.m = Menu()
                if self.attrib == 'path' or self.attrib == ' ':
                    if not p.isfile(self.p):
                        self.p = p.join(menu.file_info.path_name, self.f)    
                elif self.attrib == 'parent':
                    for d in self.merge_directories:
                        if d != menu.file_info.path_name and p.isfile(p.join(d, self.f)):
                            self.p = p.join(d, self.f)
                if p.isfile(self.p):
                    self.m.parse(self.p, False)
                    menu.submenus = menu.submenus + self.m.submenus
            elif self.tag == 'MergeDir':
                self.d = self.xml.get_text(element)
                if not p.isdir(self.d):
                    if p.isdir(p.join(menu.path, self.d)):
                        self.d = p.join(menu.path, self.d)
                    else:
                        continue
                for f in os.listdir(self.d):
                    self.sub = Menu()
                    self.sub.parse(p.join(self.d, f))
                    menu.submenus = menu.submenus + self.sub.submenus
            elif self.tag == 'Move':
                self.renamer = core.Renamer()
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
                        try:
                            self.d = applications.apps[self.e]
                            menu.layout.append(self.d)
                        except:
                            print('failure', self.e)
                            continue
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
                    menu.submenus.append(self.menu)
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
                self.ents = self.conditions.count((con, '__enter__'))
                self.exts = self.conditions.count((con, '__exit__'))
                if self.ents != self.exts:
                    self.conditions[(j-1) - i] = (con, '__exit__')
        return Evaluator(self.conditions)

    def as_submenu(self, name = ' ', parent = None):
        self.temp = SubMenu(name, parent)
        self.temp.name = self.name
        self.temp.layout = self.layout
        self.temp.directory = self.directory
        self.temp.includes = self.includes
        self.temp.excludes = self.excludes
        self.temp.submenus = self.submenus
        self.temp.entries = self.entries
        self.temp.only_unallocated = self.only_unallocated
        self.temp.deleted = self.deleted
        return self.temp


class Layout(object):
    def __init__(self):
        self.entries = [ ]

    def append(self, entry):
        self.entries.append(entry)

    def arrange(self, menu):
        self.temp_menu = [ ]
        self.blacklist = Blacklist([e for e in self.entries if e.name != 'Separator' and e.name != 'Merge'])
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
                    for e in menu.submenus:
                        if isinstance(e, SubMenu):
                            if e not in self.blacklist:
                                self.temp_menu.append(e)
                elif entry.type == 'files':
                    for e in menu.submenus:
                        if isinstance(e, DesktopEntry):
                            if e.ini.has_file and e not in self.blacklist:
                                self.temp_menu.append(e)
                elif entry.type == 'all':
                    for e in menu.submenus:
                        if not isinstance(e, Separator):
                            if e not in self.blacklist:
                                self.temp_menu.append(e)
                        elif isinstance(e, Separator):
                            self.temp_menu.append(e)
        return self.temp_menu

    def __iter__(self):
        for item in self.entries:
            yield item

    def __str__(self):
        return [e.__str__() for e in self.entries].__str__()

class Merge(object):
    def __init__(self, _type = ' '):
        self.name = 'Merge'
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

class Blacklist(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        for d in self.data:
            yield d

    def __contains__(self, value):
        if isinstance(value, DesktopEntry):
            for d in self.data:
                if value.name == d.name and value.file_info.name == d.file_info.name:
                    return True
            else:
                return False
        if isinstance(value, SubMenu):
            for d in self.data:
                if value.name == d.name:
                    return True
            else:
                return False
        else:
            raise Exception('Unknown Type: {}'.format(value.__repr__()))

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