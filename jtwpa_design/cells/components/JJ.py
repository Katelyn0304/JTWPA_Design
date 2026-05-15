import gdsfactory as gf
import numpy as np

from jtwpa_design.tech import LAYER, Layer

from .rectangle import rectangle


PRINCETON_JJ_INITIAL_ROTATION = 135.0-180


def _add_port_from_port(
    component: gf.Component,
    name: str,
    port,
) -> None:
    component.add_port(
        name,
        center=port.center,
        orientation=port.orientation,
        width=port.width,
        layer=port.layer,
    )


def _farthest_patch_port(ref):
    ports = [ref.ports["top"], ref.ports["bottom"]]
    return max(ports, key=lambda port: np.linalg.norm(np.asarray(port.center, dtype=float)))


def _adapter_core_orientation_learning(theta_deg: float) -> float:
    theta_deg = (theta_deg + 180) % 360 - 180
    if -22.5 <= theta_deg < 22.5:
        return 135
    elif 22.5 <= theta_deg < 67.5:
        return 90
    elif 67.5 <= theta_deg < 80:
        return 90
    elif 80 <= theta_deg < 112.5:
        return 270
    elif 112.5 <= theta_deg < 120:
        return 225
    elif 120 <= theta_deg < 157.5:
        return 270
    elif 157.5 <= theta_deg < 180:
        return 90
    elif -180 <= theta_deg < -157.5:
        return 90
    elif -157.5 <= theta_deg < -112.5:
        return 90
    elif -112.5 <= theta_deg < -82.5:
        return 270
    elif -82.5 <= theta_deg < -55.0:
        return 225
    elif -55.0 <= theta_deg < -22.5:
        return 225
    return 45


def _adapter_settings(theta_deg: float, adapter_length: float) -> tuple[str, float, float, float]:
    theta_deg = (theta_deg + 180) % 360 - 180
    adapter_core_orientation = _adapter_core_orientation_learning(theta_deg)
    if -22.5 <= theta_deg < 22.5:
        # East clearance segment.
        return "east", adapter_core_orientation, adapter_length, adapter_length - 2
    elif 22.5 <= theta_deg < 67.5:
        # Northeast clearance segment, biased toward the east-facing spiral run.
        return "northeast", adapter_core_orientation, adapter_length + 4, adapter_length - 2
    elif 67.5 <= theta_deg < 80:
        # North approach segment before the vertical-clearance transition.
        return "north_approach", adapter_core_orientation, adapter_length + 8, adapter_length + 2
    elif 80 <= theta_deg < 112.5:
        # North vertical-clearance segment.
        return "north", adapter_core_orientation, adapter_length, adapter_length + 6
    elif 112.5 <= theta_deg < 120:
        # Northwest transition segment near the north bend.
        return "northwest_transition", adapter_core_orientation, adapter_length - 2, adapter_length + 2
    elif 120 <= theta_deg < 157.5:
        # Northwest clearance segment.
        return "northwest", adapter_core_orientation, adapter_length - 2, adapter_length
    elif 157.5 <= theta_deg < 180:
        # West clearance segment on the +180 boundary.
        return "west_pos", adapter_core_orientation, adapter_length + 2, adapter_length
    elif -180 <= theta_deg < -157.5:
        # West clearance segment on the -180 boundary.
        return "west_neg", adapter_core_orientation, adapter_length + 2, adapter_length
    elif -157.5 <= theta_deg < -112.5:
        # Southwest clearance segment.
        return "southwest", adapter_core_orientation, adapter_length + 6, adapter_length
    elif -112.5 <= theta_deg < -82.5:
        # South clearance segment.
        return "south", adapter_core_orientation, adapter_length + 2, adapter_length + 6
    elif -82.5 <= theta_deg < -55.0:
        # Southeast transition segment near the south bend.
        return "southeast_transition", adapter_core_orientation, adapter_length - 2, adapter_length + 2
    elif -55.0 <= theta_deg < -22.5:
        # Southeast clearance segment.
        return "southeast", adapter_core_orientation, adapter_length - 2, adapter_length
    return "northeast", adapter_core_orientation, adapter_length, adapter_length


