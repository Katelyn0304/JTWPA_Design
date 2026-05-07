import gdsfactory as gf

from jtwpa_design.tech import LAYER

from .rectangle import rectangle


@gf.cell
def open_stub_capacitor(
    i: int = 0,
    width: float = 6.0,
    length: float = 232.0,
    ground_cap_gap: int = 2,
    contact_pad_height: float = 26.0,
    contact_overlap_x: float = 1.0,
    contact_overlap_y: float = 3.0,
    unit_cell_spacing: float = 20.0,
    jj_ground_mask_width: float = 32.0,
    bridge_width: float = 8.0,
    pier_radius: float = 2.5,
    pier_ground_edge: float = 3.0,
    general: bool = True,
) -> gf.Component:
    c = gf.Component()

    # hann = np.sin(np.pi * (i - 0.5)/n)**2
    # phase = np.cos(2*np.pi * (i - 0.5)/Lambda)
    # length = l0 * (1 + m * hann * phase)**(-2)

    c.add_polygon(
        [
            (-width / 2, contact_pad_height / 2 - contact_overlap_y),
            (width / 2, contact_pad_height / 2 - contact_overlap_y),
            (width / 2, length / 2),
            (-width / 2, length / 2),
        ],
        layer=LAYER.MAIN_METAL,
    )

    c.add_polygon(
        [
            (-width / 2, -contact_pad_height / 2 + contact_overlap_y),
            (width / 2, -contact_pad_height / 2 + contact_overlap_y),
            (width / 2, -length / 2),
            (-width / 2, -length / 2),
        ],
        layer=LAYER.MAIN_METAL,
    )

    c.add_polygon(
        [
            # (-width / 2 - contact_overlap_x, -contact_pad_height / 2),
            # (width / 2 + contact_overlap_x, -contact_pad_height / 2),
            # (width / 2 + contact_overlap_x, contact_pad_height / 2),
            # (-width / 2 - contact_overlap_x, contact_pad_height / 2),
            (-width / 2 - 0, -contact_pad_height / 2),
            (width / 2 + 0, -contact_pad_height / 2),
            (width / 2 + 0, contact_pad_height / 2),
            (-width / 2 - 0, contact_pad_height / 2),
        ],
        # layer=LAYER.AIR_BRIDGE_CONTACT,
        layer=LAYER.MAIN_METAL,
    )

    c.add_polygon(
        [
            (-width / 2 - contact_overlap_x, -contact_pad_height / 2),
            (width / 2 + contact_overlap_x, -contact_pad_height / 2),
            (width / 2 + contact_overlap_x, contact_pad_height / 2),
            (-width / 2 - contact_overlap_x, contact_pad_height / 2),
        ],
        layer=LAYER.AIR_BRIDGE,
    )

    c.add_polygon(
        [
            (-width / 2 - ground_cap_gap, -length / 2 - ground_cap_gap),
            (width / 2 + ground_cap_gap, -length / 2 - ground_cap_gap),
            (width / 2 + ground_cap_gap, length / 2 + ground_cap_gap),
            (-width / 2 - ground_cap_gap, length / 2 + ground_cap_gap),
        ],
        layer=LAYER.GROUND_MASK,
    )

    if general:
        pier1 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
        pier1.move(
            (unit_cell_spacing / 2, jj_ground_mask_width / 2 + pier_radius + pier_ground_edge)
        )
        pier2 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
        pier2.move(
            (unit_cell_spacing / 2, -(jj_ground_mask_width / 2 + pier_radius + pier_ground_edge))
        )
        if i % 5 == 0:
            bridge = c << rectangle(
                width=bridge_width,
                height=jj_ground_mask_width + pier_ground_edge * 2 + pier_radius * 2,
                layer=LAYER.AIR_BRIDGE,
            )
            bridge.movex(unit_cell_spacing / 2)

    # c.add_port("left", center=(-width/2, 0), orientation=180, width=1, layer=LAYER["Main"])
    # c.add_port("right", center=(width/2, 0), orientation=0, width=1, layer=LAYER["Main"])
    # c.add_port("top", center=(0, length/2), orientation=0, width=1, layer=LAYER["Main"])
    # c.add_port("bottom", center=(0, -length/2), orientation=180, width=1, layer=LAYER["Main"])

    return c
