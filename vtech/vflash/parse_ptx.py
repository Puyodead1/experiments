import struct
from binary_reader import BinaryReader, Endian
from PIL import Image

WIDTH = 256
HEIGHT = 512


def swap16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]


def rgb15_to_rgb(rgb15_val):
    # Extract 5 bits for each channel (assuming RRRRRGGGGGBBBBB format)
    r = (rgb15_val >> 10) & 0x1F
    g = (rgb15_val >> 5) & 0x1F
    b = rgb15_val & 0x1F

    # Scale 5-bit (0-31) to 8-bit (0-255)
    # Multiplying by 8 (or shifting left by 3) is the simplest method
    r_8 = (r * 255) // 31
    g_8 = (g * 255) // 31
    b_8 = (b * 255) // 31

    return (r_8, g_8, b_8)


with open(
    "CARS.PTX",
    "rb",
) as f:
    reader = BinaryReader(f.read())

    header = reader.read_bytes(44)

    image = Image.new("RGB", (WIDTH, HEIGHT))

    for x in range(WIDTH):
        for y in range(HEIGHT):
            rgb15_val = reader.read_uint16()
            r, g, b = rgb15_to_rgb(rgb15_val)

            print(f"Pixel ({x}, {y}): R={r}, G={g}, B={b}")

            image.putpixel((x, y), (r, g, b))

    image.show()
