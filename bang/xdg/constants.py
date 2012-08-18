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
from os.path import expanduser, join
from os import environ

USER_HOME = expanduser('~')
XDG_DATA_DIRECTORIES = _env('XDG_DATA_DIRS')
XDG_MENU_DIRECTORIES = ['/etc/xdg/menus/']
XDG_DIRECTORY_DIRECTORIES = ['/usr/share/desktop-directories/']
XDG_APPICATION_DIRECTORIES = ['/usr/share/applications/']
XDG_ICON_DIRECTORIES = [join(USER_HOME,'.icons/'), '/usr/share/icons/', '/usr/share/pixmaps/']
XDG_THEME_DIRECTORIES = [join(USER_HOME,'.themes/'), '/usr/share/themes/']
STD_ICON_SIZES = '16, 24, 32, 36, 48, 64, 72, 96, 128, 160, 192, 256, scalable'.split(',')
STD_ICON_EXTENSIONS = ['png', 'svg', 'xpm']

def _env(var):
    item = environ[var]
    if ':' in item:
        return item.split(':')


def test():
    print(HOME)
    print(XDG_MENU_DIRECTORIES)
    print(XDG_DIRECTORY_DIRECTORIES)
    print(XDG_APPICATION_DIRECTORIES)
    print(XDG_ICON_DIRECTORIES)
    print(XDG_THEME_DIRECTORIES)
    print(STD_ICON_SIZES)
    print(STD_ICON_EXTENSIONS)

