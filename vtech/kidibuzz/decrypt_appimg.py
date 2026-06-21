import struct
import sys
from Crypto.Cipher import AES

_UNIQUE_KEY_AES_KEY = bytes([
    0x8d, 0x25, 0x92, 0xfa, 0x27, 0xa0, 0x9b, 0x19,
    0x77, 0x4c, 0xeb, 0x9d, 0x06, 0xd2, 0x30, 0x58,
])

_HDCP_KEY_AES_KEY = bytes([
    0x7c, 0x37, 0xa0, 0x05, 0x49, 0xb6, 0xfe, 0x73,
    0x44, 0x26, 0xa4, 0x8c, 0x90, 0x02, 0x5d, 0x17,
])

# XOR keystream base.
_XOR_BASE = bytes([
    0x9d,0x99,0x9b,0x26,0x7a,0x90,0x4a,0x96,0xf8,0xf6,0xbe,0x91,0x45,0x8f,0xb4,0xad,
    0x35,0x2e,0xc4,0xf5,0x38,0xd8,0xf0,0x2f,0x8a,0x26,0x7e,0x61,0xa9,0xeb,0x03,0x93,
    0x0c,0x17,0xc1,0xd5,0x12,0xdb,0x32,0x84,0x39,0x0e,0xe5,0xca,0x90,0xd0,0x89,0x64,
    0x6f,0x6d,0x48,0xa8,0x65,0x84,0x56,0xc6,0x72,0x68,0xc9,0x4e,0x76,0xc6,0xab,0xf2,
    0xea,0x88,0x4d,0x8e,0xce,0xfa,0xdf,0x65,0xe2,0x2b,0x3e,0xad,0x19,0x97,0x0d,0x4f,
    0x4b,0x02,0x07,0xe8,0x2a,0xa7,0x93,0x13,0x77,0x92,0x99,0xea,0x76,0x4b,0x95,0xca,
    0x9f,0xb4,0xea,0x57,0x96,0x34,0x78,0xc0,0x5d,0x15,0x70,0x45,0xc9,0x2b,0x67,0xf6,
    0x32,0xb7,0xaa,0xbd,0x6f,0x8a,0xd2,0x9e,0x01,0x6e,0x98,0x3e,0x8f,0xc1,0xea,0xa2,
    0x93,0x63,0x3e,0x3a,0x52,0xd3,0x26,0x1e,0x11,0x94,0x24,0x97,0x86,0xd6,0xc0,0xe1,
    0x8d,0x52,0xd9,0x2f,0x1c,0x76,0x39,0xf0,0x79,0xc2,0x6c,0x51,0xaa,0x72,0xd1,0x03,
    0x2e,0x5d,0xf1,0x3e,0xea,0x1d,0x10,0x06,0x66,0x70,0x02,0xad,0x39,0xde,0x40,0x99,
    0xc2,0x9c,0x3b,0x47,0x19,0xb1,0xf0,0x90,0x45,0x57,0xbd,0x2b,0xb0,0xa4,0x73,0x74,
    0xd8,0x69,0xac,0x6b,0x46,0x5b,0x5f,0x00,0xc4,0x70,0xb1,0x8e,0xcb,0x8c,0x0e,0xa5,
    0x3b,0x5d,0x79,0x0c,0x4e,0x83,0x20,0x06,0xcf,0xf5,0x34,0xd5,0x87,0xa0,0xf7,0x7d,
    0xf9,0x51,0x17,0xca,0x4f,0xd4,0x3a,0x94,0x93,0x5e,0xda,0x42,0x22,0x28,0x53,0x8d,
    0x5e,0x5d,0x3a,0x87,0xa4,0x36,0xf1,0xdb,0x7e,0x63,0x78,0x56,0x19,0xae,0x86,0xa6,
    0xf9,0xdb,0xd9,0x62,0xeb,0xd2,0xca,0x4b,0x3b,0x00,0x24,0xd2,0x28,0xfa,0x36,0xda,
    0x95,0x63,0x27,0xbe,0x01,0x11,0x8a,0x96,0xb9,0x6b,0x32,0xb6,0x4c,0x15,0x48,0x78,
    0x40,0xd0,0x9a,0x3c,0x03,0x9b,0x36,0xac,0x24,0x1e,0x38,0x45,0xc3,0x49,0xe0,0x13,
    0x47,0x39,0xe8,0xbb,0x4f,0x5b,0x14,0xbf,0xea,0xd3,0x0a,0xfe,0x0a,0x1f,0x64,0x7a,
    0x36,0xf7,0x04,0x5e,0x80,0x78,0xa7,0x40,0xb7,0x82,0xbd,0xa3,0xdd,0x5f,0x79,0xc0,
    0xdb,0xa5,0x24,0x86,0x74,0x5d,0xb6,0xdf,0x78,0x64,0xa7,0x35,0x3a,0x12,0x03,0x35,
    0x43,0x1a,0xbd,0xd2,0x48,0xb1,0x45,0x8d,0x5a,0xf3,0x5c,0xf4,0x5d,0x82,0x28,0x69,
    0xbb,0x70,0x83,0x25,0x5a,0x5f,0x99,0x7d,0xcb,0xe6,0xb2,0x63,0xc4,0x37,0x4c,0x2f,
    0xd0,0xff,0x6d,0xa0,0x45,0x8e,0x37,0x1d,0x76,0x38,0xbd,0x41,0x2b,0xfb,0x15,0x97,
    0x4e,0x62,0xaf,0xa2,0xe7,0xa8,0xe4,0x21,0x4b,0x21,0xd2,0x90,0x8f,0xd6,0x68,0xf2,
    0x43,0x6f,0xbd,0xce,0x5d,0x57,0xa6,0x78,0x74,0x1a,0x87,0x91,0x2f,0x12,0x69,0xd1,
    0xfc,0x42,0x4d,0x04,0x05,0x82,0xc0,0x53,0x60,0xdd,0xb0,0xc5,0x85,0x37,0x7e,0x06,
    0x06,0x32,0x54,0x66,0x7a,0x53,0xb9,0x24,0xba,0x61,0x63,0xed,0x51,0x0e,0x4c,0xa0,
    0x2d,0xda,0x08,0x54,0x9b,0x33,0x55,0x9c,0x72,0xe1,0xf4,0x0a,0x8d,0xa1,0xb7,0xf1,
    0x7f,0x10,0xdc,0x6f,0x83,0xcb,0x99,0xab,0xb2,0xd5,0xf8,0x5c,0x79,0x39,0xe5,0x8b,
    0x49,0xf0,0x85,0x99,0x90,0x04,0xca,0x83,0xe9,0xf6,0x45,0x65,0x8f,0x5e,0x3b,0x3d,
])
_XOR_TABLE = (_XOR_BASE * 8)[:3872]

