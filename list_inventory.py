import logging
import random
from pathlib import Path

from utils.input_utils import get_file_paths, supported_image_formats


def get_arguments():
    import argparse

    parser = argparse.ArgumentParser(description="Create separation ground truth")
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-i", "--input", help="Train input folder/file", nargs="+", action="extend", type=str, required=True)
    io_args.add_argument("-o", "--output", required=True, help="Output folder", type=str)

    args = parser.parse_args()
    return args


def main(args):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    input_dirs = [Path(input_dir) for input_dir in args.input]

    assert all([input_dir.is_dir() for input_dir in input_dirs]), "All input paths must be directories"

    output_path = Path(args.output)
    assert output_path.suffix == ".txt", "Output path must be a text file"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = {}
    for input_dir in input_dirs:
        inventory_dirs = [path for path in input_dir.iterdir() if path.is_dir()]
        for inventory_dir in inventory_dirs:
            image_paths = get_file_paths(inventory_dir, supported_image_formats, disable_check=True)
            if inventory_dir.name in total:
                raise ValueError(f"Duplicate inventory directory name: {inventory_dir.name}")

            total.update({inventory_dir.name: len(image_paths)})
            if not image_paths:
                logger.warning(f"No images found in {inventory_dir}")
                continue
            else:
                logger.info(f"Found {len(image_paths)} images in {inventory_dir}")

    with open(output_path, "w") as output_file:
        inventory_dirs = list(total.keys())
        random.shuffle(inventory_dirs)
        for inventory_dir in inventory_dirs:
            output_file.write(f"{inventory_dir.name}\n")

    logger.info(f"Total images found: {sum(total.values())}")
    logger.info(f"Max images found: {max(total.values())}")
    logger.info(f"Min images found: {min(total.values())}")


if __name__ == "__main__":
    args = get_arguments()
    main(args)
