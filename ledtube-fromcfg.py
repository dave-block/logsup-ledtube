#!/usr/bin/env python
from Adafruit_BBIO.SPI import SPI as spi
from os import system
import random
import time

class LightFromConfig:

    allOff = [128,128,128]
    
    class RunSequenceParams:

        params = {'ForeColor' : '',
                  'BackColor' : '',
                  'ForeLength' : '',
                  'Timestep' : '',
                  'LightSequence' : '',
                  'SequenceStep' : '',
                  'NumberOfLoops' : '',
                  'PerLoopTimestepMod' : ''}
        
        def __init__(self):
            self['ForeColor'] = [255,255,255] #FLAGGED
            self['BackColor'] = [128,128,128] #FLAGGED
            self['ForeLength'] = 0
            self['Timestep'] = 0.05
            self['LightSequence'] = []
            self['SequenceStep'] = 1
            self['NumberOfLoops'] = 1
            self['PerLoopTimestepMod'] = 1

        def __setitem__(self, key, val):
            if key in self.params:
                self.params[key] = val

        def __getitem__(self, key):
            if key in self.params:
                return self.params[key]

        def setParameters(**kwparams):
            for key in kwparams:
                if key in self.params:
                    self['key'] = val
        
    def __init__(self, length):
	self.processBlock = {'RunSequence' : self.processRunSequence, 
				'WriteRange' : self.processWriteRange, 
				'Wait' : self.processWait, 
				'Loop' : self.processLoop }
        self.full_length = length
        self.outbuff = [self.allOff] * length
        self.hRunSequenceParams = self.RunSequenceParams()
        #self.clear_buffer()

    def write(self):
        t = spi(0,1)
        t.writebytes([0,0,0,0,0])
        for i in self.outbuff:
            t.writebytes(i)
        t.close()

    def reset_buffer(self):
	for i in range(0, len(self.outbuff), 1):
            self.outbuff[i] = self.allOff

    def processWriteRange(self):
        return        

    def processWait(self):
	return

    def processRunSequence(self, action, **kwparams):
        if action == 'GET':
            return self.hRunSequenceParams.params
        elif action == 'UPDATE':
            for key in kwparams:
                if '[' in kwparams[key]:
                    plist = kwparams[key].strip('[]').split(',')
                    kwparams[key] = []
                    for p in plist:
                        kwparams[key].append(int(p))
                elif '.' in kwparams[key]:
		    kwparams[key] = float(kwparams[key])
		else:
                    kwparams[key] = int(kwparams[key])
                self.hRunSequenceParams[key] = kwparams[key]
        elif action == 'RUN':
            if 'debug' in kwparams and kwparams['debug']:
                print '\nRunning with:'
                for p in self.hRunSequenceParams.params:
                    print p + ' : ' + str(self.hRunSequenceParams[p])
                return
            pos = 0
            loops = self.hRunSequenceParams['NumberOfLoops'] - 1
            delay = self.hRunSequenceParams['Timestep']
            length = self.hRunSequenceParams['ForeLength']
            firstrun = True
            self.reset_buffer()
            while pos < len(self.hRunSequenceParams['LightSequence']):
                self.reset_buffer()
                for tail in range(0, length, 1):
                    if pos - tail >= 0 or not firstrun:    
                        self.outbuff[self.hRunSequenceParams['LightSequence'][pos - tail]] = self.hRunSequenceParams['ForeColor']
                if pos < len(self.hRunSequenceParams['LightSequence']):
                    if pos == len(self.hRunSequenceParams['LightSequence']) - 1 and loops:
                        pos = 0
                        firstrun = False
                        loops = loops - 1
                        delay = delay * self.hRunSequenceParams['PerLoopTimestepMod']
                    elif pos == len(self.hRunSequenceParams['LightSequence']) - 1 and length:
                        length = length - 1
                    else:
                        pos = pos + self.hRunSequenceParams['SequenceStep']
                #time.sleep(delay)
                self.write()
            self.reset_buffer()
            self.write()

    def processLoop(self, action, **kwparams):
        if action == 'GET':
            return self.hLoopParams.params
        elif action == 'UPDATE':
            for key in kwparams:
                self.hLoopParams[key] = kwparams[key]
        elif action == 'RUN':
            print "Not implemented. Find a way to not make this ruin everything."
            return

    def parseBlock(self, hFile, parent=''):
        curBlock = parent
        if curBlock:
            curBlockParams = self.processBlock[curBlock]('GET')
        while 1:
            cPos = hFile.tell()
            line = hFile.readline()
            print parent + ': ' + line.strip('\n')
            if not line:
                break
            if '#' in line: #drop comments immediately
                line = line[:line.find('#')]
            if '{' in line: #possible function block found, verify and run
                functionBlock = line[:line.find('{')].strip()
                if functionBlock in self.processBlock:
                    curBlockParams = self.processBlock[functionBlock]('GET')
                    blockStart = cPos
                    blockEnd = self.parseBlock(hFile, functionBlock)
                else:
                    return -1                
                #blockend = parseBlock(hFile, level + 1)
            elif parent:
                if line[:line.find('=')].strip() in curBlockParams:
                    #check for non-param keywords
                    lineExpansion = line[line.find('=')+1:].strip().lower()
                    while 'random' in lineExpansion:
                        randexp = lineExpansion[
                                                lineExpansion.find('(', lineExpansion.find('random'))+1 :
                                                lineExpansion.find(')', lineExpansion.find('random'))
                                                ].split(',')
                        if not len(randexp) == 2:
                            #error out
                            print "Random value not set up properly at location " + str(cPos)
                            os.exit()
                        randexp = str(int(random.random() * (int(randexp[1]) - int(randexp[0])) + int(randexp[0])))
                        lineExpansion = lineExpansion[:lineExpansion.find('random')] + randexp + lineExpansion[lineExpansion.find(')', lineExpansion.find('random'))+1:]
                    while 'range' in lineExpansion[lineExpansion.find('=')+1:].strip().lower():
                        rangexp = lineExpansion[
                                                lineExpansion.find('(', lineExpansion.find('range'))+1 :
                                                lineExpansion.find(')', lineExpansion.find('range'))
                                                ].split(',')
                        if not len(rangexp) == 3:
                            #error out
                            print "Range value not set up properly at location " + str(cPos)
                        rangexp = str(range(int(rangexp[0]), int(rangexp[1]), int(rangexp[2]))).strip('[]')
                        lineExpansion = '[' + lineExpansion[:lineExpansion.find('range')] + rangexp + lineExpansion[lineExpansion.find(')', lineExpansion.find('range'))+1:] + ']'
                    lineParam = {line[:line.find('=')] : lineExpansion}
		    self.processBlock[curBlock]('UPDATE', **lineParam)
                if '}' in line:
                    self.processBlock[curBlock]('RUN')
                    return hFile.tell()
                
def init_and_run():
    print 'test'
    system('echo BB-SPI0-01 > //sys//devices//bone_capemgr.9//slots')
    print 'test2'
    hlfcfg = LightFromConfig(160)
    hcfgfile = open(r'testcfg.cfg', 'r')
    hlfcfg.parseBlock(hcfgfile)

init_and_run()
