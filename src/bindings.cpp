#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "fastwer.hpp"

namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#ifndef VERSION_INFO
#define VERSION_INFO 0.0.0
#endif

PYBIND11_MODULE(fastwer, m) {
    m.doc() = "Fast word/character error rate (WER/CER) calculation";
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);

    m.def(
        "score",
        &fastwer::score,
        R"doc(
        Compute corpus-level WER/CER.

        Args:
            hypo: List of hypothesis strings.
            ref: List of reference strings (same length as hypo).
            char_level: If True, score by Unicode code point (CER); otherwise by word (WER).

        Returns:
            Error rate as a percentage rounded to 4 decimal places.

        Raises:
            ValueError: If hypo and ref have different lengths, or if all
                references are empty.
        )doc",
        py::arg("hypo"),
        py::arg("ref"),
        py::arg("char_level") = false);
    m.def(
        "score_sent",
        &fastwer::score_sent,
        R"doc(
        Compute sentence-level WER/CER.

        Args:
            hypo: Hypothesis string.
            ref: Reference string.
            char_level: If True, score by Unicode code point (CER); otherwise by word (WER).

        Returns:
            Error rate as a percentage rounded to 4 decimal places.

        Raises:
            ValueError: If the reference is empty.
        )doc",
        py::arg("hypo"),
        py::arg("ref"),
        py::arg("char_level") = false);
}
