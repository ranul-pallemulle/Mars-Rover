from setuptools import setup, Extension
from pkgconfig import pkgconfig

ipcamera_module = Extension('ipcamera',
                            extra_compile_args=['-std=c++11'],
                            sources=['ipcamera_source.cpp','ipcamera_pymodule.cpp'],
                            language='c++',
                            **pkgconfig('gstreamer-1.0','gstreamer-plugins-base-1.0'))

redirect_module = Extension('streamredirect',
                            extra_compile_args=['-std=c++11'],
                            sources=['redirect_source.cpp','redirect_pymodule.cpp'],
                            language='c++',
                            **pkgconfig('gstreamer-1.0','gstreamer-plugins-base-1.0'))

setup (name = 'IPCamera',
       version = '1.0',
       description = 'IP Camera streaming',
       ext_modules = [ipcamera_module, redirect_module])
