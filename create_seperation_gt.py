from collections import Counter, defaultdict
from pathlib import Path

import imagesize

from utils.copy_utils import copy_mode
from utils.input_utils import get_file_paths, supported_image_formats
from utils.path_utils import image_path_to_xml_path


def get_arguments():
    import argparse

    parser = argparse.ArgumentParser(description="Create seperation ground truth")
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-i", "--input", help="Train input folder/file", nargs="+", action="extend", type=str, required=True)
    io_args.add_argument("-o", "--output", help="Output folder", type=str)

    args = parser.parse_args()
    return args


def main(args):
    input_paths = get_file_paths(args.input, supported_image_formats, disable_check=True)

    separated_documents = defaultdict(list)

    input_path_i = input_paths[0]

    current_document = input_path_i.name
    size_i = imagesize.get(input_path_i)
    separated_documents[current_document].append(input_path_i)

    for input_path_j in input_paths[1:]:
        if input_path_i.parent != input_path_j.parent:
            current_document = input_path_j.name
        else:
            size_j = imagesize.get(input_path_j)
            if size_i != size_j:
                current_document = input_path_j.name

        separated_documents[current_document].append(input_path_j)

    count_documents = len(separated_documents)
    print(f"Found {count_documents} documents")
    count_lengths = Counter([len(images) for images in separated_documents.values()])
    print(f"Found {dict(count_lengths)} documents with the given number of images")

    if args.output:
        output_path = Path(args.output)
        for document_name, document_images in separated_documents.items():
            document_dir = output_path.joinpath(document_name)
            document_dir.mkdir(parents=True, exist_ok=True)

            for image_path in document_images:
                output_image_path = document_dir.joinpath(image_path.name)
                copy_mode(image_path, output_image_path, mode="symlink")

                xml_path = image_path_to_xml_path(image_path, check=False)
                if xml_path.exists():
                    document_page_dir = document_dir.joinpath("page")
                    document_page_dir.mkdir(parents=True, exist_ok=True)
                    output_xml_path = document_page_dir.joinpath(xml_path.name)
                    copy_mode(xml_path, output_xml_path, mode="symlink")


if __name__ == "__main__":
    args = get_arguments()
    main(args)