def _xor_sector(sector: bytes, partition_id: int) -> bytes:
    offset = 224 * (partition_id % 16)
    ks = _XOR_TABLE[offset:offset + 512]
    return bytes(a ^ b for a, b in zip(sector, ks))


def _xor_partition(raw: bytes, partition_id: int) -> bytes:
    return b''.join(_xor_sector(raw[i:i+512], partition_id) for i in range(0, len(raw), 512))


def _bswap32(x):
    return struct.unpack('<I', struct.pack('>I', x & 0xFFFFFFFF))[0]


def _aes_ctr(key16: bytes, data: bytes) -> bytes:
    kw  = struct.unpack_from('<4I', key16)
    v24 = kw[3] & 0xFFFFFFFF
    out = bytearray(data)
    n = pos = 0
    n = len(data)
    while pos < n:
        chunk_idx  = pos // 0x4000
        chunk_base = chunk_idx * 0x4000
        chunk_end  = min((chunk_idx + 1) * 0x4000, n)
        dk = struct.pack('<4I',
            _bswap32(kw[0] + chunk_base), _bswap32(kw[1]),
            _bswap32(kw[2]),              _bswap32(kw[3]))
        ecb = AES.new(dk, AES.MODE_ECB)
        while pos < chunk_end:
            b = (v24 + pos) & 0xFFFFFFFF
            ctr = struct.pack('<4I', b, (b+4)&0xFFFFFFFF, (b+8)&0xFFFFFFFF, (b+12)&0xFFFFFFFF)
            ks = bytes(reversed(ecb.encrypt(bytes(reversed(ctr)))))
            for m in range(16):
                out[pos + m] ^= ks[m]
            pos += 16
    return bytes(out)


_KB_SIZE     = 16368
_KB_DATA_END = 16336
_KB_SUM_OFF  = 16344
_KB_SUM_C    = 16348
_KB_SEC_OFF  = 16352
_KB_SEC_C    = 16356
_HDR_SIZE    = 480


def _verify_key_block(block: bytes) -> bool:
    chk = sum(struct.unpack_from('<I', block, i)[0] for i in range(0, _KB_DATA_END, 4)) & 0xFFFFFFFF
    s, sc = struct.unpack_from('<II', block, _KB_SUM_OFF)
    v, vc = struct.unpack_from('<II', block, _KB_SEC_OFF)
    return (chk == s and
            (s + sc) & 0xFFFFFFFF == 0xFFFFFFFF and
            (v + vc) & 0xFFFFFFFF == 0xFFFFFFFF)