def _adapter_path_from_port(
    port,
    length: float,
    width: float,
    core_overlap: float,
    layer: Layer,
    core_orientation: float,
    name: str,
) -> gf.Component:
    center = np.asarray(port.center, dtype=float)
    patch_angle = np.deg2rad(port.orientation)
    patch_direction = np.array([np.cos(patch_angle), np.sin(patch_angle)])
    orientation = (port.orientation + 180 - core_orientation) % 360
    adapter_angle = np.deg2rad(orientation)
    adapter_direction = np.array([np.cos(adapter_angle), np.sin(adapter_angle)])
    start = center - core_overlap * patch_direction
    end = center + length * adapter_direction

    points = [tuple(start), tuple(center), tuple(end)] if core_overlap else [tuple(center), tuple(end)]
    path = gf.Path(points)
    cross_section = gf.CrossSection(
        sections=(gf.Section(width=width, offset=0, layer=layer),)
    )
    c = gf.path.extrude(path, cross_section=cross_section)
    c.name = name
    c.add_port(
        "outer",
        center=tuple(end),
        orientation=orientation,
        width=width,
        layer=layer,
    )
    return c


def _JJ_feet(width: float, height: float, layer: Layer) -> gf.Component:
    c = gf.Component(name=f"jj_feet_W{width:g}_H{height:g}")
    pts = [
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    ]
    c.add_polygon(pts, layer=layer)
    c.add_port(
        "top_right", center=(width / 2 - 0.5, height / 2), orientation=90, width=1, layer=layer
    )
    c.add_port(
        "top_left", center=(-width / 2 + 0.5, height / 2), orientation=90, width=1, layer=layer
    )
    c.add_port(
        "bottom_right", center=(width / 2 - 0.5, -height / 2), orientation=270, width=1, layer=layer
    )
    c.add_port(
        "bottom_left", center=(-width / 2 + 0.5, -height / 2), orientation=270, width=1, layer=layer
    )
    return c


@gf.cell(check_instances=False)
def JJ1(
    width: float = 1.0,
    length: float = 8.0,
    feet_width_L: float = 6,
    feet_width_R: float = 6,
    feet_height: float = 3,
    extend_L: bool = False,
    extend_R: bool = False,
) -> gf.Component:
    c = gf.Component(name="jj1_legacy")

    if extend_L:
        JJ_1 = c << rectangle(width=width, height=length + 1, layer=LAYER.JJ)
        JJ_1.move((0, -((length + 1) / 2 - 2.5 - width / 2)))
    else:
        JJ_1 = c << rectangle(width=width, height=length, layer=LAYER.JJ)
        JJ_1.move((0, -(length / 2 - 2.5 - width / 2)))
    if extend_R:
        JJ_2 = c << rectangle(width=length + 1, height=width, layer=LAYER.JJ)
        JJ_2.move(((length + 1) / 2 - 2.5 - width / 2, 0))
    else:
        JJ_2 = c << rectangle(width=length, height=width, layer=LAYER.JJ)
        JJ_2.move((length / 2 - 2.5 - width / 2, 0))
    extend_1 = c << _JJ_feet(width=feet_width_R, height=feet_height, layer=LAYER.JJ)
    extend_2 = c << _JJ_feet(width=feet_width_L, height=feet_height, layer=LAYER.JJ)

    JJ_1.rotate(-45)
    JJ_2.rotate(-45)
    extend_1.connect("top_right", JJ_1.ports["bottom"])
    extend_2.connect("top_left", JJ_2.ports["right"])

    return c


@gf.cell(check_instances=False)
def JJ2(
    width: float = 1.0,
    length: float = 8.0,
    feet_width_L: float = 6,
    feet_width_R: float = 6,
    feet_height: float = 3,
    extend_L: bool = False,
    extend_R: bool = False,
):
    c = gf.Component(name="jj2_legacy")

    if extend_R:
        JJ_1 = c << rectangle(width=width, height=length + 1, layer=LAYER.JJ)
        JJ_1.move((0, -((length + 1) / 2 - 2.5 - width / 2)))
    else:
        JJ_1 = c << rectangle(width=width, height=length, layer=LAYER.JJ)
        JJ_1.move((0, -(length / 2 - 2.5 - width / 2)))
    if extend_L:
        JJ_2 = c << rectangle(width=length + 1, height=width, layer=LAYER.JJ)
        JJ_2.move((-((length + 1) / 2 - 2.5 - width / 2), 0))
    else:
        JJ_2 = c << rectangle(width=length, height=width, layer=LAYER.JJ)
        JJ_2.move((-(length / 2 - 2.5 - width / 2), 0))
    extend_1 = c << _JJ_feet(width=feet_width_R, height=feet_height, layer=LAYER.JJ)
    extend_2 = c << _JJ_feet(width=feet_width_L, height=feet_height, layer=LAYER.JJ)

    JJ_1.rotate(-45)
    JJ_2.rotate(-45)
    extend_1.connect("top_left", JJ_1.ports["bottom"])
    extend_2.connect("top_right", JJ_2.ports["left"])

    return c


