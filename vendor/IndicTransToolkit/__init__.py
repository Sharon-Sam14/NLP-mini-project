"""IndicTransToolkit (vendored pure-Python subset).

Upstream: https://github.com/VarunGumma/IndicTransToolkit - MIT License.
Only IndicProcessor (ported from Cython) and IndicEvaluator (unmodified
pure Python) are vendored; IndicDataCollator (training-only) is omitted.
"""

from .evaluator import IndicEvaluator
from .processor import IndicProcessor

__all__ = ["IndicEvaluator", "IndicProcessor"]
