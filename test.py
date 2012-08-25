#!python3
import sys, os
import bang.xdg.applications as a
import bang.xdg.constants as c
import bang.xdg.menus as m


#TODO: Get menu merging and layout working and stable.
    #-- Test with XFCE Menu.
#TODO: Write submenu.load_applications().
    #-- Need Evaluation algorithm.
#TODO: Support auto-start directory *low priority*.
#TODO: Finish "TrashCan" *low priority*.
#TODO: Bang Only -- Figure out how to control GTK+/Qt Theming

if __name__ == '__main__':
    c.test()
    print('\n')
    m.test()