@gf.cell(check_instances=False)
def create_jj_cross_princeton(
    jj_wid: float = 0.1,
    jj_len: float = 5,
    jj_arm_ext: float = 1,
    jj_shadow_len: float = 0.5,
    jj_arm_shadow_overlap: float = 0.1,
    comp_name: str = "jj_manha_princeton",
    layer_jj: Layer = LAYER.JJ,
    layer_jj_shadow: Layer = LAYER.JJ,
    layer_patches: Layer = LAYER.JJ,
    layer_patches_shadow: Layer = LAYER.JJ,
    merge_jj_and_patches: bool = True,
    pad_style: str = "rounded",
    square_size: float = 2.2,
    square_offset_x: float = 0.0,
    square_offset_y: float = 0.0,
    junction_arm_len_x: float = 0.0,
    junction_arm_len_y: float = 0.0,
    pad_connection_overlap: float = 0.75,
    square_connection_overlap: float = 0.15,
    initial_rotation: float = PRINCETON_JJ_INITIAL_ROTATION,
) -> gf.Component:
    """Creates the Princeton-style JJ cross.

    The source geometry distinguishes QEB main, shadow, patch, and patch shadow
    layers. This repo currently maps all four to ``LAYER.JJ``.
    """
    jj_arm1_wid = jj_wid + 0.02
    jj_arm1_len = jj_len

    jj_arm2_wid = jj_wid
    jj_arm2_len = jj_len

    jj_princeton = gf.Component(name=f"{comp_name}_core")
    jj_cross = gf.Component(name=f"{comp_name}_cross")
    jj_patches = gf.Component(name=f"{comp_name}_patch")
    jj_patches_shadow = gf.Component(name=f"{comp_name}_patch_shadow")
    jj_princeton_jj = gf.Component(name=f"{comp_name}_jj_body")
    jj_princeton_shadow = gf.Component(name=f"{comp_name}_shadow_body")

    jj_arm1_ref = jj_cross << gf.components.rectangle(size=(jj_arm1_wid, jj_arm1_len), layer=layer_jj)
    jj_arm2_ref = jj_cross << gf.components.rectangle(size=(jj_arm2_wid, jj_arm2_len), layer=layer_jj)
    jj_arm1_ref.rotate(angle=0)
    jj_arm1_ref.move((1, 0))

    jj_arm2_ref.rotate(angle=-90)
    jj_arm2_ref.move((0, 1 + jj_arm2_wid))

    for ref in [jj_arm1_ref, jj_arm2_ref]:
        ref.move((-jj_arm_ext - jj_arm1_wid / 2, -jj_arm_ext - jj_arm2_wid / 2))
        ref.rotate(angle=-45)

    jj_cross_ref = jj_princeton_jj << jj_cross
    jj_cross_ref.rotate(angle=135)

    patch_wid = 4/4
    patch_offset = 2
    patch_len = 6-2 + patch_offset
    patch_overlap = 0.6
    patch_shadow_wid = patch_wid + 1
    patch_shadow_len = patch_len + 1

    jj_patch_coord = np.array(
        [
            [-patch_wid / 2, -patch_len / 2],
            [patch_wid / 2, -patch_len / 2],
            [patch_wid / 2, patch_len / 2],
            [-patch_wid / 2, patch_len / 2],
        ]
    )
    jj_patch_shadow_coord = np.array(
        [
            [-patch_shadow_wid / 2, -patch_shadow_len / 2],
            [patch_shadow_wid / 2, -patch_shadow_len / 2],
            [patch_shadow_wid / 2, patch_shadow_len / 2],
            [-patch_shadow_wid / 2, patch_shadow_len / 2],
        ]
    )

    if pad_style not in {"rounded", "rectangle"}:
        raise ValueError(f"Unsupported pad_style: {pad_style}")

    jj_patches.add_polygon(jj_patch_coord, layer=layer_patches)
    jj_patches.add_port(
        "top",
        center=(0, patch_len / 2),
        orientation=90,
        width=patch_wid,
        layer=layer_patches,
    )
    jj_patches.add_port(
        "bottom",
        center=(0, -patch_len / 2),
        orientation=270,
        width=patch_wid,
        layer=layer_patches,
    )
    jj_patches_shadow.add_polygon(jj_patch_shadow_coord, layer=layer_patches_shadow)

    patch_offset = (jj_len - jj_arm_ext) / np.sqrt(2)

    jj_patch_ref1 = jj_princeton_jj << jj_patches
    jj_patch_ref1.move((patch_offset, patch_offset + patch_len / 2 - patch_overlap))
    jj_patch_ref1.rotate(angle=135)
    jj_patch_ref2 = jj_princeton_jj << jj_patches
    jj_patch_ref2.move((patch_offset, -patch_offset - patch_len / 2 + patch_overlap))
    jj_patch_ref2.rotate(angle=135)
    patch_1_port = _farthest_patch_port(jj_patch_ref1)
    patch_2_port = _farthest_patch_port(jj_patch_ref2)

    jj_square_corner_x = square_offset_x - jj_arm2_wid / 2 + junction_arm_len_x
    jj_square_corner_y = square_offset_y + jj_arm1_wid / 2 - junction_arm_len_y
    jj_square_right_x = jj_square_corner_x + square_size
    jj_square_bottom_y = jj_square_corner_y - square_size

    jj_clip_extent = jj_len + patch_len + square_size + 10
    jj_cross_clip_mask = gf.Component(name=f"{comp_name}_clip_mask")
    jj_cross_clip_mask.add_polygon(
        [
            (-jj_clip_extent, -jj_clip_extent),
            (jj_square_corner_x, -jj_clip_extent),
            (jj_square_corner_x, jj_square_bottom_y),
            (jj_square_right_x, jj_square_bottom_y),
            (jj_square_right_x, jj_square_corner_y),
            (jj_clip_extent, jj_square_corner_y),
            (jj_clip_extent, jj_clip_extent),
            (-jj_clip_extent, jj_clip_extent),
        ],
        layer=layer_jj,
    )
    jj_cross_clip_mask_ref = jj_princeton_jj << jj_cross_clip_mask
    jj_cross_clipped = gf.boolean(
        jj_cross_ref,
        jj_cross_clip_mask_ref,
        operation="and",
        layer=layer_jj,
    )
    jj_cross_clipped.name = f"{comp_name}_cross_clipped"

    if merge_jj_and_patches:
        jj_patches_for_merge = gf.Component(name=f"{comp_name}_patches_for_merge")
        jj_patch_merge_ref1 = jj_patches_for_merge << jj_patches
        jj_patch_merge_ref1.move((patch_offset, patch_offset + patch_len / 2 - patch_overlap))
        jj_patch_merge_ref1.rotate(angle=135)
        jj_patch_merge_ref2 = jj_patches_for_merge << jj_patches
        jj_patch_merge_ref2.move((patch_offset, -patch_offset - patch_len / 2 + patch_overlap))
        jj_patch_merge_ref2.rotate(angle=135)
        jj_cross_patch_merge = gf.boolean(
            jj_cross_clipped,
            jj_patches_for_merge,
            operation="or",
            layer=layer_jj,
        )
        jj_cross_patch_merge.name = f"{comp_name}_cross_patch_merge"
        jj_princeton_jj = jj_cross_patch_merge
    else:
        jj_cross_and_patches = gf.Component(name=f"{comp_name}_cross_and_patches")
        jj_cross_and_patches << jj_cross_clipped
        jj_patch_body_ref1 = jj_cross_and_patches << jj_patches
        jj_patch_body_ref1.move((patch_offset, patch_offset + patch_len / 2 - patch_overlap))
        jj_patch_body_ref1.rotate(angle=135)
        jj_patch_body_ref2 = jj_cross_and_patches << jj_patches
        jj_patch_body_ref2.move((patch_offset, -patch_offset - patch_len / 2 + patch_overlap))
        jj_patch_body_ref2.rotate(angle=135)
        jj_princeton_jj = jj_cross_and_patches

    jj_patches_shadow_ref1 = jj_princeton_shadow << jj_patches_shadow
    jj_patches_shadow_ref1.move((patch_offset, patch_offset + patch_len / 2 - patch_overlap))
    jj_patches_shadow_ref1.rotate(angle=135)
    jj_patches_shadow_ref2 = jj_princeton_shadow << jj_patches_shadow
    jj_patches_shadow_ref2.move((patch_offset, -patch_offset - patch_len / 2 + patch_overlap))
    jj_patches_shadow_ref2.rotate(angle=135)

    jj_princeton_jj_ref = jj_princeton << jj_princeton_jj
    jj_princeton << jj_princeton_shadow

    jj_square_center_x = jj_square_corner_x + square_size / 2
    jj_square_center_y = jj_square_corner_y - square_size / 2

    jj_square_ref = jj_princeton << gf.components.rectangle(
        size=(square_size, square_size),
        centered=True,
        layer=layer_jj,
    )
    jj_square_ref.move((jj_square_center_x, jj_square_center_y))

    if merge_jj_and_patches:
        jj_princeton_merge = gf.boolean(
            jj_princeton_jj_ref,
            jj_square_ref,
            operation="or",
            layer=layer_jj,
        )
        jj_princeton_merge.name = f"{comp_name}_princeton_merge"
        jj_princeton = gf.Component(name=f"{comp_name}_merged_core")
        jj_princeton << jj_princeton_shadow
        jj_princeton << jj_princeton_merge

    _add_port_from_port(jj_princeton, "patch_1", patch_1_port)
    _add_port_from_port(jj_princeton, "patch_2", patch_2_port)

    _ = (
        jj_shadow_len,
        jj_arm_shadow_overlap,
        layer_jj_shadow,
        pad_connection_overlap,
        square_connection_overlap,
    )

    if initial_rotation:
        oriented_jj = gf.Component(name=f"{comp_name}_oriented")
        jj_ref = oriented_jj << jj_princeton
        jj_ref.rotate(angle=initial_rotation)
        oriented_ports = {
            name: jj_ref.ports[name]
            for name in ("patch_1", "patch_2")
        }
        for name, port in oriented_ports.items():
            _add_port_from_port(oriented_jj, name, port)
        jj_princeton = oriented_jj

    return jj_princeton


