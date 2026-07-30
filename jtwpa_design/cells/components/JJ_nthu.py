import gdsfactory as gf

from jtwpa_design.tech import LAYER

from .rectangle import rectangle


@gf.cell()
def JJ_nthu(
    square_size: float = 2.2,
    thin_line_width: float = 0.12,
    thin_line_length: float = 3.5,
    feet_width: float = 4.0,
    feet_length: float = 6.0,
    extend: bool = False,
    left_extend_length: float = 3.0,
    right_extend_length: float = 3.0,
    turn_left: bool = False,
    turn_right: bool = False,
) -> gf.Component:
    c = gf.Component()

    square = c << rectangle(width=square_size, height=square_size, layer=LAYER.JJ)
    square.move((-square_size / 2 + thin_line_width / 2, -square_size / 2 + thin_line_width / 2))
    thin_line_horizon = c << rectangle(
        width=thin_line_length, height=thin_line_width, layer=LAYER.JJ
    )
    thin_line_horizon.move((thin_line_length / 2, 0))
    thin_line_vertical = c << rectangle(
        width=thin_line_width, height=thin_line_length, layer=LAYER.JJ
    )
    thin_line_vertical.move((0, thin_line_length / 2))

    if extend:
        feet_top = c << rectangle(
            width=feet_width, height=feet_length + left_extend_length, layer=LAYER.JJ
        )
        feet_top.move((0, (feet_length + left_extend_length) / 2))
        feet_top.rotate(45)
        feet_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_bottom = c << rectangle(
            width=feet_width, height=feet_length + right_extend_length, layer=LAYER.JJ
        )
        feet_bottom.move((0, -(feet_length + right_extend_length) / 2))
        feet_bottom.rotate(45)
        feet_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))
    elif turn_left:
        feet_top = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_top.move((0, feet_length / 2))
        feet_extend_top = c << rectangle(
            width=left_extend_length, height=feet_width, layer=LAYER.JJ
        )
        feet_extend_top.move(((-left_extend_length + feet_width) / 2, feet_length))
        feet_top.rotate(45)
        feet_extend_top.rotate(45)
        feet_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_extend_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_bottom = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_bottom.move((0, -feet_length / 2))
        feet_extend_bottom = c << rectangle(
            width=right_extend_length, height=feet_width, layer=LAYER.JJ
        )
        feet_extend_bottom.move(((right_extend_length - feet_width) / 2, -feet_length))
        feet_bottom.rotate(45)
        feet_extend_bottom.rotate(45)
        feet_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))
        feet_extend_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))
    elif turn_right:
        feet_top = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_top.move((0, feet_length / 2))
        feet_extend_top = c << rectangle(
            width=left_extend_length, height=feet_width, layer=LAYER.JJ
        )
        feet_extend_top.move(((left_extend_length - feet_width) / 2, feet_length))
        feet_top.rotate(45)
        feet_extend_top.rotate(45)
        feet_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_extend_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_bottom = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_bottom.move((0, -feet_length / 2))
        feet_extend_bottom = c << rectangle(
            width=right_extend_length, height=feet_width, layer=LAYER.JJ
        )
        feet_extend_bottom.move(((-right_extend_length + feet_width) / 2, -feet_length))
        feet_bottom.rotate(45)
        feet_extend_bottom.rotate(45)
        feet_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))
        feet_extend_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))
    else:
        feet_top = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_top.move((0, feet_length / 2))
        feet_top.rotate(45)
        feet_top.move((thin_line_width / 2 + (feet_width / 1.414) / 2, 3.5745))
        feet_bottom = c << rectangle(width=feet_width, height=feet_length, layer=LAYER.JJ)
        feet_bottom.move((0, -feet_length / 2))
        feet_bottom.rotate(45)
        feet_bottom.move((3.5745, thin_line_width / 2 + (feet_width / 1.414) / 2))

    c.flatten()
    return c
