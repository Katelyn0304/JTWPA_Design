import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from jtwpa_design.cells.chips.spiral import spiral_chip
from jtwpa_design.parameters.chips.spiral import SpiralChipParams
from jtwpa_design.pdk import PDK


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a single spiral chip GDS.")
    parser.add_argument("--chip-id", default="C01", help="Chip ID label to place on the chip.")
    parser.add_argument("--wafer-id", default="W01", help="Wafer ID label to place on the chip.")
    parser.add_argument(
        "--junction-style",
        choices=["legacy", "princeton", "princeton_adaption"],
        default="princeton",
        help="Junction style to use in the spiral chip.",
    )
    parser.add_argument(
        "--include-dicing",
        action="store_true",
        help="Include the six_mm_chip_dicing.gds asset if it exists.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "build" / "spiral_chip",
        help="Output directory for the generated GDS file.",
    )
    args = parser.parse_args()

    PDK.activate()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    params = SpiralChipParams().model_copy(
        update={
            "chip_id": args.chip_id,
            "wafer_id": args.wafer_id,
            "include_dicing": args.include_dicing,
        }
    )
    component = spiral_chip(params=params, junction_style=args.junction_style)
    out_path = args.out_dir / f"spiral_chip_{args.wafer_id}_{args.chip_id}_{args.junction_style}.gds"
    component.write_gds(out_path)
    print(f"Generated spiral chip: {out_path}")


if __name__ == "__main__":
    main()
