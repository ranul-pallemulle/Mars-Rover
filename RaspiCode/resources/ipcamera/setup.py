from setuptools import setup, Extension

ipcamera_module = Extension('ipcamera',
                            include_dirs =
                            ['/usr/include/gstreamer-1.0','/usr/include/glib-2.0','/usr/lib/arm-linux-gnueabihf/glib-2.0/include'],
                            libraries =
                            ['pthread','gstreamer-1.0','gobject-2.0','glib-2.0'],
                            extra_compile_args=['-std=c++11'],
                            sources=['ipcamera_source.cpp','ipcamera_pymodule.cpp'],
                            language='c++')

redirect_module = Extension('streamredirect',
                            include_dirs = ['/usr/include/gstreamer-1.0','/usr/include/glib-2.0','/usr/lib/arm-linux-gnueabihf/glib-2.0/include'],
                            libraries = ['pthread','gstreamer-1.0','gobject-2.0','glib-2.0'],
                            extra_compile_args=['-std=c++11'],
                            sources=['redirect_source.cpp','redirect_pymodule.cpp'],
                            language='c++')

setup (name = 'IPCamera',
       version = '1.0',
       description = 'IP Camera streaming',
       ext_modules = [ipcamera_module, redirect_module])
