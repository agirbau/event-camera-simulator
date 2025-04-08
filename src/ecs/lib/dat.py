import struct
import logging
import numpy as np
from datetime import datetime

class DatFile():
    def __init__(self, filename):
        self.filename = filename
        self.logger = logging.getLogger()
        pass

    def write(self, ts, x, y, pol, event_type='dvs', width=None, height=None):
        f = open(self.filename, 'wb')
        if f == -1:
            print("Impossible to open the file")
            return
        if event_type in ['dvs', 'cd', 'td']:
            f.write(bytes("% Data file containing CD events.\n", encoding='utf8'))
        elif event_type in ['aps', 'em']:
            f.write(bytes("% Data file containing EM events.\n", encoding='utf8'))
        else:
            raise Exception("Specify a valid event type: 'dvs', 'cd', 'td', 'aps' or 'em'")

        f.write(bytes("% Version 2\n", encoding='utf8'))
        f.write(bytes("% Date " + str(datetime.now().replace(microsecond=0)) + '\n', encoding='utf8'))

        if width is None:
            width = x.max() + 1
        if height is None:
            height = y.max() + 1
        f.write(bytes("% Height " + str(height) + '\n', encoding='utf8'))
        f.write(bytes("% Width " + str(width) + '\n', encoding='utf8'))

        f.write(bytes(np.uint8([0])))  # Event Type
        f.write(bytes(np.uint8([8])))  # Event length
        arr = np.zeros(2 * ts.shape[0], dtype=np.uint32)
        arr[::2] = ts
        x_mask = np.uint32(0x00007FF)
        y_mask = np.uint32(0x0FFFC000)
        pol_mask = np.uint32(0x10000000)
        x_shift = 0
        y_shift = 14
        pol_shift = 28
        buf = np.array(x, dtype=np.uint32) << x_shift
        arr[1::2] += x_mask & buf
        buf = np.array(y, dtype=np.uint32) << y_shift
        arr[1::2] += y_mask & buf
        buf = np.array(pol, dtype=np.uint32) << pol_shift
        arr[1::2] += pol_mask & buf
        arr.tofile(f)
        f.close()

    def load(self, start=0, stop=-1):
        f = open(self.filename, 'rb')
        if f == -1:
            self.logger.error("The file does not exist")
            return
        else:
            self.logger.info("Load DAT Events: " + self.filename)
        l = f.readline()
        all_lines = l
        while l[0] == 37:
            p = f.tell() 
            self.logger.debug(l)
            l = f.readline()
            all_lines = all_lines + l
        f.close()
        all_lines = str(all_lines)
        f = open(self.filename, 'rb')
        f.seek(p, 0)
        evType = np.uint8(f.read(1)[0])
        evSize = np.uint8(f.read(1)[0])
        p = f.tell()
        l_last = f.tell()
        if start > 0:
            t = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
            dat = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
            while t < start:
                p = f.tell()
                t = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
                dat = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])

        if stop > 0:
            t = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
            dat = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
            while t < stop:
                l_last = f.tell()
                t = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
                dat = np.uint32(struct.unpack("<I", bytearray(f.read(4)))[0])
        else:
            l_last = f.seek(0, 2)

        num_b = (l_last - p) // evSize * 2
        f.close()
        data = np.fromfile(self.filename, dtype=np.uint32, count=num_b, offset=p)
        ts = data[::2]
        v = 0
        ind = all_lines.find("Version")
        if ind > 0:
            v = int(all_lines[ind+8])
        if v >= 2:
            x_mask = np.uint32(0x00007FF)
            y_mask = np.uint32(0x0FFFC000)
            pol_mask = np.uint32(0x10000000)
            x_shift = 0
            y_shift = 14
            pol_shift = 28
        else:
            x_mask = np.uint32(0x00001FF)
            y_mask = np.uint32(0x0001FE00)
            pol_mask = np.uint32(0x00020000)
            x_shift = 0
            y_shift = 9
            pol_shift = 17
        x = data[1::2] & x_mask
        x = x >> x_shift
        y = data[1::2] & y_mask
        y = y >> y_shift
        pol = data[1::2] & pol_mask
        pol = pol >> pol_shift
        if len(ts) > 0:
            self.logger.debug("First Event: ", ts[0], " us")
            self.logger.debug("Last Event: ", ts[-1], " us")
            self.logger.debug("Number of Events: ", ts.shape[0])

        return ts, x, y, pol