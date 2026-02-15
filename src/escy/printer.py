from .commands import Commands
import serial
import time
from enum import Enum, auto

class PrinterState(Enum):
    INIT = auto()
    READY = auto()
    BUSY = auto()
    ERROR = auto()
    CLOSING = auto()
    TERMINATED = auto()

class EscPosPrinter:
    def __init__(self) -> None:
        # Open Serial Port
        self.state = PrinterState.INIT
        self.ser = serial.Serial(
            port='/dev/cu.usbserial-A906K3SO',
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        self.data = b''
    
    def header(self):
        self.data += Commands.InitPrinter.value
        self.data += b'\x1B\x74\x06' # Select Codepage
        self.state = PrinterState.READY

    def write(self, data: str, end='\n'):
        _fin = data + end
        self.data += _fin.encode("cp1252", errors="replace")

    def format(self, data: str, end='\n'):
        chars = {
            '<b>': Commands.Bold.value,
            '</b>': Commands.BoldOff.value,
            '<i>': Commands.Italic.value,
            '</i>': Commands.ItalicOff.value,
            '<u>': Commands.Underline.value,
            '<u2>': Commands.Underline2.value,
            '</u>': Commands.UnderlineOff.value,
            '</u2>': Commands.UnderlineOff.value, # same as </u>
            '<2xH>': Commands.DoubleHeight.value,
            '<2xW>': Commands.DoubleWidth.value,
            '<Fa>': Commands.SelectFontA.value,
            '<Fb>': Commands.SelectFontB.value,
            "</*>": Commands.ResetPrintMode.value,
            "<xR90>": Commands.Rotation90.value,
            "</xR90>": Commands.Rotation90Off.value,
            "<xR180>": Commands.Rotation180.value,
            "</xR180>": Commands.Rotation180Off.value,
            "<rpm>": Commands.ReversePrintMode.value,
            "</rpm>": Commands.ReversePrintModeOff.value,
            "<ds>": Commands.DoubleStrike.value,
            "</ds>": Commands.DoubleStrikeOff.value,
            "<t>": Commands.Tab.value,
            "<lf>": Commands.FeedLine.value,
            "<beep>": Commands.Beep.value,
            "<cut>": Commands.Cutter.value,
        }
        for i in range(0, 7):
            for j in range(0, 7):
                chars[f"<F{i}x{j}>"] = Commands.char_size(i, j)
        data_bytes = data.encode("cp1252", errors="replace")
        for key, value in chars.items():
            data_bytes = data_bytes.replace(key.encode("cp1252", errors="replace"), value)
        self.data += data_bytes + end.encode("cp1252", errors="replace")
    
    def pulse(self, ontime=255, offtime=20):
        self.data += Commands.pulse(ontime, offtime)
    
    def qr(self, data: str, size=6, ecc=48):
        self.data += Commands.qr(data, size, ecc)

    def raw(self, data: bytes):
        self.data += data
    
    def cmd(self, *data: str):
        # e.g. '1B' -> b'\x1B'
        self.data += bytes([int(i, 16) for i in data])

    def footer(self, close=False):
        # More LF for Feed
        self.data += b'\n' * 6
        self.data += b'\x1B\x64\x05' # Extra Feed
        self.state = PrinterState.BUSY
        self.ser.write(self.data)
        self.ser.flush()
        time.sleep(1.0)
        self.ser.write(b'\x1D\x56\x00') # Cut
        self.ser.flush()
        time.sleep(0.3)

        self.state = PrinterState.READY

        self.data = b''

        if close:
            self.state = PrinterState.CLOSING
            self.ser.close()
            self.state = PrinterState.TERMINATED
    
    def close(self):
        self.ser.flush()
        time.sleep(0.3)
        self.data = b''
        self.state = PrinterState.CLOSING
        self.ser.close()
        self.state = PrinterState.TERMINATED