import sys

PRESET_VALUE=0xFFFF
POLYNOMIAL=0x8408

def checksum(pucY):
    uiCrcValue = PRESET_VALUE
    for ucY in pucY:
        uiCrcValue = uiCrcValue ^ ucY
        for ucJ in range(8):
            if uiCrcValue & 0x0001:
                uiCrcValue = (uiCrcValue >> 1) ^ POLYNOMIAL;
            else:
                uiCrcValue = (uiCrcValue >> 1)
    return uiCrcValue;

if __name__ == '__main__':
    print('%X' % (checksum(bytearray.fromhex(sys.argv[1])),))
