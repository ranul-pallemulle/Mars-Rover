#include <Python.h>
#include "redirect_source.h"

static PyObject* redirect_start_redirect(PyObject* self, PyObject* args) {
    char* source_ip;
    int source_port;
    char* dest_ip;
    int dest_port;
    if (!PyArg_ParseTuple(args, "sisi", &source_ip, &source_port, &dest_ip, &dest_port)) {
	return nullptr;
    }
    int res = start_redirect(source_ip, source_port, dest_ip, dest_port);
    return PyLong_FromLong(res);
}

static PyObject* redirect_stop_redirect(PyObject* self, PyObject* args) {
    int res = stop_redirect();
    return PyLong_FromLong(res);
}

static PyMethodDef StreamRedirectMethods[] = {
    {"start", redirect_start_redirect, METH_VARARGS, "Start redirecting stream from source to destination."},
    {"stop", redirect_stop_redirect, METH_VARARGS, "Stop redirection."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef streamredirectmodule = {
    PyModuleDef_HEAD_INIT,
    "streamredirect",
    NULL,
    -1,
    StreamRedirectMethods
};

PyMODINIT_FUNC PyInit_streamredirect(void) {
    PyObject *m;
    m = PyModule_Create(&streamredirectmodule);
    if (m == NULL) {
	return NULL;
    }
    return m;
}
