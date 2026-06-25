import argparse
import sys
from PIL import Image
from binreader import BinaryReader
from pathlib import Path
from dataclasses import dataclass
from pprint import pformat


@dataclass
class Header:
    header_size: int
    x: int
    y: int
    width: int
    height: int
    bpp: int
    unk3: int
    unk4: int
    palette_size: int
    unk5: int
    unk6: int
    width2: int
    height2: int
    bitmap_size: int
    unk7: int

    @classmethod
    def from_reader(cls, r: BinaryReader):
        header_size = r.read_uint16()
        x = r.read_uint32()
        y = r.read_uint16()
        width = r.read_uint16()
        height = r.read_uint16()
        bpp = r.read_uint16()
        unk3 = r.read_uint32()
        unk4 = r.read_uint32()
        palette_size = r.read_uint16()
        unk5 = r.read_uint32()
        unk6 = r.read_uint32()
        width2 = r.read_uint16()
        height2 = r.read_uint16()
        bitmap_size = r.read_uint32()
        unk7 = r.read_uint32()

        return cls(header_size, x, y, width, height, bpp, unk3, unk4, palette_size, unk5, unk6, width2, height2, bitmap_size, unk7)

    def __repr__(self):
        return (
            "Header("
            f"header_size={self.header_size}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"width={self.width}, "
            f"height={self.height}, "
            f"bpp={self.bpp}, "
            f"palette_size={self.palette_size}, "
            f"bitmap_size={self.bitmap_size}"
            ")"
        )

    def __str__(self):
        return self.__repr__()

@dataclass
class PTX:
    header: Header
    bitmap_data: bytes
    palette_data: bytes

    @classmethod
    def from_file(cls, file: Path):
        with file.open('rb') as f:
            r = BinaryReader(f)
            header = Header.from_reader(r)

            assert r.tell() == header.header_size, f"Header size mismatch: {r.tell()} != {header.header_size}"

            bitmap_data = r.read(header.bitmap_size)
            palette_data = r.read(header.palette_size * 2)

            return cls(header, bitmap_data, palette_data)

    def __repr__(self):
        return (
            "PTX(\n"
            f"    header={pformat(self.header)},\n"
            f"    bitmap_data_length={len(self.bitmap_data)},\n"
            f"    palette_data_length={len(self.palette_data)}\n"
            ")"
        )

    def __str__(self):
        return self.__repr__()

def rgb555_to_rgb(v):
    r = ((v >> 10) & 0x1F) * 255 // 31
    g = ((v >> 5)  & 0x1F) * 255 // 31
    b = (v & 0x1F) * 255 // 31
    return (r, g, b)

def convert_palette(data: bytes):
    palette = []
    for i in range(0, len(data), 2):
        v = int.from_bytes(data[i:i+2], "little")
        palette.extend(rgb555_to_rgb(v))
    return palette


def parse_8bit(ptx: PTX) -> Image.Image:
    rgb_palette = convert_palette(ptx.palette_data)

    img = Image.new("P", (ptx.header.width, ptx.header.height))
    img.putdata(ptx.bitmap_data)

    img.putpalette(rgb_palette)

    return img


def parse_16bit(ptx: PTX) -> Image.Image:
    img = Image.new("RGB", (ptx.header.width, ptx.header.height))
    pixels = []

    for i in range(0, len(ptx.bitmap_data), 2):
        v = int.from_bytes(ptx.bitmap_data[i:i+2], "little")
        pixels.append(rgb555_to_rgb(v))

    img.putdata(pixels)

    return img


def main(file: Path, show: bool = False, save: bool = False):
    ptx = PTX.from_file(file)
    print(ptx)

    img: Image.Image = None

    if ptx.header.bpp == 8:
        img = parse_8bit(ptx)
    elif ptx.header.bpp == 16:
        img = parse_16bit(ptx)
    else:
        raise ValueError(f"Unsupported BPP: {ptx.header.bpp}")

    if img:
        if save:
            output_file = file.with_suffix(".png")
            img.save(output_file)
        if show:
            img.show()
    else:
        print("Failed to create image.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PTX palette to PNG")
    parser.add_argument("file", type=Path, help="Input PTX file")
    parser.add_argument("--show", action="store_true", help="Show the image after conversion")
    parser.add_argument("--save", action="store_true", help="Save the image")

    args = parser.parse_args()
    file: Path = args.file

    if not file.exists():
        print(f"Input file does not exist.")
        sys.exit(1)

    main(**vars(args))