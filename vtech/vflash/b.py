from pathlib import Path
from binreader import BinaryReader

# glob on all ptx files
for ptx_file in Path.cwd().glob("*.PTX"):
    print(f"Found PTX file: {ptx_file.name}")
    with ptx_file.open("rb") as f:
        reader = BinaryReader(f)

        magic = reader.read(8)
        assert magic == b",\x00\x00\x00\x00\x00\xe0\x01", f"Invalid magic: {magic}"

        unk1 = reader.read_uint16()
        unk2 = reader.read_uint16()
        print(f"\tunk1: {unk1:#06x}  ({unk1})")
        print(f"\tunk2: {unk2:#06x}  ({unk2})")
