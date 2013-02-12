#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Team:
#   J Phani Mahesh <phanimahesh@gmail.com> 
#   Barneedhar (jokerdino) <barneedhar@ubuntu.com> 
#   Amith KK <amithkumaran@gmail.com>
#   Georgi Karavasilev <motorslav@gmail.com>
#   Sam Tran <samvtran@gmail.com>
#   Sam Hewitt <hewittsamuel@gmail.com>
#
# Description:
#   A One-stop configuration tool for Unity.
#
# Legal Stuff:
#
# This file is a part of Unity Tweak Tool
#
# Unity Tweak Tool is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# Unity Tweak Tool is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/gpl-3.0.txt>

import os
import sys

try:
    import DistUtilsExtra.auto
except ImportError:
    print >> sys.stderr, 'To build unity-tweak-tool you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_config_old(libdir, values = {}):

    filename = os.path.join(libdir, 'UnityTweakTool/section/sphagetti/unitytweakconfig.py')
    oldvalues = {}
    try:
        fin = open(filename, 'r')
        fout = open(filename + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except u.URLError as e:
        print ("ERROR: Can't find %s" % filename)
        sys.exit(1)
    return oldvalues

def update_config_new(libdir, values = {}):

    filename = os.path.join(libdir, 'UnityTweakTool/config/data.py')
    oldvalues = {}
    try:
        fin = open(filename, 'r')
        fout = open(filename + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except u.URLError as e:
        print ("ERROR: Can't find %s" % filename)
        sys.exit(1)
    return oldvalues

def update_config(libdir,values={}):
    update_config_new(libdir,values)
    update_config_old(libdir,values)

def move_desktop_open(root, target_data, prefix):

    old_desktop_path = os.path.normpath(root + target_data +
                                        '/share/applications')
    old_desktop_file = old_desktop_path + '/unity-tweak-tool.desktop'
    desktop_path = os.path.normpath(root + prefix + '/share/applications')
    desktop_file = desktop_path + '/unity-tweak-tool.desktop'

    if not os.path.exists(old_desktop_file):
        print ("ERROR: Can't find", old_desktop_file)
        sys.exit(1)
    elif target_data != prefix + '/':
        # This is an /opt install, so rename desktop file to use extras-
        desktop_file = desktop_path + '/extras-unity-tweak-tool.desktop'
        try:
            os.makedirs(desktop_path)
            os.rename(old_desktop_file, desktop_file)
            os.rmdir(old_desktop_path)
        except OSError as e:
            print ("ERROR: Can't rename", old_desktop_file, ":", e)
            sys.exit(1)

    return desktop_file

def update_desktop_open(filename, target_pkgdata, target_scripts):

    try:
        fin = open(filename, 'r')
        fout = open(filename + '.new', 'w')

        for line in fin:
            if 'Icon=' in line:
                line = "Icon=%s\n" % (target_pkgdata + 'media/unity-tweak-tool.svg')
            elif 'Exec=' in line:
                cmd = line.split("=")[1].split(None, 1)
                line = "Exec=%s" % (target_scripts + 'unity-tweak-tool')
                if len(cmd) > 1:
                    line += " %s" % cmd[1].strip()  # Add script arguments back
                line += "\n"
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except u.URLError as e:
        print ("ERROR: Can't find %s" % filename)
        sys.exit(1)

def compile_schemas(root, target_data):
    if target_data == '/usr/':
        return  # /usr paths dirgon't need this, they will be handled by dpkg
    schemadir = os.path.normpath(root + target_data + 'share/glib-2.0/schemas')
    if (os.path.isdir(schemadir) and
            os.path.isopen('/usr/bin/glib-compile-schemas')):
        os.system('/usr/bin/glib-compile-schemas "%s"' % schemadir)


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        DistUtilsExtra.auto.install_auto.run(self)

        target_data = '/' + os.path.relpath(self.install_data, self.root) + '/'
        target_pkgdata = target_data + 'share/unity-tweak-tool/'
        target_scripts = '/' + os.path.relpath(self.install_scripts, self.root) + '/'

        values = {'__unity_tweak_tool_data_directory__': "'%s'" % (target_pkgdata),
                  '__version__': "'%s'" % self.distribution.get_version()}
        update_config(self.install_lib, values)

        desktop_file = move_desktop_open(self.root, target_data, self.prefix)
        update_desktop_open(desktop_file, target_pkgdata, target_scripts)
        compile_schemas(self.root, target_data)

##################################################################################

DistUtilsExtra.auto.setup(
    name='unity-tweak-tool',
    version='0.0.2',
    license='GPL-3',
    author='Freyja Development Team',
    #author_email='email@ubuntu.com',
    description='A One-stop configuration tool for Unity',
    url='https://launchpad.net/unity-tweak-tool',
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )

