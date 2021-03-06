#!/usr/bin/python
#
# Generate the build tree and Makefiles for PyQwt.
#
# Copyright (C) 2001-2005 Gerard Vermeulen
# Copyright (C) 2000 Mark Colclough
#
# This file is part of PyQwt.
#
# -- LICENSE --
#
# PyQwt is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# PyQwt is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with PyQwt; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In addition, as a special exception, Gerard Vermeulen gives permission to
# link PyQwt dynamically with commercial, non-commercial or educational
# versions of Qt, PyQt and sip, and distribute PyQwt in this form, provided
# that equally powerful versions of Qt, PyQt and sip have been released under
# the terms of the GNU General Public License.
#
# If PyQwt is dynamically linked with commercial, non-commercial or
# educational versions of Qt, PyQt and sip, PyQwt becomes a free plug-in for
# a non-free program.
#
# -- LICENSE --


import compileall
import glob
import os
import pprint
import re
import shutil
import sys

import sipconfig
import pyqtconfig

try:
    import optparse # works in Python >= 2.3
except ImportError:
    import optik as optparse # version 1.4.1 is compatible with Python-2.1.

if sys.version_info < (2, 3, 0):
    True = 1
    False = 0


def compile_qt_program(name, configuration,
                       extra_defines=[],
                       extra_include_dirs=[],
                       extra_lib_dirs=[],
                       extra_libs=[],
                       ):
    """Compile a simple Qt application.

    name is the name of the single source file
    configuration is the pyqtconfig.Configuration()
    extra_defines is a list of extra preprocessor definitions
    extra_include_dirs is a list of extra directories to search for headers
    extra_lib_dirs is a list of extra directories to search for libraries
    extra_libs is a list of extra libraries
    """    
    makefile = sipconfig.ProgramMakefile(
        configuration, console=True, qt=True, warnings=True)
    
    makefile.extra_defines.extend(extra_defines)
    makefile.extra_include_dirs.extend(extra_include_dirs)
    makefile.extra_lib_dirs.extend(extra_lib_dirs)
    makefile.extra_libs.extend(extra_libs)

    exe, build = makefile.build_command(name)

    # zap a spurious executable
    try:
        os.remove(exe)
    except OSError:
        pass

    os.system(build)

    if not os.access(exe, os.X_OK):
        return None

    if sys.platform != "win32":
        exe = "./" + exe

    return exe

# compile_qt_program()

    
def copy_files(sources, directory):
    """Copy a list of files to a directory
    """ 
    for source in sources:
        shutil.copy2(source, os.path.join(directory, os.path.basename(source)))

# copy_files()


def fix_build_file(name, extra_sources, extra_headers, extra_moc_headers):
    """Extend the targets of a SIP build file with extra files 
    """
    
    keys = ('target', 'sources', 'headers', 'moc_headers')
    sbf = {}
    for key in keys:
        sbf[key] = []

    # Parse,
    nr = 0
    for line in open(name, 'r'):
        nr += 1
        if line[0] != '#':
            eq = line.find('=')
            if eq == -1:
                raise SystemExit, (
                    '"%s\" line %d: Line must be in the form '
                    '"key = value value...."' % (name, nr)
                    )
        key = line[:eq].strip()
        value = line[eq+1:].strip()
        if key in keys:
            sbf[key].append(value)

    # extend,
    sbf['sources'].extend(extra_sources)
    sbf['headers'].extend(extra_headers)
    sbf['moc_headers'].extend(extra_moc_headers)

    # and write.
    output = open(name, 'w')
    for key in keys:
        if sbf[key]:
            print >> output, '%s = %s' % (key, ' '.join(sbf[key]))

# fix_build_file()


def lazy_copy_file(source, target):
    """Lazy copy a file to another file:
    - check for a SIP time stamp to skip,
    - check if source and target do really differ,
    - copy the source file to the target if they do,
    - return True on copy and False on no copy.
    """
    if not os.path.exists(target):
        shutil.copy2(source, target)
        return True

    sourcelines = open(source).readlines()
    targetlines = open(target).readlines()

    # global length check
    if len(sourcelines) != len(targetlines):
        shutil.copy2(source, target)
        return True
    
    # skip a SIP time stamp 
    if (len(sourcelines) > 3
        and sourcelines[3].startswith(' * Generated by SIP')
        ):
        line = 4
    else:
        line = 0
        
    # line by line check
    while line < len(sourcelines):
        if sourcelines[line] != targetlines[line]:
            shutil.copy2(source, target)
            return True
        line = line + 1
        
    return False

