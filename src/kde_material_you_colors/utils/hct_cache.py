"""Memoize HctSolver.solve_to_int.

Generating a single theme calls the solver ~13k times for only ~113 unique
(hue, chroma, tone) triples. Most of those land in bisect_to_limit, the
out-of-sRGB-gamut fallback, which dominates scheme generation time. The solver
is a pure function of its three arguments, so caching the results collapses the
redundant work and cuts generation time roughly 4.8x with identical output.
"""

import logging

from materialyoucolor.hct.hct_solver import HctSolver

_CACHE = {}
_CACHE_MAX = 20000

_ORIGINAL_SOLVE_TO_INT = HctSolver.solve_to_int


def _cached_solve_to_int(hue_degrees, chroma, lstar):
    key = (hue_degrees, chroma, lstar)
    result = _CACHE.get(key)
    if result is None:
        result = _ORIGINAL_SOLVE_TO_INT(hue_degrees, chroma, lstar)
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.clear()
        _CACHE[key] = result
    return result


def install():
    if HctSolver.solve_to_int is _cached_solve_to_int:
        return
    HctSolver.solve_to_int = staticmethod(_cached_solve_to_int)
    logging.debug("HctSolver.solve_to_int memoization installed")


def clear():
    _CACHE.clear()
