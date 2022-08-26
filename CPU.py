import re

PSW_NORMAL = 0
PSW_IO = 1
PSW_ERROR = 2
PSW_END = 3
PSW_SCHEDULE = 4
PSW_CALL = 5

INSTRUMENTS = [
    'add',
    'sub',
    'inc'
    'dec',
    'io',
    'end',
    'call',
    'nop',
    'RA',
    'RB',
    'RX',
]

REGISTERS = {
    'ra', 'rb', 'rx', 'psw', 'pc'
}

class CPU:
    PC = 0
    RA = 0
    RB = 0
    RX = 0
    PSW = 0
    cpuTime = 0
    instruments = ['end']
    pName = 'IDLE'
    interruptFunc = None
    instrumentFuncs = None

    def __int__(self):
        print("hello CPU")
        self.interruptFunc = self.defaultInteruptFunc

    def defaultInteruptFunc(self, args):
        print('default interupt')

    def setInteruptFunc(self, f):
        self.interruptFunc = f

    def setPSW(self, status):
        self.PSW = status
        return self.PSW

    def load(self, pcb):
        self.PC = pcb.PC
        self.RA = pcb.RA
        self.RB = pcb.RB
        self.RX = pcb.RX
        self.PSW = pcb.PSW
        self.pName = pcb.pName
        self.cpuTime = pcb.cpuTime
        self.instruments = pcb.instruments

    def clock(self):
        if len(self.instruments) < self.PC:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Unexpected End of File'))
            return
        ins = self.instruments[self.PC]
        self.ALU(ins)
        return

    def save(self, pcb):
        pcb.PC = self.PC
        pcb.RA = self.RA
        pcb.RB = self.RB
        pcb.RX = self.RX
        pcb.setPSW = self.PSW
        pcb.cpuTime = self.cpuTime
        # pcb.instruments = self.instruments

    def setRegisterValue(self, rg, value):
        rgs = {
            'ra': self.setRA,
            'rb': self.setRB,
            'rx': self.setRX,
            'pc': self.setPC,
            'psw': self.setPSW
        }
        func = rgs.get(rg.lower())
        func(value)

    def getRegisterValue(self, rg):
        rgs = {
            'ra': self.getRA,
            'rb': self.getRB,
            'rx': self.getRX,
            'pc': self.getPC,
            'psw': self.getPSW
        }
        func = rgs.get(rg.lower())
        return func()

    def add(self, ins):
        print('ins add')
        if ins is None or len(ins) < 3:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Wrong Instrument!'))
            return
        ra = ins[1]
        rb = ins[2]
        if ins[1] not in REGISTERS or ins[2] not in REGISTERS:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Ubknow Register!\ninstrument:' + ins[1] + ' ' + ins[2]))
            return
        a = self.getRegisterValue(ra)
        b = self.getRegisterValue(rb)
        self.setRegisterValue(ra, a + b)
        self.PC = self.PC + 1

    def sub(self, ins):
        print('sub')
        if ins is None or len(ins) < 3:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Wrong Instrument!'))
            return
        ra = ins[1]
        rb = ins[2]
        if ins[1] not in REGISTERS or ins[2] not in REGISTERS:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Ubknow Register!\ninstrument:' + ins[1] + ' ' + ins[2]))
            return
        a = self.getRegisterValue(ra)
        b = self.getRegisterValue(rb)
        self.setRegisterValue(ra, a - b)
        self.PC = self.PC + 1

    def inc(self, ins):
        print('inc')
        if ins is None or len(ins) < 2:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Wrong Instrument!'))
            return
        ra = ins[1]
        if ins[1] not in REGISTERS:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Ubknow Register!\ninstrument:' + ins[1] + ' ' + ins[2]))
            return
        a = self.getRegisterValue(ra)
        self.setRegisterValue(ra, a + 1)
        self.PC = self.PC + 1

    def dec(self, ins):
        print('des')
        if ins is None or len(ins) < 2:
            self.interruptFunc((self.setPSW(PSW_ERROR), 'Wrong Instrument!'))
            return
        ra = ins[1]
        if ins[1] not in REGISTERS:
            self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1] + ' ' + ins[2]))
            return
        a = self.getRegisterValue(ra)
        self.setRegisterValue(ra, a - 1)
        self.PC = self.PC + 1

    def io(self, ins):
        print('io')
        if ins is None or len(ins) < 2:
            self.interruptFunc((PSW_ERROR, 'Wrong Instrument!'))
            return
        if re.match('^[0-9]*$', ins[1]) is None:
            return self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1]))
        self.PC = self.PC + 1
        print(ins)
        print(self.setPSW(PSW_IO))
        print(PSW_IO)
        # self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1]))
        self.interruptFunc((PSW_IO, ins[1]))


    def end(self, ins):
        print('end')
        self.interruptFunc(('END', ))

    def call(self, ins):
        print('call')
        if len(ins) < 2:
            self.interruptFunc((PSW_ERROR, 'Wrong Instrument!'))
        self.interruptFunc((self.setPSW(PSW_CALL), ins[1]))
        self.PC = self.PC + 1

    def NOP(self, ins):
        print('NOP')

    def iRA(self, ins):
        print('AX')
        if len(ins) < 2:
            self.interruptFunc((PSW_ERROR, 'Wrong Instrument!'))
        if re.match('^[0-9]*$', ins[1]) is None:
            self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1]))
            return
        self.setRegisterValue('ra', int(ins[1]))
        self.PC = self.PC + 1

    def iRB(self, ins):
        print('BX')
        if len(ins) < 2:
            self.interruptFunc((PSW_ERROR, 'Wrong Instrument!'))
        if re.match('^[0-9]*$', ins[1]) is None:
            self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1]))
            return
        self.setRegisterValue('rb', int(ins[1]))
        self.PC = self.PC + 1

    def iRX(self, ins):
        print('RX')
        if len(ins) < 2:
            self.interruptFunc((PSW_ERROR, 'Wrong Instrument!'))
        if re.match('^[0-9]*$', ins[1]) is None:
            self.interruptFunc((PSW_ERROR, 'Ubknow Register!\ninstrument:' + ins[1]))
            return
        self.setRegisterValue('rx', int(ins[1]))
        self.PC = self.PC + 1

    ## 处理指令，将 类似于  ADD AX, BX 的指令解析返回 ["add","ax","bx"] 的元组
    def parseOpt(self, opt):
        if len(str(opt)) == 0:
            return ['nop']
        ins = str(opt).replace(',', ' ').replace('=', ' ').replace('  ', '').lower().split(' ')
        for val in ins:
            val = val.replace(' ', '')

        if len(ins) < 1 and ins[0] not in INSTRUMENTS:
            return False
        return ins

    def ALU(self, opt):
        mins = self.parseOpt(opt)
        if self.instrumentFuncs is None:
            self.instrumentFuncs = {
                'add': self.add,
                'sub': self.sub,
                'inc': self.inc,
                'dec': self.dec,
                'io': self.io,
                'end': self.end,
                'call': self.call,
                'nop': self.NOP,
                'ra': self.iRA,
                'rb': self.iRB,
                'rx': self.iRX
            }
        if mins is False:
            self.interruptFunc((PSW_ERROR, 'Wrong instrument!\n' + mins[0]))
            return
        func = self.instrumentFuncs.get(mins[0], 'nop')
        func(mins)

    def setRA(self, v):
        self.RA = v

    def setRB(self, v):
        self.RB = v

    def setRX(self, v):
        self.RX = v

    def setPC(self, v):
        self.PC = v

    def setPSW(self, v):
        self.PSW = v

    def getRA(self):
        return self.RA

    def getRB(self):
        return self.RB

    def getRX(self):
        return self.RX

    def getPC(self):
        return self.PC

    def getPSW(self):
        return self.PSW