# lazy_copy_file()


def check_numarray(configuration, options):
    """Check if the numarray extension has been installed.
    """
    if options.disable_numarray:
        options.excluded_features.append('-x HAS_NUMARRAY')
        return options
       
    try:
        import numarray
        # try to find numarray/arrayobject.h
        numarray_inc = os.path.join(
            configuration.py_inc_dir, 'numarray', 'arrayobject.h')
        if os.access(numarray_inc, os.F_OK):
            print 'Found numarray-%s.' % numarray.__version__
            options.extra_defines.append('HAS_NUMARRAY')
        else:
            print ('numarray has been installed, '
                   'but its headers are not in the standard location.\n'
                   'PyQwt will be build without support for numarray.\n'
                   '(Linux users may have to install a development package)'
                   )
            raise ImportError
    except ImportError:
        options.excluded_features.append('-x HAS_NUMARRAY')
        print ('Failed to import numarray: '
               'PyQwt will be build without support for numarray.'
               )
        
    return options

# check_numarray()


def check_numeric(configuration, options):
    """Check if the Numeric extension has been installed.
    """
    if options.disable_numeric:
        options.excluded_features.append('-x HAS_NUMERIC')
        return options
           
    try:
        import Numeric
        # try to find Numeric/arrayobject.h
        numeric_inc = os.path.join(
            configuration.py_inc_dir, 'Numeric', 'arrayobject.h')
        if os.access(numeric_inc, os.F_OK):
            print 'Found Numeric-%s.' % Numeric.__version__
            options.extra_defines.append('HAS_NUMERIC')
        else:
            print ('Numeric has been installed, '
                   'but its headers are not in the standard location.\n'
                   'PyQwt will be build without support for Numeric.\n'
                   '(Linux users may have to install a development package)'
                   )
            raise ImportError
    except ImportError:
        options.excluded_features.append('-x HAS_NUMERIC')
        print ('Failed to find Numeric: '
               'PyQwt will be build without support for Numeric.'
               )
        
    return options

# check_numeric()


def check_compiler(configuration, options):
    """Check compiler specifics
    """
    print 'Do not get upset by error messages in the next 4 compiler checks:'
    
    makefile = sipconfig.Makefile(configuration)
    generator = makefile.optional_string('MAKEFILE_GENERATOR', 'UNIX')
    if generator in ['MSVC', 'MSVC.NET']:
        options.extra_cxxflags.extend(['-GR'])

    program = (
        '#warning Provoke errors to test your compiler.\n'
        '#include <stddef.h>\n'
        'class a { public: void f(size_t); };\n'
        'void a::f(%s) {};\n'
        'int main() { return 0; }\n'
        '#warning Previous errors are harmless.\n'
        )
    name = "size_t_check.cpp"
    new = [
        '// Automagically generated by configure.py',
        '',
        '// Uncomment one of the following four lines',
        ]

    for ctype in ('int', 'long', 'unsigned int', 'unsigned long'):
        open(name, "w").write(program % ctype)
        print "Check if 'size_t' and '%s' are the same type." % ctype
        if compile_qt_program(name, configuration):
            comment = ''
            print "YES"
        else:
            print "NO"
            comment =  '//'
        new.append('%stypedef %s size_t;' % (comment, ctype))

    new.extend(['',
                '// Local Variables:',
                '// mode: C++',
                '// c-file-style: "stroustrup"',
                '// End:',
                '',
                ])

    new = os.linesep.join(new)
    types_sip = os.path.join(os.pardir, 'sip', 'types.sip')
    if os.access(types_sip, os.R_OK):
        old = open(types_sip, 'r').read()
    else:
        old = ''
    if old != new:
        open(types_sip, 'w').write(new)    
    
    return options

