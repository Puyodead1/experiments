# PTX

Starts with a 44 byte header, followed by bitmap data, and then ends with a palette (if 8bpp)

| Offset | Size | Description      |
| ------ | ---- | ---------------- |
| 0      | 2    | Header Size (44) |
| 2      | 2    | X?               |
| 4      | 2    | Y?               |
| 6      | 2    | Width            |
| 8      | 2    | Height           |
| 10     | 2    | BPP              |
| 12     | 4    | Unknown          |
| 16     | 4    | Unknown          |
| 20     | 2    | Palette Size     |
| 22     | 4    | Unknown          |
| 26     | 4    | Unknown          |
| 30     | 2    | Width Again?     |
| 32     | 2    | Height Again?    |
| 34     | 4    | Bitmap Size      |
| 38     | 4    | Unknown          |
