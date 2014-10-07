#!/usr/bin/python
from Adafruit_BBIO.SPI import SPI
import time
import random
import os

class ledstrip:
    
    def __init__(self, length, missing):
        # the important piece of this for reuse is setting up the interface
        # the rest sets up the strip of leds for what we intend to do with them
        self.interface = SPI(0,1)
        self.full_length = length
        self.missing_leds = missing
        self.outbuff = [[128, 128, 128]] * length
        self.reset_buffer([128, 128, 128])
        
    def reset_buffer(self, color):
        for i in range(0, len(self.outbuff), 1):
            self.outbuff[i] = color

    def write(self):
        # this guy here, plus a small amount of init code elsewhere,
        # is all we really need to make the led strips work. The rest is just
        # for ease of use.
        self.interface.writebytes([0] * (int(self.full_length / 32) + 1) + [0])
        for i in range(0, len(self.outbuff), 1):
	    if not i in self.missing_leds:
                self.interface.writebytes(self.outbuff[i])

    def twocolorfade(self, bcolor, tcolor, length):
        outcolor = []
        totalshift = [0, 0, 0]
        for i in range(0, 3, 1):
            totalshift[i] = tcolor[i] - bcolor[i]
        for i in range(0, length, 1):
            outcolor.append([])
            for j in range(0, 3, 1):
                outcolor[i].append(bcolor[j] + (int(totalshift[j] / float(length) * i)))
        return outcolor

    def movingtwocolor(self, bcols, tcols, strip_length, gradient_width, delay):
        bfade = self.twocolorfade(bcols[0], bcols[1], gradient_width)
        for frame in bfade:
            seg1 = self.twocolorfade(frame, tcols[0], strip_length)
            seg2 = [] + seg1
            seg2.reverse()
            self.outbuff = seg1 + seg2 + seg1
            self.write()
            time.sleep(delay)
        bfade = self.twocolorfade(tcols[0], tcols[1], gradient_width)
        for frame in bfade:
            seg1 = self.twocolorfade(bcols[1], frame, strip_length)
            seg2 = [] + seg1
            seg2.reverse()
            self.outbuff = seg1 + seg2 + seg1
            self.write()
            time.sleep(delay)
        bfade = self.twocolorfade(tcols[1], tcols[0], gradient_width)
        for frame in bfade:
            seg1 = self.twocolorfade(bcols[1], frame, strip_length)
            seg2 = [] + seg1
            seg2.reverse()
            self.outbuff = seg1 + seg2 + seg1
            self.write()
            time.sleep(delay)
        bfade = self.twocolorfade(bcols[1], bcols[0], gradient_width)
        for frame in bfade:
            seg1 = self.twocolorfade(frame, tcols[0], strip_length)
            seg2 = [] + seg1
            seg2.reverse()
            self.outbuff = seg1 + seg2 + seg1
            self.write()
            time.sleep(delay)

            
    def run_sequence(self, fcol, bcol, length, delay, sequence, step, loops, timechange):
        # with run_sequence, we can do pretty much anything, 
        # provided we can set up the sequence properly
        # long list of parameters gives us what we need to make that happen
        # fcol : foreground color (the color value for the leds in sequence)
        # bcol : background color (the color value for the leds not in sequence)
        # length : number of leds still active trailing the "current" one in sequence
        # delay : time between steps in sequence
        # sequence : a list (processed in the order provided) of leds to activate
        # step : number of leds in sequence to skip per step (useful for moving a whole group at once)
        # loops : number of times to iterate through the sequence completely
        # timechange : somewhat handy but not wholly necessary per loop multiplier for delay variable
        #              can be used to increase or decrease timestep over several loops without re-running sequence
        pos = 0
        loops = loops - 1
        firstrun = True
        self.reset_buffer(bcol)
        while pos < len(sequence):
            self.reset_buffer(bcol)
            for tail in range(0, length, 1):
                if pos - tail >= 0 or not firstrun:    
                    self.outbuff[sequence[pos - tail]] = fcol
            if pos < len(sequence):
                if pos == len(sequence) - 1 and loops:
                    pos = 0
                    firstrun = False
                    loops = loops - 1
                    delay = delay * timechange
                elif pos == len(sequence) - 1 and length:
                    length = length - 1
                else:
                    pos = pos + step
            time.sleep(delay)
            self.write()
        self.reset_buffer(bcol)
        self.write()

def init_and_run():
    os.system('echo BB-SPI0-HL1606 > //sys//devices//bone_capemgr.9//slots')
    maxlength = 156
    missing_addresses = []
    hled = ledstrip(maxlength, missing_addresses)
    seg1, seg2, seg3 = range(0, 52, 1), range(52, 104, 1), range(104, maxlength, 1)
    fseq = seg1 + seg2 + seg3
        
    #single trail up/down/up
    hled.run_sequence([(128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127))],
                      [(128 + int(random.random()*60)),
                       (128 + int(random.random()*60)),
                       (128 + int(random.random()*60))],
                      7, 0.01, fseq, 1, 3, 0.2)
    
    seg2.reverse()
    fseq = seg1 + seg2 + seg3
    
    #single trail up/up/up
    hled.run_sequence([(128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127))],
                      [(128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40))],
                      9, 0.01, fseq, 1, 3, 0.2) 
        
    fseq = [seg1[0]] + [seg2[0]] + [seg1[1]] + [seg2[1]]
    for i in range(0, len(seg1) - 2, 1):
        fseq = fseq + [seg1[i + 2]] + [seg2[i + 2]] + [seg3[i]]

    #travel upware in spiral
    hled.run_sequence([(128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127))],
                      [(128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40))],
                      12, 0.05, fseq, 1, 3, 0.5)

    #travel upward in ring
    for i in range(1, len(seg1) - 3, 2):
        hled.run_sequence([(128 + int(random.random() * 127)),
                           128 + (i*2), (128 + int(random.random() * 127))],
                          [128, 128, 128], 9 + (i * 3), 0.05 / (10**i),
                          fseq, 3, 1, 1)

    #pulse red/orange
    for i in range(0, 10, 1):
        hled.reset_buffer([150, 255, 128])
        hled.write()
        time.sleep(0.5)
        hled.reset_buffer([128, 255, 128])
        hled.write()
        time.sleep(0.5)

    hled.movingtwocolor([[150, 255, 128], [128, 128, 255]],
                        [[128, 128, 255], [150, 255, 128]], 52, 50, 0.01)
    """#fade between two top/bottom colors
    bcols = [[(128+int(random.random()*127)),
              (128+int(random.random()*127)),
              (128+int(random.random()*127))],
             [(128+int(random.random()*127)),
              (128+int(random.random()*127)),
              (128+int(random.random()*127))]]
    tcols = [[(128+int(random.random()*127)),
              (128+int(random.random()*127)),
              (128+int(random.random()*127))],
             [(128+int(random.random()*127)),
              (128+int(random.random()*127)),
              (128+int(random.random()*127))]]
    hled.movingtwocolor(bcols, tcols, 52, 50, 0.1)
    """
    fseq = []
    for i in range(0, 26, 1):
	fseq = fseq + [i] + [103 - i] + [104 + i] + [51 - i] + [52 + i] + [152 - i]
    fseq2 = [] + fseq
    fseq2.reverse()
    fseq = fseq + fseq2
    
    hled.run_sequence([(128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127)),
                       (128 + int(random.random() * 127))],
                      [(128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40)),
                       (128 + int(random.random() * 40))],
                      6, 0.05, fseq, 6, 4, 0.75)

while 1:
    init_and_run()
