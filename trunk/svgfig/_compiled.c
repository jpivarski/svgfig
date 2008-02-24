#include <Python.h>

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

static PyObject *svgfig_curve(PyObject *self, PyObject *args) {
  return Py_BuildValue("(ddd)", 1., 2., 3.);
}

static PyMethodDef svgfig_methods[] = {
  {"curve", ((PyCFunction)(svgfig_curve)), METH_VARARGS, ""},
  {NULL}
};

PyMODINIT_FUNC init_compiled() {
  Py_InitModule3("_compiled", svgfig_methods, "");
}