# check_compiler()


def check_os(configuration, options):
    """Adapt to different operating systems
    """
    print "Found '%s' operating system:" % os.name
    print sys.version

    if os.name == 'nt':
        options.extra_defines.append('WIN32')

    return options

# check_os()


def check_sip(configuration, options):
    """Check if PyQwt can be built with SIP
    """
    version = configuration.sip_version
    version_str = configuration.sip_version_str
    required = (
        'PyQwt requires SIP-4.2.x, -SIP-4.1.x, SIP-4.0.x,\n'
        'SIP-3.12.x, SIP-3.11.x or SIP-3.10.x.'
        )
    
    print "Found SIP-%s." % version_str

    if (0x030a00 <= version < 0x030d00):
        pass
    elif (0x040000 <= version < 0x040300):
        pass
    else:
        raise SystemExit, required

    return options

# check_sip


def check_iqt(configuration, options):
    """Check if building of the iqt package is possible
    """
    try:
        import readline
        if os.name == 'nt':
            print 'The iqt module will not be built on Windows.'
        else:
            options.packages.append('iqt')
    except ImportError:
        pass

    return options

# check_iqt()


def check_qwt(configuration, options):
    """Check if building of the qwt package is possible
    """
    # zap spurious qwt_version_info.py*
    for name in glob.glob('qwt_version_info.py*'):
        try:
            os.remove(name)
        except OSError:
            pass

    extra_include_dirs = []
    if options.qwt_sources:
        extra_include_dirs.append(os.path.join(options.qwt_sources, 'include'))
    if options.extra_include_dirs:
        extra_include_dirs.extend(options.extra_include_dirs)

    exe = compile_qt_program('qwt_version_info.cpp', configuration,
                             extra_include_dirs = extra_include_dirs)
    if not exe:
        raise SystemExit, 'Failed to build the qwt_version_info tool'

    os.system(exe)

    try:
        from qwt_version_info import QWT_VERSION, QWT_VERSION_STR
    except ImportError:
        raise SystemExit, 'Failed to import qwt_version_info'
    
    if QWT_VERSION == 0x040200:
        options.timelines.append('-t QWT_4_2_0')
    elif QWT_VERSION == 0x040300:
        options.timelines.append('-t QWT_4_3_0')
    else:
        raise SystemExit, (
            'Qwt-%s is not supported' % QWT_VERSION_STR
            )

    print ('Found Qwt-%s.' % QWT_VERSION_STR)
    
    options.packages.append('qwt')

    return options

# check_qwt()
    

def setup_iqt_build(configuration, options):
    """Setup the iqt package build
    """
    if 'iqt' not in options.packages:
        return

    print 'Setup the iqt package build.'
    
    build_dir = 'iqt'
    tmp_dir = 'tmp-' + build_dir
    install_dir = os.path.join(configuration.default_mod_dir, 'iqt')

    sources = (
        glob.glob(os.path.join(os.pardir, 'iqt', '*.cpp'))
        + glob.glob(os.path.join(os.pardir, 'iqt', '*.py'))
        + glob.glob(os.path.join(os.pardir, 'iqt', '*.sbf'))
        )

    # zap the temporary directory
    try:
        shutil.rmtree(tmp_dir)
    except:
        pass
    # make a clean temporary directory
    try:
        os.mkdir(tmp_dir)
    except:
        raise SystemExit, 'Failed to create the temporary build directory'

    # copy all source files
    copy_files(sources, tmp_dir)

    # copy lazily to the build directory to speed up recompilation
    if not os.path.exists(build_dir):
        try:
            os.mkdir(build_dir)
        except:
            raise SystemExit, 'Failed to create the build directory'

    lazy_copies = 0
    for pattern in ('*.c', '*.cpp', '*.h', '*.py', '*.sbf'):
        for source in glob.glob(os.path.join(tmp_dir, pattern)):
            target = os.path.join(build_dir, os.path.basename(source))
            if lazy_copy_file(source, target):
                print 'Copy %s -> %s.' % (source, target)
                lazy_copies += 1
    print '%s file(s) lazily copied.' % lazy_copies

    # byte-compile the Python files
    compileall.compile_dir(build_dir, 1, install_dir)

    makefile = sipconfig.ModuleMakefile(
        configuration = configuration,
        build_file = 'iqt.sbf',
        dir = 'iqt',
        install_dir = install_dir,
        installs = [[['__init__.py', '__init__.pyc'], install_dir]],
        qt = 1,
        warnings = 1,
        debug = options.debug
        )

    makefile._target = '_iqt'
    makefile.generate()

