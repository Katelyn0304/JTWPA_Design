from pydantic import Field

from jtwpa_design.parameters._base import ParameterModel
from jtwpa_design.parameters.assemblies.jtwpa_line import JTWPALineParams
from jtwpa_design.parameters.features.chip_frame import ChipFrameParams
from jtwpa_design.parameters.features.label import ChipLabelStyleParams
from jtwpa_design.parameters.features.marker import MarkerStyleParams

try:
    from jtwpa_design.parameters.features.dicing import DicingParams
except ModuleNotFoundError:

    class DicingParams(ParameterModel):
        width: float = 0.0


class SpiralChipParams(ParameterModel):
    frame: ChipFrameParams = Field(default_factory=ChipFrameParams)
    line: JTWPALineParams = Field(default_factory=JTWPALineParams)
    wafer_id: str = "W01"
    chip_id: str = "C01"

    label: ChipLabelStyleParams = Field(default_factory=ChipLabelStyleParams)

    marker_coordinate: float = 2200.0
    marker: MarkerStyleParams = Field(default_factory=MarkerStyleParams)

    include_dicing: bool = True
    dicing: DicingParams = Field(default_factory=DicingParams)
