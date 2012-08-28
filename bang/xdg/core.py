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
import xml.dom.minidom as xdom
import collections as c
import os.path as p
import re



def lrange(lst):
    return range(len(lst))

class FileDescriptor(object):
    def __init__(self, path):
        if p.isfile(path):
            self.path = path
            self._p = p.split(path)
            self.name = self._p[1]
            self.directory = self._p[0]
            self._n = self.name.split('.')
            try: 
                self.ext = self._n[1] 
            except: 
                self.ext = None 
        else:
            raise Exception('The path is a directory or an invalid file')
        del self._p
        del self._n

class Renamer(object):
    def __init__(self, data = {'old':'new'}):
        self.data = data

    def append(self, old, new):
        self.data[old] = new

    def remove(self, old):
        del self.data[old]

    def rename(self, name):
        if name in data:
            return data[name]

    def replace(self, string):
        for s in self.data:
            if s in string:
                string.replace(s, self.data[s])

class Searchable(c.Iterable, c.Container):
    def __init__(self):
        pass

class Section(Searchable):
    def __init__(self, name):
        self.name = name
        self.values = {}

    def get_value(self, key):
        try:
            return self.values[key]
        except:
            return ' '

    def get_as(self, key, T):
        self.str = self.get_value(key)
        if self.str != ' ':
            if T != list:
                return T(self.str)
            else:
                if ',' in self.str:
                    return self.str.split(',')
                if '|' in self.str:
                    return self.str.split('|')
                if ';' in self.str:
                    return self.str.split(';')
                else:
                    return [self.str]
        else:
            if T == str:
                return ' '
            elif T == int:
                return 0
            elif T == float:
                return 0.0
            elif T == bool:
                return False
            elif T == list:
                return []

    def __str__(self):
        return '{name}\n{values}'.format(name = self.name, values = self.values)

    def __iter__(self):
        for key in self.values:
            yield key

    def __contains__(self, value):
        for key in self.values:
            if key == value:
                return True
        else:
            return False        

class IniFile(Searchable):
    KEY_VALUE_PATTERN = r'.+\=.+'
    HEADER_PATTERN = r'\[.+\]'
    def __init__(self, path = None):
        self.text = ''
        self.document = []
        if path != None:
            self.parse(path)
        else:
            self.info = None
            self.has_file = False
            pass #you choose wether you want to parse right away or not

    def parse(self, path):
        with open(path, 'rt') as f:
            self.text = re.sub(r'#.*\n', '', f.read())
            self.info = FileDescriptor(path)
            self.has_file = True
        self.section = None
        self.lines = [t for t in self.text.split('\n') if t != '']
        for line in self.lines:
            if re.match(IniFile.HEADER_PATTERN, line):
                self.temp = line.strip('[]')
                self.section = Section(self.temp)
            elif re.match(IniFile.KEY_VALUE_PATTERN, line):
                self.temp = line.split('=')
                self.key = self.temp[0]
                self.value = self.temp[1]
                self.section.values[self.key] = self.value
            else:
                pass
            self.document.append(self.section)
        self.document = list(set(self.document))

    def get_section(self, name):
        for section in self.document:
            if section == None:
                raise Exception('Unknown Error with {f}{t}'.format(f = self.info.path, t = self.text))
            else:    
                if section.name == name:
                    return section
        else:
            return None

    def __iter__(self):
        for section in self.document:
            yield section

    def __contains__(self, value):
        for section in self.document:
            if section.name == value:
                return True

class XmlFile(Searchable):
    def __init__(self, path = None):
        if path != None: 
            self.parse(path)
        else:
            self.has_file = False

    def parse(self, path):
        with open(path) as f:
            self.dom = xdom.parse(f)
            self.data = self.dom.documentElement
            self.info = FileDescriptor(path)
            self.has_file = True

    def is_text(self, element):
        return bool(element.nodeType == element.TEXT_NODE)

    def is_empty(self, element):
        return bool(element.nodeType == element.TEXT_NODE and element.data.isspace())

    def is_comment(self, element):
        return bool(element.nodeType == element.COMMENT_NODE)

    def get_all_by_name(self, name):
        self.temp = self.data.getElementsByTagName(name)
        if self.temp == [ ]:
            return None
        else:
            return self.temp

    def get_children_by_name(self, name):
        return \
        [child for child in self.node_iter(self.data) \
            if not self.is_empty(child) and child.tagName == name]

    def get_children(self, element):
        return \
        [child for child in self.node_iter(element) \
            if not self.is_text(child)]

    def has_text(self, element):
        for child in element.childNodes:
            if self.is_text(child):
                if not self.is_empty(child):
                    return True
                else:
                    continue
            else:
                continue
        else:
            return False

    def element_has(self, element, tag):
        for child in element.childNodes:
            if child.tagName == tag:
                return True
            else:
                continue
        else:
            return False

    def has_children(self, element):
        if element.hasChildNodes():
            self._test = [c for c in element.childNodes\
             if not self.is_text(c)\
              and not self.is_empty(c)]
            if len(self._test) < 1:
                return False
            else:
                return True
        else:
            return False

    def get_text(self, element):
        for child in element.childNodes:
            if self.is_text(child):
                if not self.is_empty(child):
                    return child.data
            else:
                continue
        else:
            return ' '

    def node_iter(self, element):
        for child in element.childNodes:
            if self.is_empty(child) or self.is_comment(child):
                continue
            else:
                yield child

    def get_as(self, node, attr, type, default = None):
        if node.hasAttribute(attr):
            return T(node.getAttribute(attr))
        else:
            elif T == int:
                return 0 if default != None else default
            elif T == str:
                return ' ' if default != None else default
            elif T == bool:
                return False if default != None else default
            else:
                return None

    def __iter__(self):
        return self.node_iter(self.data)

    def __contains__(self, tag_name):
        self.check = self.data.getElementsByTagName(tag_name)
        if self.check != [ ]:
            return True
        else:
            return False

#Preliminary support not to be used yet
class Locale(object):
    def __init__(self, lang, ext):
        self.lang = lang
        self.ext = ext

class Locales(object):
    EN_US = Locale('en_US', 'en')



def test():
    ini = IniFile('/usr/share/icons/Humanity/index.theme')
    for section in ini:
        print(section)
    ini.parse('/usr/share/icons/gnome/index.theme') #WARNING: this overwrites the previous file.
    for section in ini:
        print(section)
    xml = XmlFile('/etc/xdg/menus/applications.menu')
    for elem in xml:
        if elem.tagName == 'Name':
            print(xml.get_text(elem))

