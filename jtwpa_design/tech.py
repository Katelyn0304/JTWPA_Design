"""Technology definitions."""

import gdsfactory as gf
import yaml
from gdsfactory.technology import LayerViews
from gdsfactory.typings import Layer

from jtwpa_design.config import PATH


class LayerMapQPDK(gf.LayerEnum):
    """Layer map for QPDK technology.

    Simplified version for 2D layout only - no simulation features.
    """

    layout = gf.constant(gf.kcl.layout)

    # Basic metal layers
    MAIN_METAL: Layer = (1, 0)
    JJ: Layer = (2, 0)
    AIR_BRIDGE_CONTACT: Layer = (3, 0)
    AIR_BRIDGE: Layer = (4, 0)
    GROUND_MASK: Layer = (1, 1)
    WG: Layer = (102, 0)  # Waveguide layer


# Load layer views from yaml
LAYER_VIEWS = LayerViews(filepath=PATH.lyp_yaml)

# Use class directly for layer access
L = LAYER = LayerMapQPDK