# Logical partition types (index into version partition pair table)
_TYPE_APP      = 0
_TYPE_UNIQUEKEY = 1
_TYPE_HDCP     = 4  # HdcpKey_Read uses AppRead_Open(4)

# Base raw partition ID for each logical type (A copy; B copy = base+1)
_TYPE_BASE_PART = {
    _TYPE_APP:       2,
    _TYPE_UNIQUEKEY: 4,
    2:               6,
    3:               8,
    _TYPE_HDCP:      10,
}

# Sector count for each logical type
_TYPE_SECTORS = {
    _TYPE_UNIQUEKEY: 33,   # AppUpgrade_SectorWrite(..., 33)
    _TYPE_HDCP:      1,    # HdcpKey single sector
}


def parse_appa(img: bytes) -> list[dict]:
    """Decrypt sector 0 and return the list of raw partition dicts."""
    s0 = _xor_sector(img[:512], 255)
    if s0[:4] != b'APPA':
        raise ValueError(f'Bad APPA magic: {s0[:4].hex()}')
    parts = []
    prev_start = prev_count = 0
    for i in range(12):
        off = 8 + i * 8
        start, count = struct.unpack_from('<II', s0, off)
        if count == 0:
            break
        if start == 0 and i > 0:
            start = prev_start + prev_count
        parts.append({'id': i, 'start': start, 'count': count})
        prev_start, prev_count = start, count
    return parts


def read_version_partition(img: bytes, parts: list, vp_id: int) -> list | None:
    """
    Decrypt version partition vp_id (0 or 1) and return its u32 array,
    or None if the checksum fails (treated as version 0 by the firmware).
    """
    p = parts[vp_id]
    raw = img[p['start']*512 : (p['start']+1)*512]
    dec = _xor_sector(raw, vp_id)
    # AppAccess_VerifyChecksum — we don't have the exact impl, but if the partition looks valid (non-zero version) we trust it.
    vals = list(struct.unpack_from('<128I', dec))
    return vals if vals[0] > 0 else None


def resolve_active_partition(img: bytes, parts: list, logical_type: int) -> dict:
    """
    Read both version partitions, pick the one with the higher version counter,
    then return the active raw partition dict for the given logical type.
    """
    vp0 = read_version_partition(img, parts, 0)
    vp1 = read_version_partition(img, parts, 1)

    ver0 = vp0[0] if vp0 else 0
    ver1 = vp1[0] if vp1 else 0
    active_vp = vp1 if ver1 >= ver0 else vp0

    idx_a = 2 * logical_type + 1   # index of A copy version counter
    idx_b = 2 * logical_type + 2   # index of B copy version counter
    base  = _TYPE_BASE_PART[logical_type]

    # If B counter >= A counter, B is the most recently written copy
    raw_id = (base + 1) if active_vp[idx_a] <= active_vp[idx_b] else base

    print(f'  Version partitions: VP0 ver={ver0}  VP1 ver={ver1}  -> using VP{1 if ver1>=ver0 else 0}')
    print(f'  Type {logical_type} counters: A(part {base})={active_vp[idx_a]}  B(part {base+1})={active_vp[idx_b]}  -> active=part {raw_id}')

    matching = [p for p in parts if p['id'] == raw_id]
    if not matching:
        raise ValueError(f'Partition {raw_id} not present in APPA table (device may not have this partition type)')
    return matching[0]


def decrypt_uniquekey(img: bytes, parts: list) -> tuple[bytes, bytes]:
    """
    Resolve and decrypt the active UniqueKey partition.
    Returns (key_block_plaintext, header).
    """
    p = resolve_active_partition(img, parts, _TYPE_UNIQUEKEY)
    raw = img[p['start']*512 : (p['start'] + 33)*512]

    # Layer 1: XOR
    xor_dec = _xor_partition(raw, p['id'])
    header    = xor_dec[:_HDR_SIZE]
    enc_block = xor_dec[_HDR_SIZE:_HDR_SIZE + _KB_SIZE]

    # Layer 2: AES-128-CTR
    key_block = _aes_ctr(_UNIQUE_KEY_AES_KEY, enc_block)

    if not _verify_key_block(key_block):
        raise ValueError('UniqueKey checksum failed — data corrupt?')

    return key_block, header


