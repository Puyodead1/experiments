from pathlib import Path
import argparse


def main(file: Path):
    if not file.exists():
        print(f"File {file} does not exist.")
        return

    with file.open("rb") as f:
        data = f.read()

        # byteswap every 2 bytes
        swapped_data = bytearray()
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                swapped_data.append(data[i + 1])
            swapped_data.append(data[i])

        output_file = file.with_name(file.stem + "_swapped" + file.suffix)
        with output_file.open("wb") as out_f:
            out_f.write(swapped_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Byteswap a file")
    parser.add_argument("file", type=Path, help="The file to byteswap")
    args = parser.parse_args()
    main(args.file)
