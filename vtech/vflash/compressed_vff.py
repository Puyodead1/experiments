import argparse
from pathlib import Path
from binary_reader import BinaryReader
from decompress import decompress


def main(file: Path):
    with file.open("rb") as f:
        data = f.read()
    total_size = len(data)
    print(f"Attemping to decompress {file.name} ({total_size} bytes)")
    reader = BinaryReader(data)

    decompressed_size = reader.read_uint32()
    unk1 = reader.read_uint32()
    unk2 = reader.read_uint32()
    unk3 = reader.read_uint32()
    print(f"Total size: {total_size} bytes")
    print(f"Decompressed size: {decompressed_size} bytes")
    print(f"unk1: {unk1:#010x}  ({unk1})")
    print(f"unk2: {unk2:#010x}  ({unk2})")
    print(f"unk3: {unk3:#010x}  ({unk3})")

    compressed_data = reader.read_bytes(total_size - 16)

    data_in = compressed_data[2:]

    decompress(compressed_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a compressed VFF file.")
    parser.add_argument("file", type=Path, help="Path to the compressed VFF file")
    args = parser.parse_args()

    main(args.file)
    print()
