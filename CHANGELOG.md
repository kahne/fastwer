# Changelog

## 0.2.0 - 2026-09-02

- Compute character error rates by Unicode code point and reject malformed
  UTF-8 input instead of treating individual UTF-8 bytes as characters.
- Reduce edit-distance memory usage from O(m*n) to O(min(m,n)).
- Raise Python exceptions for invalid inputs and empty references instead of
  relying on assertions.
- Support Python 3.8 through 3.13 and test Linux and Windows builds in CI.
- Ship type information for the public Python API.
- Remove the unnecessary runtime dependency on pybind11.

