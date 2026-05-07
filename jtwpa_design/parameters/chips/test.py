from pydantic import Field

from jtwpa_design.parameters._base import ParameterModel
from jtwpa_design.parameters.features.chip_frame import ChipFrameParams
from jtwpa_design.parameters.features.label import ChipLabelStyleParams
from jtwpa_design.parameters.features.marker import MarkerStyleParams

try:
    from jtwpa_design.parameters.features.dicing import DicingParams
except ModuleNotFoundError:

    class DicingParams(ParameterModel):
        width: float = 0.0


class TestChipParams(ParameterModel):
    frame: ChipFrameParams = Field(default_factory=ChipFrameParams)
    test_id: str = "T1"

    label: ChipLabelStyleParams = Field(default_factory=ChipLabelStyleParams)

    marker_coordinate: float = 2600.0
    marker: MarkerStyleParams = Field(default_factory=MarkerStyleParams)

    include_dicing: bool = True
    dicing: DicingParams = Field(default_factory=DicingParams)
