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
from bang.xdg.constants import XDG_ICON_DIRECTORIES, STD_ICON_EXTENSIONS
from bang.xdg.core import IniFile, Renamer
from os.path import join, isfile, isdir, listdir
from re import sub, match, search


renamer = Renamer({'GNOME':'gnome', 'Hicolor':'hicolor'})

class IconDirectory(object):
    def __init__(self, section):
        self.section = section
        self.size = section.get_item('Size')
        self.context = section.get_item('Context')
        self.type = section.get_item('Type')
        self.min_size = section.get_item('MinSize')
        self.max_size = section.get_item('MaxSize')

class IconTheme(object):
    def __init__(self, path = None):
        self.ini = IniFile(path)
        self.parse()

    def parse(self, path = None):
        if path != None: self.ini.parse(path)
        self.section = self.ini.get_section('Icon Theme')
        if self.section == None:
            raise Exception('Invalid Icon Theme File')
        self.directories = self.section.get_item('Directories')
        if self.directories == None:
            self.directories = []
            for section in self.ini:
                self.name = section.name
                if self.name != 'IconTheme':
                    self.directories.append(self.name)
        else:
            self.directories = self.directories.split(',;')
        self.name = self.section.get_item('Name')
        if self.name == None: 
            self.comment = ''
        self.comment = self.section.get_item('Comment')
        if self.comment == None: 
            self.comment = ''
        self.inherits = self.section.get_item('Inherits')
        if self.inherits == None: 
            self.inherits = []
        else:
            self.inherits = self.inherits.split(',;')
        self.example = self.section.get_item('Example')
        if self.example == None: 
            self.example = ' '

    def get_name(self):
        return self.name

    def get_directories(self):
        return self.directories #string list!!!!!

    def get_directory_iter(self):
        for section in self.ini:
            if section.name != 'IconTheme':
                yield IconDirectory(section)

    def get_directory(self, directory):
        return IconDirectory(self.ini.get_section(directory))

    def get_directory_group(self, size = 0, min_size = 0):
        def rectify(num):
            if int(num) > 256 or num == 'scalable': 
                return 'scalable'
            else:
                return str(num)
        if size != 0 and min_size != 0:
            raise Exception('You may only set \'size\' OR \'min_size\'')
        elif size != 0:
            size = rectify(size)
            self.temp = []
            for directory in self.directories:
                if search(size, directory) == True:
                    self.temp.append(directory)
            return self.temp
        elif min_size != 0:
            min_size = rectify(min_size)
            for i in range(len(self.directories)):
                if search(size, self.directories[i]) == True:
                    return self.directories[self.i:]
        else:
            return self.directories

    def get_comment(self):
        return self.comments

    def get_inherits(self):
        return self.inherits #string list!!!!!

    def get_inherits_iter(self):
        for inherit in self.inherits:
            yield get_icon_theme_for_name(inherit)

    def get_example(self):
        return self.example

    def get_icon_for_name(self, name, size):
        self.resolver = IconResolver(self)
        self.resolved = self.resolver.resolve(name, size)
        if self.resolved == None:
            self.resolved = self.resolver.hungry_resolve(name, size)
        if self.resolved != None:
            return self.resolved
        else:
            raise Exception('''
            \"{icon}\" cannot be found, because:
            1.) Icon does not exist, or...
            2.) The theme does not inherit a theme that has it.
            '''.format(icon=name))

def get_icon_theme_for_name(name):
    name = renamer.replace(name)
    for directory in XDG_ICON_DIRECTORIES:
        if directory  == '/usr/share/pixmaps/':
            continue
        else:
            fqdir = join(directory, name)
            if isdir(fqdir):
                return IconTheme(join(fqdir, 'index.theme'))

class IconResolver(object):
    def __init__(self, theme, exts = STD_ICON_EXTENSIONS):
        self.exts = exts
        self.theme = theme
        
    def resolve(self, name, size):
        if isfile(name):
            return name
        elif search('^.*\.(png|xpm|svg)', name):
            self.name = name.strip('/').split('.') # just incase it's '/openbox.png'
            self.exts = [].append(self.name[1])
            self.name = self.name[0]
        else:
            self.name = name
        for xdg_dir in XDG_ICON_DIRECTORIES:
            if xdg_dir == '/usr/share/pixmaps/':
                self.ret = self.search_in_pixmaps(self.name, size, self.exts)
                if self.ret == None:
                    continue
                else:
                    return self.ret
            else:
                self.ret = self.search_in_theme(self.theme, self.name, xdg_dir, size, self.exts)
                if self.ret == None:
                    for theme in self.theme.get_inherits_iter():
                        self.ret = self.search_in_theme(theme, self.name, xdg_dir, size, self.exts)
                        if self.ret == None:
                            continue
                        else:
                            return self.ret
                else:
                    return self.ret
        return None

    def search_in_pixmaps(self, name, size, exts = STD_ICON_EXTENSIONS):
        for ext in exts:
            self.item = '/usr/share/pixmaps/{0}.{1}'.format(self.name, ext)
            if isfile(self.item):
                return self.item
        else:
            return None
    
    def search_in_theme(self, theme, name, xdg_dir, size, exts = STD_ICON_EXTENSIONS):
        self.dirs = theme.get_directory_group(size = size)
        for subdir in self.dirs:
            self.item = join(xdg_dir, theme.name, subdir)
            self.item = renamer.replace(self.item)
            self.item = self.search_in_directory(self.item, exts)
            if self.item != None:
                return self.item
        else:
            return None

    def hungry_resolve(self, theme, name, size, exts = STD_ICON_EXTENSIONS):
        for directory in XDG_ICON_DIRECTORIES:
            if directory == '/usr/share/pixmaps/':
                for ext in exts:
                    self.item = '{0}{1}.{2}'.format(directory, name, ext)
                    if isfile(self.item):
                        return self.item
            else:
                def check(i_theme):
                    for subdir in icon_theme.get_directory_group(min_size = size):
                        self.item = join(directory, i_theme.name ,subdir)
                        self.item = renamer.replace(self.item)
                        self.item = self.search_in_directory(self.item, exts)
                        if self.item != None:
                            return self.item
                    else:
                        return None
                self.val = check(theme)
                if self.val == None:
                    for member in theme.get_inherits_iter():
                        val = check(member)
                        if val != None:
                            return val
                else:
                    return val
        return None

        def search_in_directory(self, directory, name, exts):
            if isdir(directory) == False:
                return None
            else:
                for i in listdir(directory):
                    for ext in exts:
                        if i != '{0}.{1}'.format(name, ext):
                            continue
                        else:
                            return join(directory, i)

def test():
    pass
