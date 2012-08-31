#!python3
import sys, os
import bang.xdg.applications as a
import bang.xdg.constants as c
import bang.xdg.menus as m
import bang.xdg.icons as i
import bang.xdg.trash as t


#TODO: Support auto-start directory *low priority*.
#TODO: Bang Only -- Figure out how to control GTK+/Qt Theming

if __name__ == '__main__':
    c.test()
    print('\n')
    i.test()
    print('\n')
    m.test()
    print('\n')
    t.test()