# Puyodead1
#
# GPLv3 License
#
# This file parses and converts the MJP file format used in the vtech V.Flash system
#
# The MJP File format is like a normal MJPG (Motion JPEG) file, but with a custom header and FourCC chunks
# The video chunks are standard JPEG frames but only contain changed data from the previous frame


from io import BytesIO
from binary_reader import BinaryReader
from pathlib import Path
import argparse
from PIL import Image, ImageFile
from io import BytesIO

MJP_MAGIC = b"MIAV"
VIDEO_CHUNK_MAGIC = bytes.fromhex("30306463")  # 00dc - Video
AUDIO_1_CHUNK_MAGIC = bytes.fromhex("30317762")  # 01wb - Audio 1
AUDIO_2_CHUNK_MAGIC = bytes.fromhex("30327762")  # 02wb - Audio 2

OUTPUT_DIR = Path("output")

VIDEO_FRAME_HEADER = None


def fix_jpeg_byte_stuffing(jpeg_data: bytes) -> bytes:
    """
    Some non-standard encoders omit the 0x00 stuffing byte after 0xFF in the
    entropy stream. Standard JPEG decoders (including PIL) fail on bare 0xFF bytes.
    This adds the missing stuffing so decoders treat them as data, not markers.
    """
    # Find the SOS marker to locate where entropy data begins
    i = 0
    entropy_start = None
    while i < len(jpeg_data) - 1:
        if jpeg_data[i] == 0xFF and jpeg_data[i + 1] == 0xDA:
            sos_len = int.from_bytes(jpeg_data[i + 2 : i + 4], "big")
            entropy_start = i + 2 + sos_len
            break
        i += 1

    if entropy_start is None:
        return jpeg_data  # no SOS found, return as-is

    result = bytearray(jpeg_data[:entropy_start])

    j = entropy_start
    while j < len(jpeg_data):
        b = jpeg_data[j]
        if b == 0xFF and j + 1 < len(jpeg_data):
            next_b = jpeg_data[j + 1]
            if next_b == 0x00:
                # Already correctly stuffed
                result.append(0xFF)
                result.append(0x00)
                j += 2
            elif 0xD0 <= next_b <= 0xD7:
                # RST0-7 markers are valid inside entropy, pass through
                result.append(0xFF)
                result.append(next_b)
                j += 2
            elif next_b == 0xD9:
                # EOI - end of entropy stream
                result.append(0xFF)
                result.append(0xD9)
                result.extend(jpeg_data[j + 2 :])
                return bytes(result)
            else:
                # Bare 0xFF with no stuffing — insert 0x00
                result.append(0xFF)
                result.append(0x00)
                j += 1  # reprocess next_b as normal data byte
        else:
            result.append(b)
            j += 1

    return bytes(result)


def byte_swap(data: bytes) -> bytes:
    swapped_data = bytearray()
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            swapped_data.append(data[i + 1])
        swapped_data.append(data[i])

    return swapped_data


def bytes_find_all(data: bytes, sub: bytes) -> list[int]:
    """Find all occurrences of a byte sequence in a byte array."""
    indices = []
    start = 0
    while True:
        index = data.find(sub, start)
        if index == -1:
            break
        indices.append(index)
        start = index + 1
    return indices


def extract_jpeg_header(jpeg_data: bytes) -> bytes:
    """
    Extract everything from SOI up to (but not including) the SOS marker (0xFFDA).
    This includes DQT (quantization tables), SOF0 (frame header), DHT (Huffman tables).
    These are needed to decode subsequent SOS-only frames.
    """
    i = 0
    while i < len(jpeg_data) - 1:
        if jpeg_data[i] == 0xFF and jpeg_data[i + 1] == 0xDA:
            return jpeg_data[:i]  # everything before SOS
        i += 1
    raise ValueError(
        "No SOS marker found in JPEG data — is this really a full keyframe?"
    )