# setup_iqt_build()


def setup_qwt_build(configuration, options):
    """Setup the qwt package build
    """
    if 'qwt' not in options.packages:
        return
    
    print 'Setup the qwt package build.'

    build_dir = 'qwt'
    tmp_dir = 'tmp-' + build_dir
    build_file = os.path.join(tmp_dir, 'qwt.sbf')
    install_dir = os.path.join(configuration.default_mod_dir, 'qwt')
    sip_dir = os.path.join(configuration.pyqt_sip_dir, 'qwt')
    extra_sources = []
    extra_headers = []
    extra_moc_headers = []
    extra_py_files = glob.glob(os.path.join(os.pardir, 'qwt', '*.py'))
    
    # do we compile and link the sources of Qwt statically into PyQwt?
    if options.qwt_sources:
        extra_sources += glob.glob(os.path.join(
            options.qwt_sources, 'src', '*.cpp'))
        extra_headers += glob.glob(os.path.join(
            options.qwt_sources, 'include', '*.h'))
        extra_moc_headers = []
        for header in extra_headers:
            text = open(header).read()
            if re.compile(r'^\s*Q_OBJECT', re.M).search(text):
                extra_moc_headers.append(header)

    # add the interface to the numerical Python extensions
    extra_sources += glob.glob(os.path.join(os.pardir, 'numpy', '*.cpp'))
    extra_headers += glob.glob(os.path.join(os.pardir, 'numpy', '*.h'))

    # do we compile and link the sources of Qwt into PyQwt?
    if options.qwt_sources:
        # yes, zap all 'qwt'
        while options.extra_libs.count('qwt'):
            options.extra_libs.remove('qwt')
    elif 'qwt' not in options.extra_libs:
        # no, add 'qwt' if needed
        options.extra_libs.append('qwt')

    # zap the temporary directory
    try:
        shutil.rmtree(tmp_dir)
    except:
        pass
    # make a clean temporary directory
    try:
        os.mkdir(tmp_dir)
    except:
        raise SystemExit, 'Failed to create the temporary build directory'

    # copy the extra files
    copy_files(extra_sources, tmp_dir)
    copy_files(extra_headers, tmp_dir)
    copy_files(extra_moc_headers, tmp_dir)
    copy_files(extra_py_files, tmp_dir)

    # invoke SIP
    cmd = ' '.join(
        [configuration.sip_bin,
         # SIP assumes POSIX style path separators
         '-I', configuration.pyqt_sip_dir.replace('\\', '/'),
         '-b', build_file,
         '-c', tmp_dir,
         options.jobs,
         options.tracing,
         configuration.pyqt_qt_sip_flags,
         ]
        + options.sip_include_dirs
        + options.excluded_features
        + options.timelines
        # SIP assumes POSIX style path separators
        + [os.path.join(os.pardir, 'sip', 'qwtmod.sip').replace('\\', '/')]
        )

    print 'sip invokation:'
    pprint.pprint(cmd)

    if os.path.exists(build_file):
        os.remove(build_file)
    os.system(cmd)
    if not os.path.exists(build_file):
        raise SystemExit, 'SIP failed to generate the C++ code.'

    # fix the SIP build file
    fix_build_file(build_file,
                   [os.path.basename(f) for f in extra_sources],
                   [os.path.basename(f) for f in extra_headers],
                   [os.path.basename(f) for f in extra_moc_headers])
    
    # copy lazily to the build directory to speed up recompilation
    if not os.path.exists(build_dir):
        try:
            os.mkdir(build_dir)
        except:
            raise SystemExit, 'Failed to create the build directory'

    lazy_copies = 0
    for pattern in ('*.c', '*.cpp', '*.h', '*.py', '*.sbf'):
        for source in glob.glob(os.path.join(tmp_dir, pattern)):
            target = os.path.join(build_dir, os.path.basename(source))
            if lazy_copy_file(source, target):
                print 'Copy %s -> %s.' % (source, target)
                lazy_copies += 1
    print '%s file(s) lazily copied.' % lazy_copies

    # byte-compile the Python files
    compileall.compile_dir(build_dir, 1, install_dir)

    # files to be installed
    installs = []
    installs.append([[os.path.basename(f) for f in glob.glob(
        os.path.join(build_dir, '*.py*'))], install_dir])
    for option in options.sip_include_dirs:
        # split and undo the POSIX style path separator
        directory = option.split()[-1].replace('/', os.sep)
        if directory.startswith(os.pardir):
            installs.append([[os.path.join(os.pardir, f) for f in glob.glob(
                os.path.join(directory, "*.sip"))], sip_dir])

    # module makefile
    makefile = sipconfig.ModuleMakefile(
        configuration = configuration,
        build_file = os.path.basename(build_file),
        dir = build_dir,
        install_dir = install_dir,
        installs = installs,
        qt = 1,
        warnings = 1,
        debug = options.debug,
        )
    makefile.extra_cflags.extend(options.extra_cflags)
    makefile.extra_cxxflags.extend(options.extra_cxxflags)
    makefile.extra_defines.extend(options.extra_defines)
    makefile.extra_include_dirs.extend(options.extra_include_dirs)
    makefile.extra_lflags.extend(options.extra_lflags)
    makefile.extra_libs.extend(options.extra_libs)
    makefile.extra_lib_dirs.extend(options.extra_lib_dirs)
    if configuration.sip_version < 0x040000:
        makefile.extra_libs.insert(0, makefile.module_as_lib('qt'))
    makefile.generate()

