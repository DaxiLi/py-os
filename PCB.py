

class PCB:
    pid = 0
    pName = "idile"
    PC = 0
    RA = 0
    RB = 0
    RX = 0
    PSW = 0
    startTime = 0
    waitTime = 0
    leftWaitTime = 0
    allWaitTime = 0
    cpuTime = 0
    instruments = []
    dev = 'I/O'
    rank = 10
    # 由于没有内存， 载入时将指令存于数组之中

    def __init__(self, pid, name, ra, rb, rx, psw, pc, start_time, wait_time, ins, rank=10):
        self.pName = name
        self.pid = pid
        self.RA = ra
        self.RB = rb
        self.RX = rx
        self.PSW = psw
        self.startTime = start_time
        self.waitTime = wait_time
        self.PC = pc
        self.instruments = ins
        self.rank = rank