def reconstruct_jpeg(jpeg_header: bytes, sos_frame: bytes) -> bytes:
    """
    Stitch the keyframe header onto an SOS-only frame and ensure it ends with EOI.
    """
    data = jpeg_header + sos_frame
    if not data.endswith(b"\xff\xd9"):
        data += b"\xff\xd9"  # append EOI if missing
    return data


def swap_words(data):
    out = bytearray()

    for i in range(0, len(data), 2):
        pair = data[i : i + 2]

        if len(pair) == 2:
            out += pair[::-1]
        else:
            out += pair

    return bytes(out)


def process_video_chunk(reader: BinaryReader):
    global VIDEO_FRAME_HEADER

    frame_num = reader.read_uint32()
    chunk_size = reader.read_uint32()
    print(f"Video Chunk (Frame {frame_num}):")
    print(f"  Chunk Size: {chunk_size}")
    print(f"  Chunk Offset: {reader.pos()}")
    data = reader.read_bytes(chunk_size)
    frame = swap_words(data)

    if frame_num == 0:
        # This is the keyframe with the full JPEG data
        frame = fix_jpeg_byte_stuffing(frame)
        VIDEO_FRAME_HEADER = extract_jpeg_header(frame)
        output_file = OUTPUT_DIR / f"frame_{frame_num:04d}.jpg"
        output_file.parent.mkdir(exist_ok=True)
        with output_file.open("wb") as f:
            f.write(frame)
    else:
        if VIDEO_FRAME_HEADER is None:
            print("Error: Non-keyframe encountered before keyframe.")
            return

        # This frame only contains the SOS segment and entropy data, stitch it to the header
        frame = fix_jpeg_byte_stuffing(frame)
        full_frame = reconstruct_jpeg(VIDEO_FRAME_HEADER, frame)
        output_file = OUTPUT_DIR / f"frame_{frame_num:04d}.jpg"
        output_file.parent.mkdir(exist_ok=True)
        with output_file.open("wb") as f:
            f.write(full_frame)


def process_audio_chunk(reader: BinaryReader, chunk_magic: bytes):
    frame_num = reader.read_uint32()
    chunk_size = reader.read_uint32()
    print(f"Audio Chunk (Frame {frame_num}):")
    print(f"  Chunk Size: {chunk_size}")
    reader.seek(chunk_size, 1)  # skip the audio data


def main(file: Path):
    if not file.exists():
        print(f"File {file} does not exist.")
        return

    with file.open("rb") as f:
        reader = BinaryReader(f.read())
        magic = reader.read_bytes(4)
        if magic != MJP_MAGIC:
            print("Not a valid MJP file.")
            return

        header_size = reader.read_uint32()
        data_length = reader.read_uint32()  # not including the header
        unk2 = reader.read_uint32()
        frame_count = reader.read_uint32()
        unk4 = reader.read_uint32()
        unk5 = reader.read_uint32()
        unk6 = reader.read_uint32()
        reader.read_bytes(32)  # padding

        print(f"Magic: {magic}")
        print(f"Header Size: {header_size}")
        print(f"Data Length: {data_length}")
        print(f"Unknown 2: {unk2}")
        print(f"Frame Count: {frame_count}")
        print(f"Unknown 4: {unk4}")
        print(f"Unknown 5: {unk5}")
        print(f"Unknown 6: {unk6}")

        while not reader.eof():
            chunk_magic = reader.read_bytes(4)

            if chunk_magic == VIDEO_CHUNK_MAGIC:
                process_video_chunk(reader)
            elif chunk_magic in (AUDIO_1_CHUNK_MAGIC, AUDIO_2_CHUNK_MAGIC):
                process_audio_chunk(reader, chunk_magic)
            else:
                print(
                    f"Unknown chunk magic: {chunk_magic} at position {reader.tell() - 4}"
                )
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse MJP files")
    parser.add_argument("file", type=Path, help="The MJP file to parse")
    args = parser.parse_args()
    main(args.file)
