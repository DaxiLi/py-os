import time
import GUI
import CPU
import os
import subprocess
from CPU import PSW_IO, PSW_END, PSW_ERROR, PSW_NORMAL, PSW_SCHEDULE
import PCB


DEFAULT_SLISE = 4
DEFAULT_RANK = 10
CLOCK_CIRCLE = 1

class OS:
    ready = False
    PCBNUMS = 0
    waitPCBNUMS = 0
    currentPCB = None
    pid = 1
    clk = 0
    readPCB = []
    waitPCB = []
    cpu = None
    pwd = os.getcwd()
    UI = None

    def __init__(self, ui, cpu):
        print('hello os')
        self.cpu = cpu
        self.UI = ui

    # 处理中断事件
    def interupt(self, detail):
        print('OS intrupt processor!')
        e = detail[0]
        if e == PSW_ERROR:
            self.UI.addTextToTerminalArea("ERROR: " + detail[1])
        elif e == PSW_END:
            self.UI.addTextToTerminalArea("INFO: " + self.currentPCB.pName + " End!")
        elif e == PSW_IO:
            print('----------------')
            self.cpu.save(self.currentPCB)
            self.currentPCB.waitTime = int(detail[1])
            self.addProcessToWaitList(self.currentPCB, self.currentPCB.rank)
            self.currentPCB = self.getNextProcessFromReadyList()
            self.cpu.load(self.currentPCB)
            return
        elif e == PSW_SCHEDULE:
            if self.PCBNUMS == 0:
                return
            self.cpu.save(self.currentPCB)
            self.addProcessToReadyList(self.currentPCB, self.currentPCB.rank)
            self.currentPCB = self.getNextProcessFromReadyList()
            self.cpu.load(self.currentPCB)
            return
        else:
            print('Unknow Interupt!')
            print(detail)
        return


    def refreshStatus(self, slise):
        self.UI.refreshCPU(self.cpu, self.currentPCB.pid, self.clk, slise)

    def refreshUIList(self):
        list_val = []
        l = len(self.waitPCB)
        while l > 0:
            l = l - 1
            list_val.extend(self.waitPCB[l])
        self.UI.refreshList('W', list_val, self.clk)

        list_val = []
        l = len(self.readPCB)
        while l > 0:
            l = l - 1
            list_val.extend(self.readPCB[l])
        self.UI.refreshList('R', list_val, self.clk)

    def loadExecuteFile(self, p, n, rank):
        print('load exec file ' + p)
        f = open(p, encoding='utf-8')
        d = f.read()
        f.close()
        d = d.replace('  ', '').replace('\r', '')
        self.pid = self.pid + 1
        name = str(self.pid) + "_" + n
        ins = d.split('\n')
        pcb = PCB.PCB(self.pid, name, 0, 0, 0, 0, 0, self.clk, 0, ins)
        self.addProcessToReadyList(pcb, rank)
        return n + ' is running pid: ' + str(self.pid)

    def loadBatFile(self, p, n, rank):
        print('load bat file ' + p)
        f = open(p, encoding='utf-8')
        d = f.read()
        f.close()
        ps = d.split('\n')
        retval = ''
        for p in ps:
            # print(p)
            if p.endswith('.if'):
                p1 = os.path.join(self.pwd, p)
            else:
                p1 = os.path.join(self.pwd, p + '.if')
            if os.path.exists(p1):
                # print(p1)
                retval = retval + self.loadExecuteFile(p1, p, rank) + '\n'
        self.refreshUIList()
        return retval

    def initPCBList(self):
        self.readPCB.clear()
        self.waitPCB.clear()
        for i in range(0, DEFAULT_RANK):
            self.readPCB.append([])
            self.waitPCB.append([])

    def getNextProcessFromReadyList(self):
        l = len(self.readPCB)
        # print('l : ' + str(l))
        if l == 0:
            print('---------------------------')
            print('---- ERROR -----------')
        while l > 0:
            l = l - 1
            if len(self.readPCB[l]) == 0:
                continue
            retval = self.readPCB[l][0]
            self.readPCB[l].pop(0)
            self.PCBNUMS = self.PCBNUMS - 1
            return retval

    def addProcessToReadyList(self, pcb, rank=10):
        self.PCBNUMS = self.PCBNUMS + 1
        l = len(self.readPCB)
        if l <= rank:
            for i in range(l, rank + 1):
                self.readPCB.append([])
        self.readPCB[rank].append(pcb)

    def addProcessToWaitList(self, pcb, rank=10):
        self.PCBNUMS = self.waitPCBNUMS + 1
        # pcb.waitTime = 0
        l = len(self.waitPCB)
        if l <= rank:
            for i in range(l, rank + 1):
                self.waitPCB.append([])
        self.waitPCB[rank].append(pcb)

    def powerOnInitFunc(self):
        print('init ready list')
        self.initPCBList()
        pcb = PCB.PCB(1, '1_IDLE', 0, 0, 0, 0, 0, 0, 0, ['nop'], 0)
        self.pid = self.pid + 1
        self.addProcessToReadyList(pcb, 0)
        self.currentPCB = self.getNextProcessFromReadyList()
        self.cpu.load(self.currentPCB)
        self.ready = True
        # self.scheduePCB()

    # 处理 ui 的 command 回调
    def commandCallBack(self, cmd):
        print('command Call Back')
        cmd = cmd.replace('  ', '').lower().split(' ')
        if len(cmd) < 1:
            return "找不到该命令!"
        if cmd[0] == 'ls':
            for root, dirs, files in os.walk(self.pwd, topdown=False):
                r = os.popen('dir')
            return r.read()
        if cmd[0] == 'cd':
            if len(cmd) > 1:
                self.pwd = os.path.join(self.pwd, cmd[1])
                return self.pwd
            else:
                return '缺少必要参数'
        if cmd[0] == 'pwd':
            return self.pwd
        if cmd[0] == 'cls':
            self.UI.clearTextTerminalArea()
            return

        if cmd[0].endswith('.if'):
            arg = 10
            if (len(cmd) > 1):
                arg = cmd[1]
            p = os.path.join(self.pwd, cmd[0])
            if os.path.exists(p):
                return self.loadExecuteFile(p, cmd[0], arg)
        if cmd[0].endswith('.ifs'):
            arg = 10
            if (len(cmd) > 1):
                arg = cmd[1]
            p = os.path.join(self.pwd, cmd[0], arg)
            if os.path.exists(p):
                return self.loadBatFile(p, cmd[0], arg)

        p = os.path.join(self.pwd, cmd[0] + '.if')
        arg = 10
        if (len(cmd) > 1):
            arg = cmd[1]
        if os.path.exists(p):
            return self.loadExecuteFile(p, cmd[0], arg)
        p = os.path.join(self.pwd, cmd[0] + '.ifs')
        if os.path.exists(p):
            return self.loadBatFile(p, cmd[0], arg)
        return "command not found"

    def scheduePCB(self):
        self.currentPCB = self.getNextProcessFromReadyList()
        self.cpu.load(self.currentPCB)

    def runSlise(self):
        global DEFAULT_SLISE
        global CLOCK_CIRCLE
        print(DEFAULT_SLISE)
        for t in range(0, DEFAULT_SLISE):
            if self.UI.isPowerOn() is False:
                return
            self.clk = self.clk + 1
            self.cpu.cpuTime = self.cpu.cpuTime + 1
            self.cpu.clock()
            self.refreshUIList()
            self.refreshStatus(t + 1)
            for l in self.waitPCB:
                for v in l:
                    if v.waitTime == 0:
                        self.addProcessToReadyList(v)
                        l.remove(v)
                        return
                    v.waitTime = v.waitTime - 1
                    v.allWaitTime = v.allWaitTime + 1
            # # 有进程就绪，立刻让出 idle
            if self.cpu.pName == '1_IDLE' and self.PCBNUMS > 0:
                break
            time.sleep(CLOCK_CIRCLE)

    def run(self):
        print("pyos start...")
        while True:
            if self.UI.isPowerOn() is False:
                time.sleep(CLOCK_CIRCLE)
                continue
            if self.ready is False:
                time.sleep(CLOCK_CIRCLE)
                continue
            print('--')
            self.interupt((PSW_SCHEDULE, 'schedule'))
            self.runSlise()
