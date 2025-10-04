#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "fastlz/fastlz.h"

#ifdef _MSC_VER
typedef unsigned __int32 uint32_t;
#else
#include <stdint.h>
#endif

PyObject* FastlzError;


static PyObject *compress(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *result;
    const char *input;
    char *output;
    int level = 0;
    Py_ssize_t input_len;
    Py_ssize_t output_alloc_size;
    int compressed_len;

    static char *arglist[] = {"string", "level", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y#|i", arglist, &input,
                                     &input_len, &level))
        return NULL;

    if (input_len > INT_MAX) {
        PyErr_SetString(PyExc_ValueError, "input string is too large to be compressed");
        return NULL;
    }

    if (level == 0) {
        if (input_len < 65536)
            level = 1;
        else
            level = 2;
    } else if (level != 1 && level != 2) {
        PyErr_SetString(PyExc_ValueError, "level must be either 1 or 2");
        return NULL;
    }

    output_alloc_size = (Py_ssize_t)(input_len * 1.05);
    if (output_alloc_size < 66) {
        output_alloc_size = 66;
    }

    output = (char *) malloc(output_alloc_size);
    if (output == NULL)
        return PyErr_NoMemory();

    compressed_len = fastlz_compress_level(level, input, (int)input_len, output);
    if (compressed_len == 0 && input_len != 0) {
        free(output);
        PyErr_SetString(FastlzError, "could not compress");
        return NULL;
    }

    result = Py_BuildValue("(y#n)", output, compressed_len, input_len);
    free(output);
    return result;
}


static PyObject *decompress(PyObject *self, PyObject *args) {
    PyObject *result;
    const char *input;
    Py_ssize_t input_len;
    char *output;
    Py_ssize_t output_len;
    int decompressed_len;

    if (!PyArg_ParseTuple(args, "y#n", &input, &input_len, &output_len))
        return NULL;

    if (output_len > INT_MAX || input_len > INT_MAX) {
        PyErr_SetString(PyExc_ValueError, "input is too large to be decompressed");
        return NULL;
    }

    output = (char *) malloc(output_len + 1);
    if (output == NULL)
        return PyErr_NoMemory();

    decompressed_len = fastlz_decompress(input, (int)input_len, output, (int)output_len);

    if (decompressed_len != output_len) {
        PyErr_SetString(FastlzError, "could not decompress");
        free(output);
        return NULL;
    }

    result = Py_BuildValue("y#", output, output_len);
    free(output);
    return result;
}


static PyMethodDef module_methods[] = {
    {"compress", (PyCFunction)compress, METH_VARARGS|METH_KEYWORDS,
     PyDoc_STR("Compress a string. Optionally provide a compression level.")},
    {"decompress", (PyCFunction)decompress, METH_VARARGS,
     PyDoc_STR("Decompress a string.")},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc,
"Python wrapper for FastLZ, a lightning-fast lossless compression library.");

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "fastlz",
    module_doc,
    -1,
    module_methods
};

PyMODINIT_FUNC
PyInit_fastlz(void) {
    PyObject *m, *d;

    m = PyModule_Create(&module_def);

    PyModule_AddObject(m, "__version__", Py_BuildValue("s", "0.0.2"));
    PyModule_AddObject(m, "__author__", Py_BuildValue("s", "Jared Suttles"));

    d = PyModule_GetDict(m);
    FastlzError = PyErr_NewException("fastlz.FastlzError", NULL, NULL);
    PyDict_SetItemString(d, "FastlzError", FastlzError);
    return m;
}
