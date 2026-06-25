# Puyodead1, 2026
# GPLv3 License
#
# This script parses and extracts a binary archive file format seen in the vtech v.flash game "Bratz - The Secret Necklace"

"""
OUTPUT.BIN file format

uint32 - data offset; offset to the start of file data, used to mark the end of the entry table
File entry table (repeated until data offset is reached):
    uint32 - lba; the file's location in the archive, in 2048 byte sectors
    uint32 - size; the file's size in bytes
    uint32 - name length; the length of the file name string
    char[] - name; the file name string in iso 9660 cd rom style

file data
"""

from pathlib import Path
from binary_reader import BinaryReader
import argparse
from dataclasses import dataclass


@dataclass
class FileEntry:
    lba: int
    size: int
    name: str

    def __str__(self):
        return (
            f"File Entry:\n"
            f"  LBA: {self.lba}\n"
            f"  Size: {self.size}\n"
            f"  Name: {self.name}"
            f"  Offset: {self.lba * 2048:#x}"
        )

    @staticmethod
    def parse(reader: BinaryReader) -> "FileEntry":
        unk = reader.read_uint32()
        size = reader.read_uint32()
        name_len = reader.read_uint32()
        name = reader.read_str(name_len).split(";")[0][
            1:
        ]  # remove leading slash and split on ';' to get the clean name
        return FileEntry(unk, size, name)


@dataclass
class Archive:
    data_offset: int
    files: list[FileEntry]

    @staticmethod
    def parse(reader: BinaryReader) -> "Archive":
        data_offset = reader.read_uint32()

        archive = Archive(data_offset, [])

        while reader.pos() < data_offset:
            entry = FileEntry.parse(reader)
            archive.add_file(entry)

        return archive

    def add_file(self, file: FileEntry):
        self.files.append(file)

    def extract_file(self, reader: BinaryReader, idx: int, base_dir: Path):
        if idx < 0 or idx >= len(self.files):
            raise IndexError("File index out of range")

        file = self.files[idx]

        # calculate the file's offset in the archive
        offset = file.lba * 2048
        reader.seek(offset)

        output_path = base_dir / file.name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Extracting {file.name} to {output_path}")

        with output_path.open("wb") as f:
            f.write(reader.read_bytes(file.size))

    def extract_files(self, reader: BinaryReader, base_dir: Path):
        for idx in range(len(self.files)):
            self.extract_file(reader, idx, base_dir)

    def __str__(self):
        return (
            f"Archive:\n"
            f"  Data Offset: {self.data_offset}\n"
            f"  File Count: {len(self.files)}\n"
        )


def main(file: Path, output: Path, extract: bool):
    with file.open("rb") as f:
        reader = BinaryReader(f.read())

    archive = Archive.parse(reader)
    print(archive)

    if extract:
        archive.extract_files(reader, output)
    else:
        for file in archive.files:
            print(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a binary archive file.")
    parser.add_argument("file", type=Path, help="The path to the binary archive file.")
    parser.add_argument(
        "--output",
        type=Path,
        help="The path to the output directory for extracted files. Defaults to the parent directory of the input file.",
    )
    parser.add_argument(
        "--extract",
        "-e",
        action="store_true",
        help="Extract files from the archive.",
    )
    args = parser.parse_args()
    file: Path = args.file
    output: Path = args.output if args.output else Path(file.parent)
    extract = args.extract

    print(f"Parsing archive: {file}")
    print(f"Output directory: {output}")
    print()

    main(file, output, extract)