def decrypt_hdcp(img: bytes, parts: list) -> bytes:
    """
    Resolve and decrypt the active HdcpKey partition.
    Returns the 320-byte plaintext HDCP key block.
    """
    p = resolve_active_partition(img, parts, _TYPE_HDCP)
    raw = img[p['start']*512 : (p['start'] + 1)*512]

    # Layer 1: XOR (1 sector)
    xor_dec = _xor_sector(raw, p['id'])

    # Layer 2: AES-128-CTR, 320 bytes
    return _aes_ctr(_HDCP_KEY_AES_KEY, xor_dec[:320])


def dump_raw_partition(img: bytes, parts: list, part_id: int) -> bytes:
    """XOR-decrypt a raw partition by index and return its bytes."""
    p = parts[part_id]
    raw = img[p['start']*512 : (p['start'] + p['count'])*512]
    return _xor_partition(raw, p['id'])


def _print_partition_table(img: bytes, parts: list):
    vp0 = read_version_partition(img, parts, 0)
    vp1 = read_version_partition(img, parts, 1)
    active_vp = vp1 if (vp1 and vp0 and vp1[0] >= vp0[0]) or not vp0 else vp0

    labels = {
        0: 'version A',
        1: 'version B',
        2: 'app A',
        3: 'app B',
        4: 'uniquekey A',
        5: 'uniquekey B',
        6: 'type2 A',
        7: 'type2 B',
        8: 'type3 A / hdcp A',
        9: 'type3 B / hdcp B',
        10: 'type4 A',
        11: 'type4 B',
    }

    print(f'{"ID":>3}  {"start":>7}  {"count":>6}  {"offset":>12}  {"size":>10}  label')
    print('-' * 70)
    for p in parts:
        i = p['id']
        marker = ''
        if i in (0, 1):
            ver = vp0[0] if i == 0 and vp0 else (vp1[0] if i == 1 and vp1 else 0)
            marker = f'  [ver={ver}]'
        elif i in (4, 5) and active_vp:
            cnt = active_vp[3 if i == 4 else 4]
            marker = f'  [counter={cnt}]'
        print(f'{i:>3}  {p["start"]:>7}  {p["count"]:>6}  '
              f'0x{p["start"]*512:>08x}  '
              f'0x{p["count"]*512:>08x}  '
              f'{labels.get(i, "?")} {marker}')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    imgpath = sys.argv[1]
    cmd     = sys.argv[2] if len(sys.argv) > 2 else None

    print(f'Loading {imgpath} ...')
    img   = open(imgpath, 'rb').read()
    parts = parse_appa(img)
    print(f'  {len(img)//512} sectors, {len(parts)} partitions found\n')

    if cmd is None:
        _print_partition_table(img, parts)
        print('\nSubcommands: uniquekey  hdcp  raw <part_id>')

    elif cmd == 'uniquekey':
        outpath = sys.argv[3] if len(sys.argv) > 3 else None
        print('Decrypting UniqueKey ...')
        key_block, header = decrypt_uniquekey(img, parts)
        with open("uniquekey_header.bin", "wb") as f:
            f.write(header)

        ts = key_block[16336:16344]
        year, mon, day, hr, mi, sec = struct.unpack_from('<HBBBBBB', ts)[:6]  # type: ignore
        ident = bytes(b if 0x20 <= b <= 0x7e else ord('.') for b in key_block[:28]).decode()
        print(f'\n  Device identifier: {ident}')
        print(f'  Provisioned:       {year}-{mon:02d}-{day:02d} {hr:02d}:{mi:02d}:{sec:02d}')
        print(f'  Key data size:     {16336} bytes')

        if outpath:
            open(outpath, 'wb').write(key_block)
            print(f'  Written to {outpath}')
        else:
            print(f'  Key block hex (first 64 B): {key_block[:64].hex()}')

    elif cmd == 'hdcp':
        outpath = sys.argv[3] if len(sys.argv) > 3 else None
        print('Decrypting HdcpKey ...')
        hdcp = decrypt_hdcp(img, parts)
        print(f'  First 32 bytes: {hdcp[:32].hex()}')
        if outpath:
            open(outpath, 'wb').write(hdcp)
            print(f'  Written to {outpath}')

    elif cmd == 'raw':
        if len(sys.argv) < 4:
            print('Usage: raw <part_id> [outfile]')
            sys.exit(1)
        part_id = int(sys.argv[3])
        outpath = sys.argv[4] if len(sys.argv) > 4 else None
        print(f'Dumping raw partition {part_id} (XOR layer only) ...')
        raw = dump_raw_partition(img, parts, part_id)
        print(f'  {len(raw)} bytes, first 32: {raw[:32].hex()}')
        if outpath:
            open(outpath, 'wb').write(raw)
            print(f'  Written to {outpath}')
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)


if __name__ == '__main__':
    main()
