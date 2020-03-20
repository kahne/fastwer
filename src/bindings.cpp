#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "fastwer.hpp"

namespace py = pybind11;


PYBIND11_MODULE(fastwer, m) {
    m.def("score", &fastwer::score, "",py::arg("hypo"), py::arg("ref"), py::arg("char_level") = false);
    m.def("score_sent", &fastwer::score_sent, "",py::arg("hypo"), py::arg("ref"), py::arg("char_level") = false);
}
