import os,sys,time,wiringpi

# This script writes a 64 kbyte binary to a clean EEPROM.
# It is recommended to verify the chip has been erased with cleancheck before using this.

# usage: python3 eeprom_burn.py <bin> [optional arguments]
# optional arguments:
#  nosizecheck - skips the file size check and allows burning files that are not 0xFFFF in size

# pin 7 and 9 on my raspi are broken

# expected file size
correct_filesize = 65536

# eeprom pin assignments
A0  = 8
A1  = 9
A2  = 7
A3  = 0
A4  = 2
A5  = 3
A6  = 12
A7  = 13
A8  = 14
A9  = 30
A10 = 21
A11 = 22
A12 = 23
A13 = 24
A14 = 25
A15 = 29

D0  = 28
D1  = 27
D2  = 26
D3  = 31
D4  = 11
D5  = 10
D6  = 6
D7  = 5

ce_pin = 4
oe_pin = 1

# wiringpi acronyms
OUTPUT = 1

# initialize gpio pins
def initialize_gpio():

    wiringpi.wiringPiSetup()

    wiringpi.pinMode(ce_pin, OUTPUT)
    wiringpi.pinMode(oe_pin, OUTPUT)

    # set control signals properly while we're setting up
    wiringpi.digitalWrite(ce_pin, True)
    wiringpi.digitalWrite(oe_pin, False)

    wiringpi.pinMode(A0, OUTPUT)
    wiringpi.pinMode(A1, OUTPUT)
    wiringpi.pinMode(A2, OUTPUT)
    wiringpi.pinMode(A3, OUTPUT)
    wiringpi.pinMode(A4, OUTPUT)
    wiringpi.pinMode(A5, OUTPUT)
    wiringpi.pinMode(A6, OUTPUT)
    wiringpi.pinMode(A7, OUTPUT)
    wiringpi.pinMode(A8, OUTPUT)
    wiringpi.pinMode(A9, OUTPUT)
    wiringpi.pinMode(A10, OUTPUT)
    wiringpi.pinMode(A11, OUTPUT)
    wiringpi.pinMode(A12, OUTPUT)
    wiringpi.pinMode(A13, OUTPUT)
    wiringpi.pinMode(A14, OUTPUT)
    wiringpi.pinMode(A15, OUTPUT)

    wiringpi.pinMode(D0, OUTPUT)
    wiringpi.pinMode(D1, OUTPUT)
    wiringpi.pinMode(D2, OUTPUT)
    wiringpi.pinMode(D3, OUTPUT)
    wiringpi.pinMode(D4, OUTPUT)
    wiringpi.pinMode(D5, OUTPUT)
    wiringpi.pinMode(D6, OUTPUT)
    wiringpi.pinMode(D7, OUTPUT)


def write_byte(a, d):
    wiringpi.digitalWrite(ce_pin, True)  # de-assert chip enable

    # set the address - inverted to account for python list indexing
    wiringpi.digitalWrite(A0, a[15])
    wiringpi.digitalWrite(A1, a[14])
    wiringpi.digitalWrite(A2, a[13])
    wiringpi.digitalWrite(A3, a[12])
    wiringpi.digitalWrite(A4, a[11])
    wiringpi.digitalWrite(A5, a[10])
    wiringpi.digitalWrite(A6, a[9])
    wiringpi.digitalWrite(A7, a[8])
    wiringpi.digitalWrite(A8, a[7])
    wiringpi.digitalWrite(A9, a[6])
    wiringpi.digitalWrite(A10, a[5])
    wiringpi.digitalWrite(A11, a[4])
    wiringpi.digitalWrite(A12, a[3])
    wiringpi.digitalWrite(A13, a[2])
    wiringpi.digitalWrite(A14, a[1])
    wiringpi.digitalWrite(A15, a[0])

    # set the byte - inverted to account for python list indexing
    wiringpi.digitalWrite(D0, d[7])
    wiringpi.digitalWrite(D1, d[6])
    wiringpi.digitalWrite(D2, d[5])
    wiringpi.digitalWrite(D3, d[4])
    wiringpi.digitalWrite(D4, d[3])
    wiringpi.digitalWrite(D5, d[2])
    wiringpi.digitalWrite(D6, d[1])
    wiringpi.digitalWrite(D7, d[0])

    wiringpi.digitalWrite(ce_pin, False)  # assert chip enable
    time.sleep(0.0000001)  # wait for the required time
    wiringpi.digitalWrite(ce_pin, True)  # de-assert chip enable and done

if __name__ == '__main__':

    # open the file
    try:
        binfile = open(sys.argv[1], 'rb')
    except IndexError:
        print('bad filename')
        quit()
    except FileNotFoundError:
        print('bad filename')
        quit()

    if not "nosizecheck" in sys.argv:  # allow skipping of size check
        if os.path.getsize(sys.argv[1]) != correct_filesize:  # check the file size
            print('incorrect file size')
            quit()
    else:
        if correct_filesize < os.path.getsize(sys.argv[1]):
            print('warning: file size is greater than 0xFFFF, some data cannot be written')
        correct_filesize = os.path.getsize(sys.argv[1])  # update the correct file size if we're bypassing the check

    initialize_gpio()  # init gpio

    if input('type "flash" to burn >> ') != "flash":  # prompt for user confirmation
        print('exiting...')
        quit()

    addr = 0  # start the address counter at address 0x0000
    progress = 0
    last_progress = 0
    while True:  # main flashing loop

        data_byte = binfile.read(1)  # pull the next byte

        # check to see if we actually got a byte
        # if it's blank, we're EOF and done
        if data_byte == b'':
            break

        data_byte_l = [int(x) for x in bin(data_byte[0])[2:]]  # convert the byte to a list of integers
        while len(data_byte_l) < 8:  # prepend zeroes until we're 8 bits long
            data_byte_l.insert(0,0)

        addr_byte_l = [int(x) for x in bin(addr)[2:]]  # convert the address to a byte list
        while len(addr_byte_l) < 16:  # prepend zeroes until we're 16 bits long
            addr_byte_l.insert(0,0)

        write_byte(addr_byte_l, data_byte_l)  # write the byte out

        progress = round(100*(addr/correct_filesize), 1)
        if progress > last_progress:
            print(f'burning: {progress}% complete...', end='\r')  # update status
            last_progress = progress

        addr += 1  # increment address counter

    print('burn complete!               ')
    binfile.close()
