import gdsfactory as gf

from jtwpa_design.tech import LAYER

from .rectangle import rectangle


@gf.cell(check_instances=False)
def marker(
    size: float = 100.0,
    width: float = 4.0,
    boundary: float = 50.0,
):
    c = gf.Component()
    c << rectangle(width=size, height=width, layer=LAYER.MAIN_METAL)
    c << rectangle(width=width, height=size, layer=LAYER.MAIN_METAL)
    c << rectangle(width=size + boundary * 2, height=size + boundary * 2, layer=LAYER.GROUND_MASK)
    return c


@gf.cell(check_instances=False)
def four_marker(
    size: float = 100.0,
    width: float = 4.0,
    boundary: float = 50.0,
):
    c = gf.Component()
    m1 = c << marker(size=size, width=width, boundary=boundary)
    m2 = c << marker(size=size, width=width, boundary=boundary)
    m3 = c << marker(size=size, width=width, boundary=boundary)
    m4 = c << marker(size=size, width=width, boundary=boundary)
    m1.move((-size / 2 - boundary / 2, -size / 2 - boundary / 2))
    m2.move((size / 2 + boundary / 2, -size / 2 - boundary / 2))
    m3.move((size / 2 + boundary / 2, size / 2 + boundary / 2))
    m4.move((-size / 2 - boundary / 2, size / 2 + boundary / 2))
    return c