@gf.cell(check_instances=False, set_name=False)
def _create_jj_cross_princeton_adaption(
    adapter_direction: str = "east",
    adapter_core_orientation: float = 135,
    adapter_1_length: float = 9.0,
    adapter_2_length: float = 9.0,
    adapter_width: float = 2.0,
    adapter_overlap: float = 0.2,
    layer_adapter: Layer = LAYER.JJ,
    core_rotation: float = 0.0,
) -> gf.Component:
    """Creates a fixed-orientation Princeton JJ core with connected adapter leads.

    The Princeton core remains at one process-friendly orientation. Adapter
    paths extend from the outer patch ports and can be parameterized.
    """
    c = gf.Component(
        name=(
            f"jj_princeton_adaption_{adapter_direction}_"
            f"L1_{adapter_1_length:g}_L2_{adapter_2_length:g}"
        )
    )
    core = create_jj_cross_princeton(initial_rotation=core_rotation)
    core_ref = c << core

    for index, patch_port_name in enumerate(("patch_1", "patch_2"), start=1):
        adapter_path_length = adapter_1_length if index == 1 else adapter_2_length
        lead_ref = c << _adapter_path_from_port(
            core_ref.ports[patch_port_name],
            length=adapter_path_length,
            width=adapter_width,
            core_overlap=adapter_overlap,
            layer=layer_adapter,
            core_orientation=adapter_core_orientation,
            name=(
                f"jj_adapter_{index}_path_{adapter_direction}_"
                f"port{core_ref.ports[patch_port_name].orientation:g}_"
                f"L{adapter_path_length:g}"
            ),
        )
        _add_port_from_port(c, f"adapter_{index}", lead_ref.ports["outer"])

    return c


def create_jj_cross_princeton_adaption(
    theta_deg: float = 0.0,
    adapter_length: float = 6.0,
    adapter_width: float = 2.0,
    adapter_core_overlap: float = 0.2,
    layer_adapter: Layer = LAYER.JJ,
    core_rotation: float = 0.0,
) -> gf.Component:
    adapter_direction, adapter_core_orientation, adapter_1_length, adapter_2_length = _adapter_settings(
        theta_deg,
        adapter_length,
    )
    return _create_jj_cross_princeton_adaption(
        adapter_direction=adapter_direction,
        adapter_core_orientation=adapter_core_orientation,
        adapter_1_length=adapter_1_length,
        adapter_2_length=adapter_2_length,
        adapter_width=adapter_width,
        adapter_overlap=adapter_core_overlap,
        layer_adapter=layer_adapter,
        core_rotation=core_rotation,
    )
