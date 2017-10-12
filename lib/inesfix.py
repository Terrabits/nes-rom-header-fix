"""
Converts NES ROMs to iNES format, applying correct iNES header.
Usage: ines-fix <infile>
Supported infile formats are .nes, .pas (headerless .nes)

ROM data is recognized by CRC32 using BootGod's master XML database
  so make sure you have a local copy
"""

from   binascii  import crc32
import codecs
import os
from   pathlib   import Path
import struct
from   xml.etree import ElementTree

##### String holding location of cart db
cart_xml = "NesCarts (2017-08-21).xml"
# uncomment next line to use Nestopia's DB instead
# cart_xml = "NstDatabase.xml"

def fix_headers(path):
    success = True
    files   = os.listdir(str(path))
    files   = [str(path / i) for i in files if os.path.isfile(str(path / i))]
    for i in files:
        if not fix_header(i):
            success = False
    return False

def fix_header(filename):
    # Other required vars
    i_fmt = 'p'
    blob = None
    found = 0
    oldHeader = b''

    # Open rom database
    #print "Attempting to open cart db " + cart_xml
    cart_xml_path = str(Path(__file__).parent / cart_xml)
    tree = ElementTree.parse(cart_xml_path)
    #print "DB opened!"

    # Attempt to open supplied rom file

    try:
        with open(filename, "rb") as f:
            tag = f.read(4)
            f.seek(0)
            if (tag == b'NES\x1A'):
                i_fmt = 'i'
                oldHeader = f.read(16)

    #        print "Detected " + i_fmt + " format for input file"

            blob = f.read()

    except IOError as err:
        print("Error opening " + filename + ": ")
        print("I/O error({0}): {1}".format(err.errno, err.strerror))
        return False

    if (len(blob) > 0):
        format_crc32 = format(crc32(blob) & 0xFFFFFFFF, '08X')
        print("CRC check: " + format_crc32)

        # go look up crc32 in db
        game_list = tree.findall("game")
        for game in game_list:
            cart_list = game.findall("cartridge")
            for cart in cart_list:
                if (cart.attrib.get('crc') == format_crc32):
                    found=1
                    break
            if (found):
                break

        if (found == 0):
            print(filename)
            print("*** CART NOT FOUND IN DB")
            print("----------------------------------------------------")
            return False

    print("Found CRC match: " + game.attrib.get("name").encode('ascii', 'ignore').decode('ascii'))
    #ElementTree.tostring(game)

    # retrieve data from game
    board = cart.find("board")
    mapper = int(board.attrib.get("mapper"))

    prg_size = 0
    prg_list = board.findall("prg")
    for prg in prg_list:
        prg_size = prg_size + int(prg.attrib.get("size") [:-1])

    chr_size = 0
    chr_list = board.findall("chr")
    for chr in chr_list:
        chr_size = chr_size + int(chr.attrib.get("size") [:-1])


    battery = 0
    wram_list = board.findall("wram")
    for wram in wram_list:
        if (wram.attrib.get("battery") is not None):
            battery = int(wram.attrib.get("battery"))

    chip_list = board.findall("chip")
    for chip in chip_list:
        if (chip.attrib.get("battery") is not None):
            battery = int(chip.attrib.get("battery"))


    mirror_4 = 0
    mirror_v = 0
    pad = board.find("pad")
    if (format_crc32 == "CD50A092" or \
        format_crc32 == "EC968C51" or \
        format_crc32 == "404B2E8B"):
        mirror_4 = 1
    elif (pad is not None):
    # the "h" pad means "v" mirror
        mirror_v = int(pad.attrib.get("h"))


    mapper_lo = mapper & 0x0F
    mapper_hi = mapper & 0xF0

    newHeader = b'NES\x1A'
    newHeader = newHeader + struct.pack("BBBB",
                                        int(prg_size / 16),
                                        int(chr_size / 8),
                                        int((mapper_lo << 4) + (mirror_4 << 3) + (battery << 1) + (mirror_v)),
                                        int(mapper_hi))
    newHeader = newHeader + ( b'\0' * 8 )

    if (newHeader != oldHeader):
        print("*** HEADER UPDATED ***\noldHeader: " + codecs.encode(oldHeader, 'hex').decode('ascii'))
        print("newHeader: " + codecs.encode(newHeader, 'hex').decode('ascii'))

        # write new file
        try:
            with open(filename, "wb") as f:
                f.write( newHeader )
                f.write( blob )


        except IOError as err:
            print("Error opening " + filename)
            print("I/O error({0}): {1}".format(err.errno, err.strerror))
            return False

        print("All done.  Wrote new file " + filename)
    else:
        print("*** Header unchanged: not writing replacement file.")
    print("----------------------------------------------------")
    return True
