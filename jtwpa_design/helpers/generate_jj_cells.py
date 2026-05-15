import argparse
from collections.abc import Callable
from pathlib import Path

import gdsfactory as gf

from jtwpa_design.cells.components.JJ import (
    JJ1,
    JJ2,
    create_jj_cross_princeton,
    create_jj_cross_princeton_adaption,
)
from jtwpa_design.cells.components.text_id import text_id
from jtwpa_design.pdk import PDK


CellFactory = Callable[[], gf.Component]


JJ_CELLS: dict[str, CellFactory] = {
    "jj1": JJ1,
    "jj2": JJ2,
    "princeton": create_jj_cross_princeton,
    "princeton_no_merge": lambda: create_jj_cross_princeton(
        merge_jj_and_patches=False,
        pad_style="rectangle",
    ),
    "princeton_adaption": lambda: create_jj_cross_princeton_adaption(theta_deg=45),
}


def create_jj_cells_top(spacing: float = 40.0) -> gf.Component:
    top = gf.Component("jj_cells_top")

    x = 0.0
    for name, factory in JJ_CELLS.items():
        component = factory()
        ref = top << component
        ref.dmovex(x - ref.dxmin)
        ref.dmovey(-ref.dymin)

        label = top << text_id(id=name, text_size=3, margin=0.5)
        label.dmovex(x - label.dxmin)
        label.dmovey(ref.dymax + 5 - label.dymin)

        x = ref.dxmax + spacing

    return top


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a top cell containing all allowed JJ cells.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "build" / "jj_cells",
        help="Output directory for the generated GDS file.",
    )
    parser.add_argument(
        "--spacing",
        type=float,
        default=40.0,
        help="Horizontal spacing between JJ cell examples.",
    )
    args = parser.parse_args()

    PDK.activate()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    top = create_jj_cells_top(spacing=args.spacing)
    out_path = args.out_dir / "jj_cells_top.gds"
    top.write_gds(out_path)
    print(f"Generated JJ top cell: {out_path}")


if __name__ == "__main__":
    main()
