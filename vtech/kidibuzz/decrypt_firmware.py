import array
import os
import struct
import sys

CHUNK_BYTES = 0x1000
CHUNK_WORDS = CHUNK_BYTES // 4
NATIVE_LE = (sys.byteorder == "little")

TABLE_A = bytes.fromhex("FF FE 00 FE 03 00 FE FD FE FD 00 00 02 01 FC 01 FF FE FD 04 FC 01 04 01 03 FF FD FE FC 02 00 00 01 00 FE 04 04 FD 04 FE 00 FF 00 FD 04 FC 04 02 FE 01 04 FC FC FE 02 FC FE FD 01 FE 02 FC 04 02 04 FE FC FC FD 03 02 00 01 FE 00 04 FF 01 FD FC 03 03 03 FD FE 01 04 03 FC FF 01 03 01 FF 04 FD FE FF 03 FF 04 01 FC FE 03 03 00 FF FF 04 FE 00 00 02 FC 00 03 03 FF FC 00 FC 01 03 00 02 04 04 03 FF FD 03 03 00 FE 03 FE 01 02 FD FC FD 00 00 02 FD FD FE FD 02 03 FF 00 04 02 FD 00 00 04 00 FE 02 FF FF FD 00 FF 04 FC FE 04 FC 02 01 FC 00 03 FE 01 02 FC FC 01 FC FD 01 03 FC FE FF 04 FC 00 FD FE FD 00 04 FC 01 04 04 FE 01 FE FC FF 01 FD 02 FE FC 04 FD FE 02 FD 03 FD FD 02 01 FF FC FE FC 01 03 02 FD FE 01 02 03 03 04 03 FC 03 FE 02 FC FC 01 FF FE 03 02 FE 01 FD 02 FF FD FF 02 FD 03 00 01 FD FF FE FF FD 04 FE 00 04 FC 00 FC 01 01 04 00 FF FF FE 01 FE FC 04 02 04 03 01 02 01 04 04 02 03 FF 00 00 03 01 03 FF 02 FF 03 FD 03 00 FD FF 00 FF 02 04 02 03 FF FF 02 FF 02 FD FC 00 FE FC 02 03 FC 00 FF 01 01 FE 00 04 04 04 FF 00 FD FE 02 02 FF FF FC 02 FF 00 FE FD 01 04 04 03 04 03 00 FE 04 FC 04 03 FC FD FE 01 FD FE 04 00 00 03 FE 02 03 00 01 02 01 02 01 FE FC 04 FF FF 02 FD FC FC 02 01 FE FF 02 03 FC 02 03 FF FC 01 02 FE 04 01 01 04 03 FF FE 04 FE 01 01 00 01 FC FC FE FC 03 00 FC FE FD FC FF 01 04 FC 04 00 FE 02 FE 01 FF 00 00 02 FE 04 FE 04 04 FD FF 01 04 FE 01 FD 02 FE 04 FE 02 FD 02 04 FC 04 00 02 FF 01 FD 04 00 01 02 00 FF 00 FD FC 03 FF 03 FF FF FD 03 00 FE FF FC FE 04 04 FC 00 FD 04 01 FC 03 00 02 04 01 02 FF FD 03 03 FC FC 02 03 FC")
TABLE_B = bytes.fromhex("0E FC 3E 01 10 10 F9 2E B0 F3 3F CE BB 57 CD 3B 6E 8C 7F 73 23 99 12 C8 31 8B 2F D9 0D 0D A5 C0 B5 39 F7 8D 4E AE 16 F4 0B E3 6F 42 52 BB 28 95 1A 59 A7 4D 98 35 55 BE 1A 6F A1 27 33 64 47 E8 18 80 D2 EF 4A 53 5F 74 75 E6 A5 E6 98 4F 32 25 67 83 F7 F1 EE 6C 07 A3 76 3B 9C 1A AC 00 5B F9 00 77 D9 10 4C 25 5D 17 B6 A4 E8 A2 D7 3C 72 51 1D B3 77 47 6D 65 B2 DE 0D 97 29 99 C2 08 69 5B 35 C9 13 D6 9B 4F 97 45 95 C7 40 5E 55 A9 71 82 03 90 2E 38 5F 49 DD D9 A7 29 4E 8D BB A4 FA 75 7F 1C 88 2A 81 F7 96 67 DC F4 B5 02 5C BF B5 21 E2 C3 24 AA 0A 3F 11 FB 0C 9C 15 DC E0 FE 95 B1 A6 19 41 F5 44 46 E0 E3 51 D5 50 76 32 A5 C8 94 82 F3 61 86 B8 70 D5 AC 03 96 86 6F 79 3B C2 76 71 67 45 1D 2D 63 FF 23 BD 12 18 A2 1F 84 32 45 AB C9 EE B5 AF 03 B1 54 56 BF A8 2E CE 86 09 2D A9 AE 9C 8C 84 76 7B 8D E7 53 16 6F 6D 84 79 9A 25 EC D2 1E 37 21 2D 5B CB C1 83 01 26 05 F3 3C 16 98 4F 28 91 A9 DA 8B 99 3F 50 C3 62 CC 27 FD B7 06 15 A8 9A F2 D2 2A 2B 41 1F D1 CB E0 07 0C 80 CB 65 DB 9B 22 A6 84 99 7E D0 88 48 85 C3 D5 2B BC C0 3D 1E 9D 27 27 3D EA 85 84 03 40 CD 05 AF EF E6 8B EC 09 66 E0 B0 B9 9E A4 65 D6 D6 8A 47 B8 D9 C4 0D 4B B5 BB CB 61 BC 04 17 4D CE 8F 6B AD DB 22 CA 87 A3 06 A6 98 C0 01 02 E8 E7 84 D4 A2 6B 24 AD 23 02 4E 9B 51 CC 37 4F 2E 91 13 7B AD 4B 87 7E C4 E4 60 43 C2 40 85 66 E3 7E 2A 99 21 7B 47 47 4E 98 49 77 60 BE 07 F2 0C 9F F7 A8 96 3E A2 50 E7 B1 55 4F E0 25 1A DB EE 24 E6 60 DE 13 14 22 F3 FF 12 25 36 99 5B 4A 0E 7E A5 BA 10 BC 5B 87 18 92 4D 91 99 78 A7 A7 31 5F 1F EF 81 3A 73 88 3B BD 13 6D 7C 65 1A 9D 5D B8 83")

