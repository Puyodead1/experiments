"""
LAYOUT
  0x0000  serial        28 bytes ASCII   device unique ID / serial
  0x001c  rnd_body      ...              per-device random / key material -> 0x3ebc
  0x3ebc  region_group  2 bytes ASCII    "US","GB",...
  0x3ebe  lang_code     3 bytes ASCII    eng fre ger dut spa dan por ita
  0x3ec1  flags         3 bytes          observed 01 00 FF
  0x3ec4  model         4 bytes ASCII    e.g. "1695"
  0x3ec8  (zero pad)
  0x3fd0  build_ts      8 bytes          u16 year,u8 mon,day,hour,min,sec,pad
  0x3fd8  cksum1        uint32           == sum(words[0..0xff3])
  0x3fdc  cksum1_cpl    uint32           == ~cksum1
  0x3fe0  cksum2        uint32
  0x3fe4  cksum2_cpl    uint32           == ~cksum2
  0x3fe8  tail          0x10 bytes       zero pad
"""
import struct
import sys
from io import BytesIO
from binreader import BinaryReader

FILE_SIZE        = 0x3ff8
SERIAL_OFF       = 0x0000
SERIAL_LEN       = 0x1c
BODY_CKSUM_WORDS = 0xff4
OFF_REGION_GROUP = 0x3ebc
OFF_LANG_CODE    = 0x3ebe
OFF_FLAGS        = 0x3ec1
OFF_MODEL        = 0x3ec4
OFF_BUILD_TS     = 0x3fd0
OFF_CKSUM1       = 0x3fd8
OFF_CKSUM1_CPL   = 0x3fdc
OFF_CKSUM2       = 0x3fe0
OFF_CKSUM2_CPL   = 0x3fe4
OFF_TAIL         = 0x3fe8

KNOWN_LANGS = {"eng", "fre", "ger", "dut", "spa", "dan", "por", "ita"}


class UniqueKey:
    def __init__(self, data: bytes):
        if len(data) < FILE_SIZE:
            raise ValueError("uniquekey too small: %d (expected %d)"
                             % (len(data), FILE_SIZE))
        self.raw = data[:FILE_SIZE]
        r = BinaryReader(BytesIO(self.raw))

        r.seek(SERIAL_OFF)
        self.serial = self._ascii(r.read(SERIAL_LEN))
        self.rnd_body = self.raw[SERIAL_OFF + SERIAL_LEN:OFF_REGION_GROUP]

        r.seek(OFF_REGION_GROUP)
        self.region_group = self._ascii(r.read(2))
        self.lang_code = self._ascii(r.read(3))
        self.flags = r.read(3)
        self.model = self._ascii(r.read(4))

        r.seek(OFF_BUILD_TS)
        year = r.read_uint16()
        mon, day, hour, minute, sec, _pad = (r.read_ubyte() for _ in range(6))
        self.build_ts = (year, mon, day, hour, minute, sec)

        r.seek(OFF_CKSUM1)
        self.cksum1 = r.read_uint32()
        self.cksum1_cpl = r.read_uint32()
        self.cksum2 = r.read_uint32()
        self.cksum2_cpl = r.read_uint32()

        self.tail = self.raw[OFF_TAIL:FILE_SIZE]

        words = struct.unpack("<%dI" % BODY_CKSUM_WORDS,
                              self.raw[:BODY_CKSUM_WORDS * 4])
        self.computed_cksum1 = sum(words) & 0xffffffff

    @staticmethod
    def _ascii(b: bytes) -> str:
        nul = b.find(b"\x00")
        if nul >= 0:
            b = b[:nul]
        try:
            return b.decode("ascii")
        except UnicodeDecodeError:
            return b.hex()

    @property
    def checksum_bypass(self) -> bool:
        return self.cksum1 == 0xffffffff and self.cksum1_cpl == 0xffffffff

    @property
    def cksum1_ok(self) -> bool:
        if self.checksum_bypass:
            return True
        comp = ((self.cksum1 + self.cksum1_cpl) & 0xffffffff) == 0xffffffff
        return comp and self.computed_cksum1 == self.cksum1

    @property
    def cksum2_ok(self) -> bool:
        return ((self.cksum2 + self.cksum2_cpl) & 0xffffffff) == 0xffffffff

    @property
    def valid(self) -> bool:
        return self.cksum1_ok and self.cksum2_ok

    @property
    def build_ts_str(self) -> str:
        y, mo, d, h, mi, s = self.build_ts
        return "%04d-%02d-%02d %02d:%02d:%02d" % (y, mo, d, h, mi, s)

    @property
    def variant_tag(self) -> str:
        if self.lang_code in KNOWN_LANGS:
            return "gen"
        if self.region_group == "GB":
            return "euk"
        return self.lang_code or "?"

    def summary(self) -> str:
        return "\n".join([
            "uniquekey: %d bytes" % len(self.raw),
            "  serial        (0x0000): %r" % self.serial,
            "  region_group  (0x3ebc): %r" % self.region_group,
            "  lang_code     (0x3ebe): %r%s" % (
                self.lang_code,
                "" if self.lang_code in KNOWN_LANGS else "  (unknown)"),
            "  flags         (0x3ec1): %s" % self.flags.hex(),
            "  model         (0x3ec4): %r" % self.model,
            "  variant_tag           : %r" % self.variant_tag,
            "  build_ts      (0x3fd0): %s" % self.build_ts_str,
            "  cksum1        (0x3fd8): 0x%08x" % self.cksum1,
            "  cksum1_cpl    (0x3fdc): 0x%08x" % self.cksum1_cpl,
            "  computed sum          : 0x%08x" % self.computed_cksum1,
            "  cksum1_ok             : %s%s" % (
                self.cksum1_ok,
                "  (all-FF bypass)" if self.checksum_bypass else ""),
            "  cksum2        (0x3fe0): 0x%08x" % self.cksum2,
            "  cksum2_cpl    (0x3fe4): 0x%08x" % self.cksum2_cpl,
            "  cksum2_ok             : %s" % self.cksum2_ok,
            "  rnd_body length       : 0x%x bytes" % len(self.rnd_body),
            "  VALID                 : %s" % self.valid,
        ])


def main():
    if len(sys.argv) < 2:
        print("usage: parse_uniquekey.py <uniquekey.txt>")
        sys.exit(1)
    uk = UniqueKey(open(sys.argv[1], "rb").read())
    print(uk.summary())


if __name__ == "__main__":
    main()