# setup_qwt_build()


def setup_parent_build(configuration, options):
    """Generate the parent Makefile
    """
    print "Setup the PyQwt build."
     
    sipconfig.ParentMakefile(configuration = configuration,
                             subdirs = options.packages).generate()

# setup_main_build


def parse_args():
    """Return the parsed options and args from the command line
    """
    usage = (
        'python configure.py [options]'
        '\n\nEach option takes at most one argument, but some options'
        '\naccumulate arguments when repeated. For example, invoke:'
        '\n\n\tpython configure.py -I %s -I %s'
        '\n\nto search the current *and* parent directories for headers.'
        ) % (os.curdir, os.pardir)

    parser = optparse.OptionParser(usage=usage)

    common_options = optparse.OptionGroup(parser, 'Common options')
    common_options.add_option(
        '-Q', '--qwt-sources', default='', action='store',
        type='string', metavar='/sources/of/qwt',
        help=('compile and link the Qwt source files in'
              ' /sources/of/qwt statically into PyQwt'))
    common_options.add_option(
        '-I', '--extra-include-dirs', default=[], action='append',
        type='string', metavar='/usr/lib/qt3/include/qwt',
        help=('add an extra directory to search for headers'
              ' (the compiler must be able to find the Qwt headers'
              ' without the -Q option)'))
    common_options.add_option(
        '-L', '--extra-lib-dirs', default=[], action='append',
        type='string', metavar='/usr/lib/qt3/lib',
        help=('add an extra directory to search for libraries'
              ' (the linker must be able to find the Qwt library'
              ' without the -Q option)'))
    common_options.add_option(
        '-j', '--jobs', default=0, action='store',
        type='int', metavar='N',
        help=('concatenate the SIP generated code into N files'
              ' [default 1 per class] (to speed up make by running '
              ' simultaneous jobs on multiprocessor systems)'))
    parser.add_option_group(common_options)

    make_options = optparse.OptionGroup(parser, 'Make options')
    make_options.add_option(
        '--debug', default=False, action='store_true',
        help='enable debugging symbols [default disabled]')
    make_options.add_option(
        '--extra-cflags', default=[], action='append',
        type='string', metavar='EXTRA_CFLAG',
        help='add an extra C compiler flag')
    make_options.add_option(
        '--extra-cxxflags', default=[], action='append',
        type='string', metavar='EXTRA_CXXFLAG',
        help='add an extra C++ compiler flag')
    make_options.add_option(
        '-D', '--extra-defines', default=[], action='append',
        type='string', metavar='HAS_EXTRA_SENSORY_PERCEPTION',
        help='add an extra preprocessor definition')
    make_options.add_option(
        '-l', '--extra-libs', default=[], action='append',
        type='string', metavar='extra_sensory_perception',
        help='add an extra library')
    make_options.add_option(
        '--extra-lflags', default=[], action='append',
        type='string', metavar='EXTRA_LFLAG',
        help='add an extra linker flag')
    parser.add_option_group(make_options)

    sip_options = optparse.OptionGroup(parser, 'SIP options')
    sip_options.add_option(
        '-x', '--excluded-features', default=[], action='append',
        type='string', metavar='EXTRA_SENSORY_PERCEPTION',
        help=('add a feature for SIP to exclude'
              ' (normally one of the features in sip/features.sip)'))
    sip_options.add_option(
        '-t', '--timelines', default=[], action='append',
        type='string', metavar='EXTRA_SENSORY_PERCEPTION',
        help=('add a timeline option for SIP'
              ' (normally one of the timeline options in sip/timelines.sip)'))
    sip_options.add_option(
        '--sip-include-dirs', default=[os.path.join(os.pardir, 'sip')],
        action='append', type='string', metavar='SIP_INCLUDE_DIR',
        help='add an extra directory for SIP to search')
    sip_options.add_option(
        '--tracing', default=False, action='store_true',
        help=('enable tracing of the execution of the bindings'
              ' [default disabled]'))
    parser.add_option_group(sip_options)
    
    detection_options = optparse.OptionGroup(parser, 'Detection options')
    detection_options.add_option(
        '--disable-numarray', default=False, action='store_true',
        help='disable detection and use of numarray [default enabled]')
    detection_options.add_option(
        '--disable-numeric', default=False, action='store_true',
        help='disable detection and use of Numeric [default enabled]')
    parser.add_option_group(detection_options)

    options, args =  parser.parse_args()
    
    # tweak some of the options to facilitate later processing
    if options.jobs < 1:
        options.jobs = ''
    else:
        options.jobs = '-j %s' % options.jobs
        
    options.excluded_features = [
        ('-x %s' % f) for f in options.excluded_features
        ]

    # SIP assumes POSIX style path separators
    options.sip_include_dirs = [
        ('-I %s' % f).replace('\\', '/') for f in options.sip_include_dirs
    ]
    
    options.timelines = [
        ('-t %s' % t) for t in options.timelines
        ]

    if options.tracing:
        options.tracing = '-r'
    else:
        options.tracing = ''

    options.packages = []
    
    return options, args