def load_tables():
    A = list(struct.unpack("<128I", TABLE_A))
    B = list(struct.unpack("<128I", TABLE_B))
    return A, B

def _chunk_keystream(A, B, iVar8):
    deltas = array.array("I", bytes(4 * CHUNK_WORDS))
    xors = array.array("I", bytes(4 * CHUNK_WORDS))
    for i in range(CHUNK_WORDS):
        idx = (((iVar8 + i) // 0x80) + i) & 0x7f
        deltas[i] = A[0x7f - idx]
        xors[i] = B[idx]
    return deltas, xors
 
 
def decrypt_stream(fin, fout, A, B, total_size):
    iVar8 = 0
    remaining = total_size
    ks_cache = {}
    while remaining > 0:
        raw = fin.read(CHUNK_BYTES)
        if not raw:
            break
        nbytes = len(raw)
        pad = (-nbytes) % 4
        if pad:
            raw = raw + b"\x00" * pad
        nwords = len(raw) // 4
 
        words = array.array("I")
        words.frombytes(raw)
        if not NATIVE_LE:
            words.byteswap()
 
        key = (iVar8 // 0x80) & 0x7f
        ks = ks_cache.get(key)
        if ks is None:
            ks = _chunk_keystream(A, B, iVar8)
            ks_cache[key] = ks
        deltas, xors = ks
 
        for i in range(nwords):
            w = (words[i] - deltas[i]) & 0xffffffff
            words[i] = w ^ xors[i]
 
        if not NATIVE_LE:
            words.byteswap()
        out = words.tobytes()
        if pad and nbytes < CHUNK_BYTES:
            out = out[:nbytes]
        fout.write(out)
 
        iVar8 += nwords
        remaining -= nbytes
 
 
def decrypt_bytes(data, A, B):
    from io import BytesIO
    out = BytesIO()
    decrypt_stream(BytesIO(data), out, A, B, len(data))
    return out.getvalue()
 
 
def main():
    if len(sys.argv) < 3:
        print("usage: vtech_ota_decrypt.py <encrypted_in> <decrypted_out>")
        sys.exit(1)
    inp, outp = sys.argv[1], sys.argv[2]
    A, B = load_tables()
    size = os.path.getsize(inp)
    with open(inp, "rb") as fin, open(outp, "wb") as fout:
        decrypt_stream(fin, fout, A, B, size)
    with open(outp, "rb") as f:
        magic = f.read(4)
    print("wrote %s (%d bytes)" % (outp, size))
    print("first 4 bytes: %s  %s" % (
        magic.hex(), "PK zip OK" if magic[:2] == b"PK" else "NOT a zip header"))
 
 
if __name__ == "__main__":
    main()
 