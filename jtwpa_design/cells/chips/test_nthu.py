import gdsfactory as gf

from jtwpa_design.cells.components.marker import marker
from jtwpa_design.cells.components.rectangle import rectangle
from jtwpa_design.cells.components.text_id import text_id
from jtwpa_design.parameters.chips.test import TestChipParams
from jtwpa_design.tech import LAYER


def _unprocessed_ground(size: float = 5900):
    c = gf.Component()
    c << rectangle(width=size, height=size, layer=LAYER.GROUND_MASK)
    c.add_port("center", center=(0, 0), orientation=180, width=1, layer=LAYER.GROUND_MASK)
    return c


@gf.cell
def test_chip_nthu(params: TestChipParams = TestChipParams()) -> gf.Component:
    c = gf.Component()

    gds_path = "jtwpa_design/cells/chips/gds_components/test_chip_without_ground_nthu_v2.gds"
    c << gf.import_gds(gds_path)
    c << text_id(
        id=params.test_id, text_size=params.label.text_size, margin=params.label.text_margin
    )
    marker1 = c << marker(
        size=params.marker.size,
        width=params.marker.width,
        boundary=params.marker.boundary,
    )
    marker1.movex(params.marker_coordinate)
    marker2 = c << marker(
        size=params.marker.size,
        width=params.marker.width,
        boundary=params.marker.boundary,
    )
    marker2.movex(-params.marker_coordinate)

    unprocessed_ground = _unprocessed_ground(size=params.frame.size - params.dicing.width)

    ground = gf.boolean(
        A=unprocessed_ground,
        B=c,
        operation="not",
        layer1=LAYER.GROUND_MASK,
        layer2=LAYER.GROUND_MASK,
        layer=LAYER.MAIN_METAL,
    )
    c.add_ref(ground)
    if params.include_dicing:
        c << gf.import_gds("jtwpa_design/cells/chips/gds_components/six_mm_chip_dicing.gds")
    c.flatten()

    return c
