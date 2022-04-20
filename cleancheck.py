import os,sys,time,wiringpi

# This script checks if the EEPROM has been erased properly.
# Due to hardware limitations, the EEPROM must be erased with external hardware.

# usage: python3 eeprom_cleancheck.py

# pin 7 and 9 on my raspi are broken

# EEPROM size
correct_filesize = 65536

# eeprom pin assignments
A0  = 3
A1  = 2
A2  = 0
A3  = 12
A4  = 13
A5  = 14
A6  = 30
A7  = 21
A8  = 22
A9  = 23
A10 = 24
A11 = 25
A12 = 7
A13 = 9
A14 = 8
A15 = 1

D0  = 28
D1  = 29
D2  = 27
D3  = 26
D4  = 11
D5  = 31
D6  = 10
D7  = 6

ce_pin = 4
oe_pin = 5

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

    initialize_gpio()  # init gpio

    if input('type "check" to check >> ') != "check":  # prompt for user confirmation
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

        data_byte_l = read_byte(addr_byte_l)  # pull the next byte list

        if 0 in data_byte_l:  # all bits should be 1. if we see a 0, we fail
            print(f'FAILED: {hex(addr)}: {data_byte_l}')
            quit()

        progress = round(100*(addr/correct_filesize), 1)
        if progress > last_progress:
            print(f'checking: {progress}% complete...', end='\r')  # update status
            last_progress = progress

        addr += 1  # increment address counter

    print('PASS                        ')
