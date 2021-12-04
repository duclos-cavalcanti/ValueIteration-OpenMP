## Interface python code for CFFI

## Imports
from cffi import FFI

def compile_interface(verbose:bool = True) -> object:
  """
  Use API mode of cffi to get speed of access and proper errors.
  This means you invoke
  >>> ffi.set_source(...)
  with headers and path to libraries followed by the compilation step
  >>> ffi.compile(verbose=True)
  which is started by importing the backend
  Parameters:
      - verbose: whether (=True, default) or not (=False) to print information about compilation status [Boolean]
  Returns:
      - output: compiled code [object]
  """
  ## the main FFI instance which we use to create the interface
  ffi = FFI()
  ffi.cdef("""int cffi_example(int i);""")

  ffi.set_source("cpp_interface",  ## name of the output C/C++ extension, name is not important, but use sth unique

                 ## header with the interface, the content must match the cdef's from above
                 ## the content of that interface.h could also be defined here as python string, but the C-Include
                 ## results in less duplicated code
                 """ #include "interface.h" """,

                 ## additional include directories as list of strings, here only the public headers of the library
                 include_dirs=['include'],

                 ## includes pi.c as additional sources
                 ## (we don't need this, your source code is already compiled as library)
                 # sources=['src/foo.c'],

                 ## our code is in a shared / static library, hence we have to link against it
                 ## 'lib' prefix and '.so' suffix are already covered by ffi, so we put here just the name
                 ##  as specified in CMakeLists.txt
                 libraries=['cpp_backend_lib'],

                 ## 'make install' copies the library into this folder (located in the same directory as this script)
                 ## Provide a list of string with extra lib directories
                 library_dirs=['lib'],

                 ## rpath is there to add properly 'libbackend.so' to LD_LIBRARY_PATH without exporting by hand
                 ## the directory as environment variable, i.e you can avoid to write something like
                 ## >>> export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.../backend/lib
                 ## in your bashrc or everytime in the console.
                 ## from the troubleshooting section of CFFI:
                 ##   --> you can compile MODULENAME.so with the path hard-coded inside in the first place.
                 ##   -- > $ORIGIN is directory where MODULE_NAME.so is, i.e. the name directly after set_source(...)
                 ## hence, also add our 'lib' directory to $ORIGIN, then it works.
                 ## use the extra link args to inform the linker about openmp (for later)
                 extra_link_args=['-Wl,-rpath=$ORIGIN/lib', '-fopenmp'],

                 ## to get a fast interface compile with optimizations (similar to CMakeLists.txt, look there for
                 ## explanations)
                 ## currently I don't know how to get rid of default -O2 argument. If you look at the console output
                 ##  you will see both -O3 and -O2. I don't know what gcc does if both are specified (choosing highest or
                 ## lowest, maybe using both?!)
                 ## nevertheless, the interface should not be the bottleneck, as it is just forwarding the pointers to
                 ##  the already compiled library.
                 extra_compile_args=['-O3', '-march=native', '-ffast-math', '-fopenmp', '-D use_openmp'],

                 ## the ``source_extension`` keyword makes sure the C compiler treats it
                 ## as C++.  The ``extern "C"`` part in the C++ code makes sure that the
                 ## function name is not mangled in the compiled module.
                 source_extension='.cpp')

  return ffi.compile(verbose=verbose)

## you can use this python file directly to compile the interface
if __name__ == "__main__":
  compile_interface()
