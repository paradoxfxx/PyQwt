"""pyqt_distutils.command

Package containing implementation of all the pyqt_distutils commands.
"""
#
# Copyright (C) 2003 Gerard Vermeulen
#
# This file is part of PyQwt
#
# PyQwt is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# PyQwt is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU  General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyQwt; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In addition, as a special exception, Gerard Vermeulen gives permission to
# link PyQwt dynamically with commercial, non-commercial or educational
# versions of Qt, PyQt and sip, and distribute PyQwt in this form, provided
# that equally powerful versions of Qt, PyQt and sip have been released under
# the terms of the GNU General Public License.
#
# If PyQwt is dynamically linked with commercial, non-commercial or educational
# versions of Qt, PyQt and sip, PyQwt becomes a free plug-in for a non-free
# program.


distutils_all = [
    'build_py',
    'build_clib',
    'build_scripts',
    'clean',
    'install',
    'install_lib',
    'install_headers',
    'install_scripts',
    'install_data',
    'sdist',
    ]

__import__('distutils.command', globals(), locals(), distutils_all)

__all__ = [
    'build',
    'build_ext',
    'run_sip',
    'run_moc',
    'bdist',
    'bdist_dumb',
    'bdist_rpm',
    'bdist_wininst',
    ] + distutils_all

# Local Variables: ***
# mode: python ***
# End: ***
