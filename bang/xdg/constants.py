from os.path import expanduser, join

HOME = expanduser('~')
XDG_MENU_DIRECTORIES = ['/etc/xdg/menus/']
XDG_DIRECTORY_DIRECTORIES = ['/usr/share/desktop-directories/']
XDG_APPICATION_DIRECTORIES = ['/usr/share/applications/']
XDG_ICON_DIRECTORIES = [join(HOME,'.icons/'), '/usr/share/icons/', '/usr/share/pixmaps/']
XDG_THEME_DIRECTORIES = [join(HOME,'.themes/'), '/usr/share/themes/']
STD_ICON_SIZES = '16, 24, 32, 36, 48, 64, 72, 96, 128, 160, 192, 256, scalable'.split(',')
STD_ICON_EXTENSIONS = ['png', 'svg', 'xpm']

if __name__ == '__main__':
    print(HOME)
    print(XDG_MENU_DIRECTORIES)
    print(XDG_DIRECTORY_DIRECTORIES)
    print(XDG_APPICATION_DIRECTORIES)
    print(XDG_ICON_DIRECTORIES)
    print(XDG_THEME_DIRECTORIES)
    print(STD_ICON_SIZES)
    print(STD_ICON_EXTENSIONS)

