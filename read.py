import os,sys,time,wiringpi
from bitstring import BitArray

# This script reads the EEPROM from hex 0000-FFFF.

# usage: python3 eeprom_read.py <output filename>

# pin 7 and 9 on my raspi are broken

# output file size
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
INPUT = 0

# initialize gpio pins
def initialize_gpio():

    wiringpi.wiringPiSetup()

    wiringpi.pinMode(ce_pin, OUTPUT)
    wiringpi.pinMode(oe_pin, OUTPUT)

    # set control signals properly while we're setting up
    wiringpi.digitalWrite(ce_pin, True)
    wiringpi.digitalWrite(oe_pin, True)

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

    wiringpi.pinMode(D0, INPUT)
    wiringpi.pinMode(D1, INPUT)
    wiringpi.pinMode(D2, INPUT)
    wiringpi.pinMode(D3, INPUT)
    wiringpi.pinMode(D4, INPUT)
    wiringpi.pinMode(D5, INPUT)
    wiringpi.pinMode(D6, INPUT)
    wiringpi.pinMode(D7, INPUT)


def read_byte(a):
    wiringpi.digitalWrite(ce_pin, True)  # de-assert chip enable
    wiringpi.digitalWrite(oe_pin, True)  # de-assert output enable

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

    wiringpi.digitalWrite(ce_pin, False)  # assert chip enable
    wiringpi.digitalWrite(oe_pin, False)  # assert output enable

    time.sleep(0.00000008)  # wait to make sure the chip is ready

    # read the byte - inverted to account for python list indexing
    d = [
        wiringpi.digitalRead(D7),
        wiringpi.digitalRead(D6),
        wiringpi.digitalRead(D5),
        wiringpi.digitalRead(D4),
        wiringpi.digitalRead(D3),
        wiringpi.digitalRead(D2),
        wiringpi.digitalRead(D1),
        wiringpi.digitalRead(D0)
        ]

    wiringpi.digitalWrite(oe_pin, True)  # de-assert output enable
    wiringpi.digitalWrite(ce_pin, True)  # de-assert chip enable

    return d  # return our bit list

if __name__ == '__main__':

    # open the file
    try:
        binfile = open(sys.argv[1], 'wb')
    except IndexError:
        print('bad filename')
        quit()

    initialize_gpio()  # init gpio

    if input('type "read" to read >> ') != "read":  # prompt for user confirmation
        print('exiting...')
        quit()

    addr = 0  # start the address counter at address 0x0000
    progress = 0
    last_progress = 0
    data_str = ''
    while True:  # main reading loop

        # check to see if we've hit address FFFF yet
        # if we have, we're done
        if addr >= correct_filesize:
            break

        addr_byte_l = [int(x) for x in bin(addr)[2:]]  # convert the address to a byte list
        while len(addr_byte_l) < 16:  # prepend zeroes until we're 16 bits long
            addr_byte_l.insert(0,0)

        data_byte_l = read_byte(addr_byte_l)  # pull the next byte list from gpio

        for i in read_byte(addr_byte_l):  # go thru each element in the list and add it to the data string
            data_str += str(i)

        progress = round(100*(addr/correct_filesize), 1)
        if progress > last_progress:
            print(f'reading: {progress}% complete...', end='\r')  # update status
            last_progress = progress

        addr += 1  # increment address counter

    binfile.write(BitArray(bin=data_str).bytes)  # write the file out
    binfile.close()
    print('read complete!               ')
