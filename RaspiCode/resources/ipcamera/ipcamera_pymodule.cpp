#include <Python.h>
#include "ipcamera_source.h"

static PyObject* ipcamera_initialise(PyObject* self, PyObject* args) {
    char* ip;
    int port;
    if (!PyArg_ParseTuple(args, "si", &ip, &port)) {
	return nullptr;
    }
    int res = initialise(ip, port);
    return PyLong_FromLong(res);
}

static PyObject* ipcamera_start_stream(PyObject* self, PyObject* args) {
    int res = start_stream();
    return PyLong_FromLong(res);
}

static PyObject* ipcamera_stop_stream(PyObject* self, PyObject* args) {
    int res = stop_stream();
    return PyLong_FromLong(res);
}

static PyObject* ipcamera_cleanup(PyObject* self, PyObject* args) {
    int res = cleanup();
    return PyLong_FromLong(res);
}

static PyMethodDef IPCameraMethods[] = {
    {"initialise", ipcamera_initialise, METH_VARARGS, "Initialise the ip camera."},
    {"start_stream", ipcamera_start_stream, METH_VARARGS, "Set the ip camera gstreamer pipeline to 'PLAYING'."},
    {"stop_stream", ipcamera_stop_stream, METH_VARARGS, "Set the ip camera gstreamer pipeline to 'PAUSED'."},
    {"cleanup", ipcamera_cleanup, METH_VARARGS, "Clean up ip camera resources."},
    {NULL,NULL,0,NULL}
};

static struct PyModuleDef ipcameramodule = {
    PyModuleDef_HEAD_INIT,
    "ipcamera",
    NULL,
    -1,
    IPCameraMethods
};

PyMODINIT_FUNC PyInit_ipcamera(void) {
    PyObject *m;
    m = PyModule_Create(&ipcameramodule);
    if (m == NULL) {
    	return NULL;
    }
    return m;
}

