# include "Python.h"
# include "TuioServer.h"
# include <iostream>


//http://superjared.com/entry/anatomy-python-c-module/


TuioServer *server;
int cursorAlive [20];

static PyObject * initServer (PyObject *self, PyObject *args) 
{
server = new TuioServer("127.0.0.1",3333);
return Py_BuildValue("i", 0);

}

static PyObject * move (PyObject *self, PyObject *args) 
{
int run , id ;
float x,y,X,Y,m;
 if (!PyArg_ParseTuple(args, "iifffff",&run, &id,&x,&y,&X,&Y,&m)) { return NULL;}

  server->addCurSet(id,x,y,X,Y,m);
  if (run==1){  server->sendCurMessages(); }

return Py_BuildValue("i", 0);
}

static PyObject * isMessageFull (PyObject *self, PyObject *args) 
{
int x=0;
if (server->freeCurSpace()){x=1;}
return Py_BuildValue("i", x);

}

static PyObject * CursorAlive (PyObject *self, PyObject *args) 
{

int endMess, id , indice;
if (!PyArg_ParseTuple(args, "iii",&endMess, &id,&indice)) { return NULL;}
if (endMess==0){cursorAlive[indice]=id;}
if (endMess==1){cursorAlive[indice]=id;server->addCurAlive(cursorAlive,indice+1);}

return Py_BuildValue("i", 0);

}


static PyMethodDef methods[] = { 
{"initServer", initServer, METH_VARARGS,"initialisation du Server Tuio."}, {"move", move, METH_VARARGS,"bouge la souris"},{"isMessageFull", isMessageFull, METH_VARARGS,"Message est plein"},{"CursorAlive", CursorAlive, METH_VARARGS,"selectionne les curseurs actif"},
{NULL, NULL, 0, NULL} /* Sentinel */ 
};
 
PyMODINIT_FUNC initTuioServerModule() { 
(void) Py_InitModule("TuioServerModule", methods);
 }
