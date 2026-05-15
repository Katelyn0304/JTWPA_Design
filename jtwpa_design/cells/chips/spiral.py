from typing import Literal
from pathlib import Path

import gdsfactory as gf
import numpy as np
from gdsfactory.cross_section import ComponentAlongPath

from jtwpa_design.builders.components.open_stub_capacitor import make_open_stub_capacitor
from jtwpa_design.builders.components.twpa_launcher import make_twpa_launcher
from jtwpa_design.cells.components.JJ import (
    JJ1,
    JJ2,
    create_jj_cross_princeton,
    create_jj_cross_princeton_adaption,
)
from jtwpa_design.cells.components.marker import four_marker
from jtwpa_design.cells.components.rectangle import rectangle
from jtwpa_design.cells.components.text_id import text_id
from jtwpa_design.cells.paths.jtwpa_path import jtwpa_path
from jtwpa_design.helpers.generate_bridge_paths import create_bridge_paths
from jtwpa_design.helpers.tukey_window import tukey_window
from jtwpa_design.parameters.assemblies.jtwpa_line import JTWPALineParams
from jtwpa_design.parameters.chips.spiral import SpiralChipParams
from jtwpa_design.parameters.components.open_stub_capacitor import OpenStubCapacitorParams
from jtwpa_design.parameters.rules import LayoutRules
from jtwpa_design.tech import LAYER

JunctionStyle = Literal["legacy", "princeton", "princeton_adaption"]


def _junction(
    junction_style: JunctionStyle,
    theta_deg: float,
    legacy_factory,
    **legacy_kwargs,
) -> gf.Component:
    if junction_style == "princeton_adaption":
        return create_jj_cross_princeton_adaption(theta_deg=theta_deg)
    if junction_style == "princeton":
        return create_jj_cross_princeton()
    if junction_style == "legacy":
        return legacy_factory(**legacy_kwargs)
    raise ValueError(f"Unsupported junction_style: {junction_style}")


def _junction_rotation(junction_style: JunctionStyle) -> float:
    if junction_style == "princeton_adaption":
        return -15+45
    if junction_style == "princeton":
        return -15
    if junction_style == "legacy":
        return -15
    raise ValueError(f"Unsupported junction_style: {junction_style}")


def _orient_junction_ref(ref, junction_style: JunctionStyle, theta_deg: float) -> None:
    ref.rotate(_junction_rotation(junction_style))
    _ = theta_deg