# parse_args()


def main():
    """Generate the build tree and the Makefiles
    """
    try:
        configuration = pyqtconfig.Configuration()
    except AttributeError:
        raise SystemExit, (
            'SIP-3 and PyQt have been built with build.py (deprecated).\n'
            'Rebuild and reinstall SIP and PyQt with configure.py.'
            )

    options, args = parse_args()
    
    print 'Command line options:'
    pprint.pprint(options.__dict__)
    print

    options = check_sip(configuration, options)
    options = check_os(configuration, options)
    options = check_compiler(configuration, options)
    options = check_numarray(configuration, options)
    options = check_numeric(configuration, options)
    options = check_iqt(configuration, options)
    options = check_qwt(configuration, options)

    print
    print 'Extended command line options:'
    pprint.pprint(options.__dict__)
    print
    print 'The following packages will be built: %s.' % options.packages
    print
    setup_iqt_build(configuration, options)
    print
    setup_qwt_build(configuration, options)
    print
    setup_parent_build(configuration, options)
    print
    print 'Great, run make or nmake to build and install PyQwt.'

# main()


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except:
        print (
            'An internal error occured.  Please report all the output\n'
            'from the program, including the following traceback, to\n'
            'pyqwt-users@lists.sourceforge.net'
            )
        raise
        
# Local Variables: ***
# mode: python ***
# End: ***
