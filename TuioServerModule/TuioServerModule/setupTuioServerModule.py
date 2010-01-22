from distutils.core import setup, Extension

module =  Extension("TuioServerModule", ["TuioServerModule.cpp"],include_dirs=['./include'],library_dirs=['/usr/local/lib'],libraries=['TuioServer','oscpack'])

setup (name = 'TuioServerModule',version = '0.2',author='Anthony Perron',author_email='anthony-perron@hotmail.fr',description = 'Tuio Server',ext_modules = [module] )

# -> construit /usr/local/lib/python2.6/dist-packages/libTuioServerModule.so