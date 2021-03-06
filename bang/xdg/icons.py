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
import os.path as p
import os, re



renamer = core.Renamer({'GNOME':'gnome', 'Hicolor':'hicolor'})

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
        self.ini = core.IniFile(path)
        self.resolver = IconResolver(self)
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
            self.directories = self.directories.split(',')
        self.name = self.section.get_item('Name')
        self.comment = self.section.get_item('Comment')
        self.inherits = self.section.get_as('Inherits', list)
        self.example = self.section.get_item('Example')

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
        elif size > 0:
            size = rectify(size)
            self.temp = []
            for directory in self.directories:
                if re.search(size, directory) == True:
                    self.temp.append(directory)
            return self.temp
        elif min_size > 0:
            min_size = rectify(min_size)
            for i in range(len(self.directories)):
                if re.search(size, self.directories[i]) == True:
                    return self.directories[self.i:]
        else:
            return self.directories

    def get_comment(self):
        return self.comments

    def get_inherits(self):
        return self.inherits #string list!!!!!

    def get_inherits_iter(self):
        for inherit in [get_icon_theme_for_name(i) for i in self.inherits]:
            yield inherit

    def get_example(self):
        return self.example

    def get_icon_for_name(self, name, size):
        self.resolved = self.resolver.resolve(name, size)
        if self.resolved == None:
            self.resolved = self.resolver.hungry_resolve(name, size)
        if self.resolved != None:
            return self.resolved
        else:
            self._err =\
            "\"{icon}\" cannot be found, because:\n" +\
            "1.) Icon does not exist, or...\n" +\
            "2.) The theme does not inherit a theme that has it."
            raise Exception(self._err.format(icon=name))

def get_icon_theme_for_name(name):
    name = renamer.replace(name)
    for directory in constants.XDG_ICON_DIRECTORIES:
        if directory != '/usr/share/pixmaps/':
            fqdir = p.join(directory, name)
            if p.isdir(fqdir):
                return IconTheme(p.join(fqdir, 'index.theme'))
        else:
            continue


class IconResolver(object):
    def __init__(self, theme, exts = constants.STD_ICON_EXTENSIONS):
        self.exts = exts
        self.theme = theme
        
    def resolve(self, name, size):
        if p.isfile(name):
            return name
        elif re.search('^.*\.(png|xpm|svg)', name):
            self.name = name.strip('/').split('.') # just incase it's '/openbox.png'
            self.exts = [self.name[1]]
            self.name = self.name[0]
        else:
            self.name = name
        self.ret = self.search_in_pixmaps(self.name, self.exts)
        if self.ret != None:
            return self.ret
        else:
            self.ret = self.search_in_theme(self.theme, self.name, size, self.exts)
            if self.ret != None:
                return self.ret
            else:
                for theme in self.theme.get_inherits_iter():
                    self.ret = self.search_in_theme(theme, self.name, size, self.exts)
                    if self.ret == None:
                        continue
                    else:
                        return self.ret
        return None

    def hungry_resolve(self, name, size):
        if p.isfile(name):
            return name
        elif re.search('^.*\.(png|xpm|svg)', name):
            self.name = name.strip('/').split('.') # just incase it's '/openbox.png'
            self.exts = [self.name[1]]
            self.name = self.name[0]
        else:
            self.name = name
        self.ret = self.search_in_pixmaps(self.name, self.exts)
        if self.ret != None:
            return self.ret
        else:
            self.sizes = constants.STD_ICON_SIZES
            self.sizes = self.sizes[self.sizes.index(size) + 1:] if size != 'scalable' else ['scalable']
            for s in self.sizes:
                self.ret = self.search_in_theme(self.theme, self.name, s, self.exts)
                if self.ret != None:
                    return self.ret
                else:
                    for theme in self.theme.get_inherits_iter():
                        self.ret = self.search_in_theme(theme, self.name, s, self.exts)
                        if self.ret == None:
                            continue
                        else:
                            return self.ret
        return None

    def search_in_pixmaps(self, name, exts = constants.STD_ICON_EXTENSIONS):
        for ext in exts:
            self.item = '/usr/share/pixmaps/{0}.{1}'.format(self.name, ext)
            if p.isfile(self.item):
                return self.item
        else:
            return None

    def search_in_theme(self, theme, name, size, exts = constants.STD_ICON_EXTENSIONS):
        for root, subdir, files in os.walk(theme.ini.file_info.directory):
            if str(size) in root:
                for f in files:
                    for ext in exts:
                        self.item = '{0}.{1}'.format(name, ext)
                        if self.item == f:
                            return self.item


def test():
    pass
