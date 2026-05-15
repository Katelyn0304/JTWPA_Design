from pathlib import Path

import gdsfactory as gf

from jtwpa_design.cells.chips.spiral import spiral_chip
from jtwpa_design.cells.chips.test import test_chip
from jtwpa_design.cells.components.marker import marker
from jtwpa_design.cells.components.rectangle import rectangle
from jtwpa_design.parameters.chips.twenty_five_mm_chip import TwentyFiveMMChipParams
from jtwpa_design.parameters.rules import LayoutRules
from jtwpa_design.tech import LAYER


def _unprocessed_ground(size: float = 24900):
    c = gf.Component()
    c << rectangle(width=size, height=size, layer=LAYER.GROUND_MASK)
    c.add_port("center", center=(0, 0), orientation=180, width=1, layer=LAYER.GROUND_MASK)
    return c


@gf.cell(check_instances=False)
def _corner_markers(
    size: float = 400, width: float = 20, boundary: float = 200, coordinate: float = 11200
) -> gf.Component:
    c = gf.Component()
    marker_1 = c << marker(size=size, width=width, boundary=boundary)
    marker_1.move((-coordinate, -coordinate))
    marker_2 = c << marker(size=size, width=width, boundary=boundary)
    marker_2.move((coordinate, coordinate))
    marker_3 = c << marker(size=size, width=width, boundary=boundary)
    marker_3.move((-coordinate, coordinate))
    marker_4 = c << marker(size=size, width=width, boundary=boundary)
    marker_4.move((coordinate, -coordinate))
    return c


@gf.cell(check_instances=False)
def twenty_five_mm_chip(
    spiral_id_list: list[str],
    test_id_list: list[str],
    params: TwentyFiveMMChipParams = TwentyFiveMMChipParams(),
    rules: LayoutRules = LayoutRules(),
) -> gf.Component:
    c = gf.Component()
    temp = gf.Component()

    chip_coordinate = params.spiral_chip.frame.size
    test_chip_points = [
        (-chip_coordinate, -chip_coordinate),
        (chip_coordinate, chip_coordinate),
    ]
    spiral_chip_points = [
        (0, -chip_coordinate),
        (chip_coordinate, -chip_coordinate),
        (-chip_coordinate, 0),
        (0, 0),
        (chip_coordinate, 0),
        (-chip_coordinate, chip_coordinate),
        (0, chip_coordinate),
    ]
    for i in range(len(test_chip_points)):
        test_chip_ref = temp << test_chip(
            params=params.test_chip.model_copy(
                update={"test_id": test_id_list[i], "include_dicing": False}
            ),
        )
        test_chip_ref.move(test_chip_points[i])

    for i in range(len(spiral_chip_points)):
        spiral_chip_ref = temp << spiral_chip(
            params=params.spiral_chip.model_copy(
                update={"chip_id": spiral_id_list[i], "include_dicing": False}
            ),
            rules=rules,
        )
        spiral_chip_ref.move(spiral_chip_points[i])

    dicing_path = Path("jtwpa_design/cells/chips/gds_components/twenty_five_mm_chip_dicing.gds")
    if dicing_path.exists():
        temp << gf.import_gds(dicing_path)

    mark_path = Path("jtwpa_design/cells/chips/gds_components/A25mark_250919.gds")
    if mark_path.exists():
        temp << gf.import_gds(mark_path)

    temp << _corner_markers(
        size=params.marker_size,
        width=params.marker_width,
        boundary=params.marker_boundary,
        coordinate=params.marker_coordinate,
    )

    unprocessed_ground = _unprocessed_ground(
        size=params.chip_size - params.spiral_chip.dicing.width
    )

    _ = gf.boolean(
        A=unprocessed_ground,
        B=temp,
        operation="not",
        layer1=LAYER.GROUND_MASK,
        layer2=LAYER.GROUND_MASK,
        layer=LAYER.MAIN_METAL,
    )
    c.add_ref(_)
    c << temp

    return c
