CXX = g++
INCLUDES = -I./
COPTS  = -Wall -O3
CDEBUG = -Wall -g 
CXXFLAGS = $(COPTS) $(INCLUDES)

LIBNAME = libTuioServer
LIBSONAME = $(LIBNAME).so
LIBFILENAME = $(LIBSONAME).1.0.0

PREFIX = /usr/local
INSTALL = /usr/bin/install -c


all:	tuioServer

tuioServer : TuioServer.cpp
	$(CXX) -shared -I../oscpack -o $(LIBFILENAME) $+ $(LIBS) 

#Installs the library on a system global location
install: tuioServer
	@$(INSTALL) -m 755 $(LIBFILENAME) $(PREFIX)/lib/$(LIBFILENAME)
	@ln -s -f $(PREFIX)/lib/$(LIBFILENAME) $(PREFIX)/lib/$(LIBSONAME) 
	@mkdir  -p $(PREFIX)/include/TuioServer
	@$(INSTALL) -m 644 TuioServer.h $(PREFIX)/include/TuioServer
	@echo "SUCCESS! TuioServer has been installed in $(PREFIX)/lib and $(PREFIX)/include/TuioServer/"
	@echo "now doing ldconfig..."
	@ldconfig

