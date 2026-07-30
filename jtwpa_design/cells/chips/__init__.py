from sympy import im

from jtwpa_design.cells.chips.spiral import (
    # JJ_ground_mask,
    # bridge_on_cpw,
    # capacitors_JJs,
    # jtwpa_line,
    spiral_chip,
    # twpa_cpw,
)
from jtwpa_design.cells.chips.spiral_nthu import (
    # capacitors_JJs_nthu,
    # jtwpa_line_nthu,
    # bridge_on_cpw_nthu,
    spiral_chip_nthu,
)
from jtwpa_design.cells.chips.test import test_chip
from jtwpa_design.cells.chips.test_nthu import test_chip_nthu

# from jtwpa_design.cells.chips.twenty_five_mm_chip import twenty_five_mm_chip
# from jtwpa_design.cells.chips.twenty_five_mm_chip_nthu import twenty_five_mm_chip_nthu

__all__ = [
    # "capacitors_JJs",
    # "JJ_ground_mask",
    # "twpa_cpw",
    # "jtwpa_line",
    "spiral_chip",
    # "capacitors_JJs_nthu",
    # "jtwpa_line_nthu",
    # "bridge_on_cpw_nthu",
    "spiral_chip_nthu",
    "test_chip",
    "test_chip_nthu",
    # "twenty_five_mm_chip",
    # "twenty_five_mm_chip_nthu",
    # "bridge_on_cpw",
]


def __getattr__(name):
    if name == "capacitors_JJs":
        from .spiral import capacitors_JJs

        return capacitors_JJs
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