@gf.cell(check_instances=False)
def capacitors_JJs(
    rules: LayoutRules = LayoutRules(),
    base_capacitor: OpenStubCapacitorParams = OpenStubCapacitorParams(),
    junction_style: JunctionStyle = "princeton",
) -> gf.Component:
    capacitor_points = np.load(
        "jtwpa_design/cells/chips/npy/arranged_capacitor_points.npy", allow_pickle=False
    )
    JJ_arch_spiral = np.load("jtwpa_design/cells/chips/npy/JJ_arch_spiral.npy", allow_pickle=False)
    JJ_arc1 = np.load("jtwpa_design/cells/chips/npy/JJ_arc1.npy", allow_pickle=False)
    JJ_arc2 = np.load("jtwpa_design/cells/chips/npy/JJ_arc2.npy", allow_pickle=False)
    c = gf.Component()

    num_of_capacitors = len(capacitor_points)

    boundary_capacitor_params = base_capacitor.model_copy(
        update={"length": base_capacitor.length / 2, "general": False}
    )
    first_capacitor = c << make_open_stub_capacitor(params=boundary_capacitor_params, rules=rules)
    first_capacitor.rotate(-capacitor_points[0][2])
    first_capacitor.move((capacitor_points[0][0], capacitor_points[0][1]))
    final_capacitor = c << make_open_stub_capacitor(params=boundary_capacitor_params, rules=rules)
    final_capacitor.rotate(-capacitor_points[num_of_capacitors - 1][2])
    final_capacitor.move(
        (capacitor_points[num_of_capacitors - 1][0], capacitor_points[num_of_capacitors - 1][1])
    )

    for i in range(1, num_of_capacitors - 1):
        W = tukey_window(i, num_of_capacitors - 2, alpha=0.5)
        phase = np.cos(2 * np.pi * (i - 0.5) / 30)
        i_capacitor_length = base_capacitor.length * (1 + 0.08 * W * phase) ** (-2)
        i_capacitor_params = base_capacitor.model_copy(
            update={"i": i - 1, "length": i_capacitor_length}
        )
        cx = capacitor_points[i][0]
        cy = capacitor_points[i][1]
        if 1 <= i <= 1122:
            i_capacitor = c << make_open_stub_capacitor(params=i_capacitor_params, rules=rules)
            i_capacitor.rotate(-capacitor_points[i][2])
            i_capacitor.move((cx, cy))
        elif 1123 <= i <= 1200:
            i_capacitor = c << make_open_stub_capacitor(params=i_capacitor_params, rules=rules)
            i_capacitor.rotate(-np.degrees(np.arctan2(cx, cy - 500)))
            i_capacitor.move((cx, cy))
        elif 1201 <= i <= 1279:
            i_capacitor = c << make_open_stub_capacitor(params=i_capacitor_params, rules=rules)
            theta_deg = np.degrees(np.arctan2(cx, cy + 500))
            if -10 < cx < 10 and -10 < cy < 10:
                theta_deg = 2
            i_capacitor.rotate(-theta_deg)
            i_capacitor.move((cx, cy))
        else:
            i_capacitor = c << make_open_stub_capacitor(params=i_capacitor_params, rules=rules)
            i_capacitor.rotate(-capacitor_points[i][2])
            i_capacitor.move((cx, cy))

    for cx, cy in JJ_arch_spiral:
        theta_deg = np.degrees(np.arctan2(cy, cx))
        if -1757 < cx < -1755 and -1545 < cy < -1543:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=8, extend_R=True)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 1747 < cx < 1749 and 1554 < cy < 1556:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=10)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 75 <= abs(theta_deg) <= 105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 60 <= theta_deg < 75 or -120 <= theta_deg < -105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 30 <= theta_deg < 60 or -150 <= theta_deg < -120:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=10, extend_R=True)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 105 < theta_deg <= 120 or -75 < theta_deg <= -60:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=10)
            JJ_ref.move((-1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif abs(theta_deg) <= 15 or abs(theta_deg) >= 165:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 150 <= theta_deg < 165 or -30 <= theta_deg < -15:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 120 < theta_deg < 150 or -60 < theta_deg < -30:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=10, extend_R=True)
            JJ_ref.move((1, -1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 15 < theta_deg <= 30 or -165 < theta_deg <= -150:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_R=10)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        else:
            continue
        JJ_ref.move((cx, cy))
    for cx, cy in JJ_arc1:
        theta_deg = np.degrees(np.arctan2(cy - 500, cx))
        if 75 <= abs(theta_deg) <= 105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 60 <= theta_deg < 75 or -120 <= theta_deg < -105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 30 <= theta_deg < 60 or -150 <= theta_deg < -120:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=10, extend_R=True)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 105 < theta_deg <= 120 or -75 < theta_deg <= -60:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=10)
            JJ_ref.move((-1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif abs(theta_deg) <= 15 or abs(theta_deg) >= 165:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 150 <= theta_deg < 165 or -30 <= theta_deg < -15:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 120 < theta_deg < 150 or -60 < theta_deg < -30:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=10, extend_R=True)
            JJ_ref.move((1, -1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 15 < theta_deg <= 30 or -165 < theta_deg <= -150:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_R=10)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        else:
            continue
        JJ_ref.move((cx, cy))
    for cx, cy in JJ_arc2:
        theta_deg = np.degrees(np.arctan2(cy + 500, cx))
        if 75 <= abs(theta_deg) <= 105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 60 <= theta_deg < 75 or -120 <= theta_deg < -105:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 30 <= theta_deg < 60 or -150 <= theta_deg < -120:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_R=10, extend_R=True)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 105 < theta_deg <= 120 or -75 < theta_deg <= -60:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ1, feet_width_L=10)
            JJ_ref.move((-1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif abs(theta_deg) <= 15 or abs(theta_deg) >= 165:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8, feet_width_R=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 150 <= theta_deg < 165 or -30 <= theta_deg < -15:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=8)
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 120 < theta_deg < 150 or -60 < theta_deg < -30:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_L=10, extend_R=True)
            JJ_ref.move((1, -1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        elif 15 < theta_deg <= 30 or -165 < theta_deg <= -150:
            JJ_ref = c << _junction(junction_style, theta_deg, JJ2, feet_width_R=10)
            JJ_ref.move((1, 1))
            _orient_junction_ref(JJ_ref, junction_style, theta_deg)
        else:
            continue
        JJ_ref.move((cx, cy))

    c.add_port("center", center=(0, 0), orientation=0, width=1, layer=LAYER.GROUND_MASK)

    return c


@gf.cell()
def JJ_ground_mask(rules: LayoutRules = LayoutRules()) -> gf.Component:
    p = jtwpa_path()
    mask_section = gf.Section(
        width=rules.jj_ground_mask.width, offset=0, layer=LAYER.GROUND_MASK, port_names=("o1", "o2")
    )
    x = gf.CrossSection(sections=(mask_section,))
    c = gf.path.extrude(p, cross_section=x)
    c.add_port("center", center=(0, 0), orientation=180, width=1, layer=LAYER.GROUND_MASK)
    return c


@gf.cell()
def bridge_on_cpw(rules: LayoutRules = LayoutRules()) -> gf.Component:
    c = gf.Component()
    pier_radius = rules.bridge.pier_radius
    bridge_width = rules.bridge.width
    pier_ground_edge = rules.bridge.pier_ground_edge_clearance
    cpw_width = rules.cpw.width
    cpw_gap = rules.cpw.gap
    pier1 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
    pier1.movey(cpw_width / 2 + cpw_gap + pier_radius + pier_ground_edge)
    pier2 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
    pier2.movey(-(cpw_width / 2 + cpw_gap + pier_radius + pier_ground_edge))
    c << rectangle(
        width=bridge_width,
        height=cpw_width
        + 2 * cpw_gap
        + 2 * pier_ground_edge
        + 4 * pier_radius
        + (bridge_width - 2 * pier_radius),
        layer=LAYER.AIR_BRIDGE,
    )
    return c


@gf.cell()
def twpa_cpw(rules: LayoutRules = LayoutRules()) -> gf.Component:
    via = ComponentAlongPath(
        component=bridge_on_cpw(rules=rules),
        spacing=200,
        padding=100,
        offset=0,
    )
    r = 100
    p = gf.path.arc(radius=1250, angle=-12.5)
    p += gf.path.straight(length=184.827 - r)
    p += gf.path.arc(radius=r, angle=90)
    # p += gf.path.straight(length=50)
    cpw_width = rules.cpw.width
    cpw_gap = rules.cpw.gap
    s0 = gf.Section(width=cpw_width, offset=0, layer=LAYER.MAIN_METAL)
    s1 = gf.Section(
        width=cpw_width + 2 * cpw_gap, offset=0, layer=LAYER.GROUND_MASK, port_names=("o1", "o2")
    )
    x = gf.CrossSection(sections=(s0, s1), components_along_path=(via,))
    c = gf.path.extrude(p, cross_section=x)
    for index, inst in enumerate(c.insts, start=1):
        if inst.cell.name.startswith("Unnamed"):
            inst.cell.name = f"twpa_cpw_bridge_placements_{index}"
    return c


def spiral_bridges(rules: LayoutRules = LayoutRules()):
    capacitor_points = np.load(
        "jtwpa_design/cells/chips/npy/arranged_capacitor_points.npy", allow_pickle=False
    )
    path1, path2 = create_bridge_paths(capacitor_points)
    s = gf.Section(width=rules.bridge.width, offset=0, layer=LAYER.AIR_BRIDGE)
    x = gf.CrossSection(sections=(s,))
    bridge1 = gf.path.extrude(path1, cross_section=x)
    bridge1.name = "spiral_bridge_path_1"
    bridge1.add_port("center", center=(0, 0), orientation=90, width=1, layer=LAYER.GROUND_MASK)
    bridge2 = gf.path.extrude(path2, cross_section=x)
    bridge2.name = "spiral_bridge_path_2"
    bridge2.add_port("center", center=(0, 0), orientation=90, width=1, layer=LAYER.GROUND_MASK)
    return bridge1, bridge2


@gf.cell(check_instances=False)
def jtwpa_line(
    params: JTWPALineParams = JTWPALineParams(),
    rules: LayoutRules = LayoutRules(),
    junction_style: JunctionStyle = "princeton",
) -> gf.Component:
    c = gf.Component()
    c_J = c << capacitors_JJs(
        rules=rules,
        base_capacitor=params.capacitor,
        junction_style=junction_style,
    )
    JJ_ground_mask_ref = c << JJ_ground_mask(rules=rules)
    JJ_ground_mask_ref.connect("center", c_J.ports["center"])
    cpw_1 = c << twpa_cpw(rules=rules)
    cpw_1.rotate(132.5)
    cpw_1.move((-1764, -1536.85))
    cpw_2 = c << twpa_cpw(rules=rules)
    cpw_2.rotate(-47.5)
    cpw_2.move((1756.15, 1547.4))
    launcher_1 = c << make_twpa_launcher(params=params.launcher, rules=rules)
    launcher_1.connect("right", cpw_1.ports["o2"], allow_layer_mismatch=True)
    launcher_2 = c << make_twpa_launcher(params=params.launcher, rules=rules)
    launcher_2.connect("right", cpw_2.ports["o2"], allow_layer_mismatch=True)
    pier_radius = rules.bridge.pier_radius
    pier_center_1 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
    pier_center_1.move((-14.48, -15.11))
    pier_center_2 = c << gf.components.circle(radius=pier_radius, layer=LAYER.AIR_BRIDGE_CONTACT)
    pier_center_2.move((-13.63, 26.86))
    spiral_bridge_1, spiral_bridge_2 = spiral_bridges(rules=rules)
    bridge_region_source = gf.Component(name="spiral_bridge_region_source")
    bridge_region_source << spiral_bridge_1
    bridge_region_source << spiral_bridge_2
    bridge_region = bridge_region_source.get_region(layer=LAYER.AIR_BRIDGE, merge=True)
    c.add_polygon(bridge_region, layer=LAYER.AIR_BRIDGE)
    c.add_port("center", center=(c.x, c.y), orientation=30, width=1, layer=LAYER.GROUND_MASK)
    return c


def _unprocessed_ground(size: float = 5900):
    c = gf.Component(name=f"unprocessed_ground_S{size:g}")
    c << rectangle(width=size, height=size, layer=LAYER.GROUND_MASK)
    c.add_port("center", center=(0, 0), orientation=180, width=1, layer=LAYER.GROUND_MASK)
    return c


@gf.cell(check_instances=False)
def spiral_chip(
    params: SpiralChipParams = SpiralChipParams(),
    rules: LayoutRules = LayoutRules(),
    junction_style: JunctionStyle = "princeton",
) -> gf.Component:
    c = gf.Component()
    jtwpa_line_ref = c << jtwpa_line(
        params=params.line,
        rules=rules,
        junction_style=junction_style,
    )
    marker_coordinate = params.marker_coordinate
    marker_size = params.marker.size
    marker_width = params.marker.width
    marker_boundary = params.marker.boundary
    wafer_id = c << text_id(
        id=params.wafer_id,
        text_size=params.label.text_size,
        margin=params.label.text_margin,
    )
    wafer_id.move((-marker_coordinate, marker_coordinate))
    chip_id = c << text_id(
        id=params.chip_id,
        text_size=params.label.text_size,
        margin=params.label.text_margin,
    )
    chip_id.move((marker_coordinate, -marker_coordinate))
    marker_1 = c << four_marker(size=marker_size, width=marker_width, boundary=marker_boundary)
    marker_1.move((-marker_coordinate, -marker_coordinate))
    marker_2 = c << four_marker(size=marker_size, width=marker_width, boundary=marker_boundary)
    marker_2.move((marker_coordinate, marker_coordinate))
    unprocessed_ground = _unprocessed_ground(size=params.frame.size - params.dicing.width)
    dicing_path = Path("jtwpa_design/cells/chips/gds_components/six_mm_chip_dicing.gds")
    if params.include_dicing and dicing_path.exists():
        c << gf.import_gds(dicing_path)
    jtwpa_line_ref.connect("center", unprocessed_ground.ports["center"])
    ground = gf.boolean(
        A=unprocessed_ground,
        B=c,
        operation="not",
        layer1=LAYER.GROUND_MASK,
        layer2=LAYER.GROUND_MASK,
        layer=LAYER.MAIN_METAL,
    )
    ground.name = "spiral_chip_ground"
    c.add_ref(ground)
    return c
