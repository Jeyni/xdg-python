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

from bang.xdg.constants import USER_UID
import bang.xdg.constants as constants
import bang.xdg.core as core
import subprocess as cmd
import datetime as dt
import shutil as sh
import os.path as p
import os


DATE_FORMAT = '%Y-%d-%mT%H:%M:%S'

def get_all_known_trash_folders():
    lines = cmd.check_output(['mount', '-v'], universal_newlines = True)
    lines = [l for l in lines.split('\n') if l.startswith('/dev/') and '/boot' not in l]
    trash_folders = constants.XDG_HOME_TRASH_DIRECTORIES
    for line in lines:
        d = line.split()[2] if line.split()[2] != '/' else ''
        if p.isdir(d + '/.Trash'):
            trash_folders.append(d + '/.Trash')
        elif p.isdir(d + '/.Trash-' + USER_UID):
            trash_folders.append(d + '/.Trash-' + USER_UID)
    return list(set(trash_folders))

def get_root_dir(path):
    return path.split('/')[1]

class TrashDump(object):
    def __init__(self):
        self.bins = [TrashCan(d) for d in get_all_known_trash_folders()]

    def delete(self, path):
        self.last_deleted = core.FileDescriptor(path)
        for bin in self.bins:
            if bin.root == get_root_dir(path):
                if p.isfile(path) or p.isdir(path):
                    bin.delete(path)
                else:
                    continue

    def erase(self, name):
        for bin in self.bins:
            if name in bin.list_contents():
                bin.erase(name)

    def restore(self, name):
        for bin in self.bins:
            if name in bin.list_contents():
                bin.restore(name)

    def get_last_deleted(self):
        return self.last_deleted

    def list_contents(self):
        self._cont = []
        for tf in self.bins:
            self._cont += tf.list_contents()
        return self._cont

    def list_infos(self):
        self._cont = []
        for tf in self.bins:
            self._cont += tf.list_infos()
        return self._cont

    def list_infos_as_obj(self):
        self._cont = []
        for tf in self.bins:
            self._cont += tf.list_infos_as_obj()
        return self._cont

    def __iter__(self):
        for b in self.bins:
            yield b


class TrashCan(object):
    def __init__(self, path):
        if path == None:
            self.path = constants.XDG_HOME_TRASH_DIRECTORIES[0]
        else:
            self.path = path
        self.root = get_root_dir(self.path)
        self.info = self.path + '/info/'
        self.files = self.path + '/files/'
        self.date_format = '%Y-%d-%mT%H:%M:%S' 
        self.template = \
        "[Trash Info]\n" +\
        "Path={original_path}\n" +\
        "DeletionDate={deletion_date}"

    def delete(self, path):
        self.last_deleted = core.FileDescriptor(path)
        sh.move(path, self.files)
        self.date_str = dt.datetime.today().strftime(self.date_format)
        self.write = self.info + self.last_deleted.name + '.trashinfo'
        with open(self.write, 'wt') as wt:
            wt.write(
                self.template.format(
                    original_path = path,
                    deletion_date = self.date_str
                    )
                )

    def erase(self, name):
        self._erased = self.files + name
        self._erased_i = self.info + name + '.trashinfo'
        if p.isdir(self._erased):
            sh.rmtree(self._erased)
        elif p.isfile(self._erased):
            os.remove(self._erased)
        else:
            raise Exception('file missing' + self._erased)
        os.remove(self._erased_i)

    def restore(self, name):
        self._info = TrashInfo(self.info + name + '.trashinfo')
        sh.move(self.files + name, self._info.original_path)
        os.remove(self._info.path)

    def get_last_deleted(self):
        return self.last_deleted

    def get_info_for(self, name):
        self._item = self.info + name + '.trashinfo'
        return TrashInfo(self._item)

    def list_contents(self):
        return os.listdir(self.files)

    def list_infos(self):
        return os.listdir(self.info)

    def list_infos_as_obj(self):
        return [TrashInfo(self.info + fi) for fi in os.listdir(self.info)]

    def __iter__(self):
        for item in self.list_contents():
            yield item

class TrashInfo(object):
    def __init__(self, path):
        self.ini = core.IniFile(path)
        self._sect = self.ini.get_section('Trash Info')
        self.path = path
        self.original_path = self._sect.get_value('Path')
        self.deletion_date = self._sect.get_value('DeletionDate')

def test():
    print(get_all_known_trash_folders())
    bin = TrashDump()
    print([b.path for b in bin.bins])
    print(bin.list_contents())
