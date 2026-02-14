from enum import Enum

class Commands(Enum):
    InitPrinter = b'\x1B\x40' # ESC @
    FeedLine = b'\x0A' # LF
    Cutter = b'\x1D\x56\x41\x00' # ESC V 0
    FullCut = b'\x1B\x6D' # ESC m
    Tab = b'\x09' # Tabulator
    ResetPrintMode = b'\x1B\x21\x00' # ESC ! 0
    SelectFontA = b'\x1B\x21\x00' # ESC ! 0
    SelectFontB = b'\x1B\x21\x01' # ESC ! 1
    DoubleHeight = b'\x1B\x21\x10' # ESC ! 10
    DoubleWidth = b'\x1B\x21\x20' # ESC ! 20
    BoldOff = b'\x1B\45\x00' # ESC E 0
    Bold = b'\x1B\45\x01' # ESC E 1
    ItalicOff = b'\x1B\x34\x00' # ESC 4 0
    Italic = b'\x1B\x34\x01' # ESC 4 1
    UnderlineOff = b'\x1B\x2D\x00' # ESC - 0
    Underline = b'\x1B\x2D\x01' # ESC - 1
    Underline2 = b'\x1B\x2D\x02' # ESC - 2
    Rotation90Off = b'\x1B\x56\x00' # ESC V 0
    Rotation90 = b'\x1B\x56\x01' # ESC V 0
    Rotation180Off = b'\x1B\x7B\x00' # ESC { 0
    Rotation180 = b'\x1B\x7B\x01' # ESC { 0
    SetCharSize = b'\x1D\x21' # GS !
    ReversePrintModeOff = b'\x1D\x42\x00' # GS B 0
    ReversePrintMode = b'\x1D\x42\x01' # GS B 1
    DoubleStrikeOff = b'\x1b\x47\x00' # Esc G 0
    DoubleStrike = b'\x1b\x47\x01' # Esc G 1
    @staticmethod
    def qr(data: str, size=6, ecc=48):
        d = data.encode("iso-8859-1")
        store_len = len(d) + 3
        pL = store_len & 0xFF
        pH = store_len >> 8

        out = b''

        # Model 2
        out += b'\x1D\x28\x6B\x04\x00\x31\x41\x32\x00'

        # Size
        out += b'\x1D\x28\x6B\x03\x00\x31\x43' + bytes([size])

        # ECC
        out += b'\x1D\x28\x6B\x03\x00\x31\x45' + bytes([ecc])

        # Store data
        out += b'\x1D\x28\x6B' + bytes([pL, pH]) + b'\x31\x50\x30' + d

        # Print
        out += b'\x1D\x28\x6B\x03\x00\x31\x51\x30'

        return out

    @staticmethod
    def char_size(w, h):
        if w < 0 or w > 7 or h < 0 or h > 7:
            return Commands.SetCharSize.value+b'\x00'
        n = (w << 4) | h
        return Commands.SetCharSize.value+ bytes([n])
