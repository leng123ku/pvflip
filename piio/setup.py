# Primitive python wrapper for iio
# Copyright 2013, Gabriele Facciolo <facciolo@cmla.ens-cachan.fr>
#
# This file is part of pvflip.
# 
# Pvflip is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pvflip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with pvflip.  If not, see <http://www.gnu.org/licenses/>.

import distutils.ccompiler as cc
import os, os.path
import platform
import ctypes
import distutils.cmd
from distutils.core import setup #, Extension

class build_iio(distutils.cmd.Command):
    description = """build iio to a shared library"""
    
    user_options = [('compiler=', 'c', 'specify the compiler type. It must understand GCC arguments')
                    ,('release', 'r', 'build iio without debug asserts')
                    ]
    
    boolean_options = ['release']
    
    help_options = [
        ('help-compiler', None, "list available compilers", cc.show_compilers)
        ]

    compiler = None  

      ### libraries for IIO
    libraries = ['png','jpeg','tiff']
        
    def initialize_options (self):
        self.compiler = None
        self.release = True
        
    def finalize_options (self):
        pass
    
    def compile(self):
        if self.release:
            print("compiling iio in Release mode (No debug output or asserts)" )
        else:
            print("compiling iio in Debug mode (Defualt, prints debug output and asserts)")
        
        compiler = cc.new_compiler(compiler=self.compiler)

         # sources for IIO
        source_folders = ['./']
        sources = ['iio.c','freemem.c','fancy_image.c']

       ### removed the sources are just a couple of files
        #sources = []
        #for folder in source_folders:
        #    for fn in os.listdir(folder):
        #        fn_path = os.path.join(folder, fn)
        #        if fn_path[-1] == 'c':
        #            sources.append(fn_path)
        #        elif fn_path[-1] == 'o':
        #            os.remove(fn_path)

        include_folders = source_folders
        
        compiler_preargs = ['-std=gnu99'] 
        
        if self.release:
            compiler_preargs.append('-DNDEBUG')
        
        # check if we are on a 64bit python
        arch = ctypes.sizeof(ctypes.c_voidp) * 8
        
        if arch == 64 and platform.system() == 'Linux':
            compiler_preargs += ['-m64', '-O3', '-fPIC']
        elif arch == 32 and platform.system() == 'Linux':
            compiler_preargs += ['-m32', '-O3']
        elif arch == 64 and platform.system() == 'Darwin':
            compiler_preargs += ['-O3', '-arch', 'x86_64']
        elif platform.system() == 'Darwin':
            compiler_preargs += ['-O3', '-arch', 'i386']
        
        if platform.system() in ('Windows', 'Microsoft'):
            # Compile with stddecl instead of cdecl (-mrtd). 
            # Using cdecl cause a missing bytes issue in some cases
            # Because -mrtd and -fomit-frame-pointer (which is included in -O)
            # gives problem with function pointer to the sdtlib free function
            # we also have to use -fno-omit-frame-pointer
           # compiler_preargs += ['-mrtd', '-O3', '-shared', '-fno-omit-frame-pointer'] 
            compiler_preargs += ['-O3', '-static'] 
        
        if arch == 64 and platform.system() in ('Windows', 'Microsoft'):
            compiler_preargs += ['-m64']
        if arch == 32 and platform.system() in ('Windows', 'Microsoft'):
            compiler_preargs += ['-m32']
            
        for x in compiler.executables:
            args = getattr(compiler, x)
            try:
                args.remove('-mno-cygwin') #Not available on newer versions of gcc 
                args.remove('-mdll')
            except:
                pass
        
        objs = compiler.compile(sources, include_dirs=include_folders, extra_preargs=compiler_preargs)
        
        libname = 'iio'
        if arch == 64 and platform.system() != 'Darwin':
            libname += ''
        if arch == 64 and platform.system() == 'Darwin':
            libname = compiler.library_filename(libname, lib_type='shared')
            compiler.set_executable('linker_so', ['cc', '-dynamiclib', '-arch', 'x86_64'])
        elif arch == 32 and platform.system() == 'Darwin':
            libname = compiler.library_filename(libname, lib_type='shared')
            compiler.set_executable('linker_so', ['cc', '-dynamiclib', '-arch', 'i386'])
        else:
            libname = compiler.library_filename(libname, lib_type='shared')
        linker_preargs = [ '-lpng', '-ljpeg', '-ltiff']
        if platform.system() == 'Linux' and platform.machine() == 'x86_64':
            linker_preargs += ['-fPIC']
        if platform.system() in ('Windows', 'Microsoft'):
            # link with stddecl instead of cdecl
         #   linker_preargs += ['-mrtd'] 
            # remove link against msvcr*. this is a bit ugly maybe.. :)
            compiler.dll_libraries = [lib for lib in compiler.dll_libraries if not lib.startswith("msvcr")]
        compiler.link(cc.CCompiler.SHARED_LIBRARY, objs, libname, output_dir = './', extra_postargs=linker_preargs)
        
    def run(self):
        self.compile()
        


setup(
    name="piio",
    version="0.1.0",
    description="python iio wrapper",
    author="Gabriele Facciolo",
    author_email="contact@example.com",
    license='BSD',
    url='http://github.com//',
    packages=['.'],
#    ext_package='piio',
#    ext_modules = [iiomodule],
    cmdclass={'build':build_iio}
   )
