import gdsfactory as gf

from jtwpa_design.cells.chips.twenty_five_mm_chip_nthu import twenty_five_mm_chip_nthu
from jtwpa_design.cells.components.text_id import text_id
from jtwpa_design.parameters.rules import LayoutRules
from jtwpa_design.parameters.wafers.four_inch_wafer import WaferParams
from jtwpa_design.tech import LAYER


def _unprocessed_ground(size: float = 101600):
    c = gf.Component()
    c << gf.components.circle(radius=size / 2, layer=LAYER.GROUND_MASK)
    c.add_port("center", center=(0, 0), orientation=180, width=1, layer=LAYER.GROUND_MASK)
    return c


def generate_spiral_chips_id(number: int = 49) -> list[list[str]]:
    id_list = []
    for i in range(1, number + 1):
        if i < 10:
            id_list.append(f"C0{i}")
        else:
            id_list.append(f"C{i}")
    split_list = [id_list[i : i + 7] for i in range(0, len(id_list), 7)]
    return split_list


def generate_test_chips_id(number: int = 14) -> list[list[str]]:
    id_list = []
    for i in range(1, number + 1):
        id_list.append(f"T{i}")
    split_list = [id_list[i : i + 2] for i in range(0, len(id_list), 2)]
    return split_list


@gf.cell
def four_inches_wafer_nthu(
    params: WaferParams = WaferParams(), rules: LayoutRules = LayoutRules()
) -> gf.Component:
    c = gf.Component()

    spiral_id_list = generate_spiral_chips_id()
    test_id_list = generate_test_chips_id()

    chip_points = [
        (-25000, -17000),
        (0, -17000),
        (25000, -17000),
        (-25000, 8000),
        (0, 8000),
        (25000, 8000),
        (0, 33000),
    ]
    for i in range(len(spiral_id_list)):
        chip_ref = c << twenty_five_mm_chip_nthu(
            spiral_id_list[i],
            test_id_list[i],
            params=params.twenty_five_mm_chip,
            rules=rules,
        )
        chip_ref.move(chip_points[i])

    wafer_id = c << text_id(
        id="NCU JTWPA " + params.wafer_id,
        text_size=params.label.text_size,
        margin=params.label.text_margin,
    )
    wafer_id.movey(params.label.text_coordinate)

    unprocessed_ground = _unprocessed_ground(size=params.wafer_size)

    ground = gf.boolean(
        A=unprocessed_ground,
        B=c,
        operation="not",
        layer1=LAYER.GROUND_MASK,
        layer2=LAYER.GROUND_MASK,
        layer=LAYER.MAIN_METAL,
    )
    c.add_ref(ground)
    c.flatten()

    return c
