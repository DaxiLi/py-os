import re
import time
import os
from CPU import PSW_IO, PSW_END, PSW_ERROR, PSW_NORMAL, PSW_SCHEDULE, PSW_NEXT
import PCB

DEFAULT_SLISE = 4
DEFAULT_RANK = 10
CLOCK_CIRCLE = 1


class OS:
    ready = False
    waitPCBNUMS = 0
    currentPCB = None
    pid = 1
    clk = 0
    level = 0
    currentList = []
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
            self.UI.addTextToTerminalArea("Warning: [ ERROR ] pid: {pid} 异常结束！\n".format(pid=self.currentPCB.pid))
            return self.interupt((PSW_NEXT,))
        elif e == PSW_END:
            self.UI.addTextToTerminalArea("INFO: \t[ END ]      \t " + self.currentPCB.pName + " 运行结束!\n")
            self.interupt((PSW_NEXT,))
            return
        elif e == PSW_IO:
            print('----------------')
            self.UI.addTextToTerminalArea("INFO: \t[ IO ] Device: " + str(detail[2]) + " pid/ " + str(self.currentPCB.pid) + "需耗时" + str(detail[1]) + "\n" )
            self.cpu.save(self.currentPCB)
            self.currentPCB.dev = detail[2]
            self.currentPCB.leftWaitTime = int(detail[1])
            self.currentPCB.waitTime = 0
            self.addProcessToWaitList(self.currentPCB, self.currentPCB.rank)
            self.interupt((PSW_NEXT,))
            return
        elif e == PSW_SCHEDULE:
            if self.getPCBNums() == 0:
                return
            self.UI.addTextToTerminalArea("INFO: \t[ SCHEDULE 1 ] \t 换出 -- pid/ " + str(self.currentPCB.pid) + "进程\n")
            self.cpu.save(self.currentPCB)
            self.addProcessToReadyList(self.currentPCB, self.currentPCB.rank)
            self.currentPCB = self.getNextProcessFromReadyList()
            self.UI.addTextToTerminalArea("INFO: \t[ SCHEDULE 2 ] \t 换进 ++ pid/ " + str(self.currentPCB.pid) + "进程\n" )
            self.cpu.load(self.currentPCB)
            return
        elif e == PSW_NEXT:
            self.UI.addTextToTerminalArea("INFO: \t[ SCHEDULE ] \t 切换进程 ** pid/ " + str(self.currentPCB.pid) + "\n" )
            self.currentPCB = self.getNextProcessFromReadyList()
            self.cpu.load(self.currentPCB)
            return
        else:
            print('Unknow Interupt!')
            print(detail)
        return

    # 刷新当前进程的信息，最顶部那个 UI
    def refreshStatus(self, slise):
        self.UI.refreshCPU(self.cpu, self.currentPCB.pid, self.clk, slise)

    # 刷新中间的，就绪和等待队列 UI
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

    # 加载可执行文件
    def loadExecuteFile(self, p, n, rank):
        print('load exec file ' + p)
        print("rank " + str(rank))
        if re.match('^[0-9]*$', str(rank) ) is None:
            rank = 10
        else:
            rank = int(rank)
        f = open(p, encoding='utf-8')
        d = f.read()
        f.close()
        d = d.replace('  ', '').replace('\r', '')
        self.pid = self.pid + 1
        name = str(self.pid) + "_" + n
        ins = d.split('\n')
        pcb = PCB.PCB(self.pid, name, 0, 0, 0, 0, 0, self.clk, 0, ins, rank)
        self.addProcessToReadyList(pcb, rank)
        return "INFO: \t[ CREATE ] \t" + n + ' is running pid: ' + str(self.pid)

    # 加载批处理文件
    def loadBatFile(self, p, n, rank=10):
        print('load bat file ' + p)
        print("rank " + str(rank))
        if re.match('^[0-9]*$', str(rank)) is None:
            rank = 10
        else:
            rank = int(rank)
        f = open(p, encoding='utf-8')
        d = f.read()
        f.close()
        ps = d.split('\n')
        retval = ''
        for line in ps:
            line = line.replace("  ", '').strip()
            names = line.split(' ')
            if len(names) == 2:
                if re.match('^[0-9]*$', names[1]) is not None:
                    rank = int(names[1])
            if line.endswith('.if'):
                p1 = os.path.join(self.pwd, names[0])
            else:
                p1 = os.path.join(self.pwd, names[0] + '.if')
            if os.path.exists(p1):
                retval = retval + self.loadExecuteFile(p1, names[0], rank) + '\n'
        self.refreshUIList()
        return retval

    # 初始化 PCB List，清空，初始化即可
    def initPCBList(self):
        self.readPCB.clear()
        self.waitPCB.clear()
        for i in range(0, DEFAULT_RANK):
            self.readPCB.append([])
            self.waitPCB.append([])

    # 从 就绪列表中 ，根据优先级，从高到低，返回下一个 PCB
    def getNextProcessFromReadyList(self):
        num = self.getPCBNums()
        if num == 0:
            retval = self.readPCB[0][0]
            self.readPCB[0].pop(0)
            return retval
        while len(self.currentList) == 0:
            if self.level <= 1:
                self.level = len(self.readPCB) - 1
            else:
                self.level = self.level - 1
            self.currentList.extend(self.readPCB[self.level])
        retval = self.currentList[0]
        self.currentList.pop(0)
        self.readPCB[self.level].pop(0)
        return retval

    # 将 PCB 重新加到就绪队列 尾部
    def addProcessToReadyList(self, pcb, rank=10):
        # self.PCBNUMS = self.PCBNUMS + 1
        l = len(self.readPCB)
        if l <= int(rank):
            for i in range(l, rank + 1):
                self.readPCB.append([])
        self.readPCB[rank].append(pcb)

    # 将 PCB 加到等待队列尾部
    def addProcessToWaitList(self, pcb, rank=10):
        # self.PCBNUMS = self.waitPCBNUMS + 1
        # pcb.waitTime = 0
        l = len(self.waitPCB)
        if l <= rank:
            for i in range(l, rank + 1):
                self.waitPCB.append([])
        self.waitPCB[rank].append(pcb)

    def getPCBNums(self):
        ct = 0
        for i in range(1, len(self.readPCB)):
            for v in self.readPCB[i]:
                ct = ct + 1
        return ct

    # 开机回调函数，开机时调用，做初始化工作，
    # 主要初始化 就学队列
    # 创建 idle 进程
    def powerOnInitFunc(self):
        print('init ready list')
        self.pid = 1
        self.clk = 0
        self.level = 0
        self.currentList.clear()
        self.pwd = os.getcwd()
        self.waitPCBNUMS = 0
        self.initPCBList()
        pcb = PCB.PCB(1, '1_IDLE', 0, 0, 0, 0, 0, 0, 0, ['nop'], 0)
        self.pid = self.pid + 1
        self.addProcessToReadyList(pcb, 0)
        self.currentPCB = self.getNextProcessFromReadyList()
        self.cpu.load(self.currentPCB)
        self.ready = True

    # 处理 ui 的 command 回调
    # 比较粗糙，也不想费神分离出来
    # 处理 command ，并执行命令，返回 结果 字符串显示在底部控制台
    def commandCallBack(self, cmd):
        print('command Call Back')
        d_cmd = cmd.replace('  ', '').lower().split(' ')
        if len(d_cmd) < 1:
            return "找不到该命令!"
        if d_cmd[0] == 'ls':
            r = os.popen('dir')
            return r.read()
        if d_cmd[0] == 'cd':
            if len(d_cmd) > 1:
                self.pwd = os.path.join(self.pwd, d_cmd[1])
                return self.pwd
            else:
                return '缺少必要参数'
        if d_cmd[0] == 'pwd':
            return self.pwd
        if d_cmd[0] == 'cls':
            self.UI.clearTextTerminalArea()
            return
        if d_cmd[0].endswith('.if'):
            arg = 10
            if (len(d_cmd) > 1):
                arg = d_cmd[1]
            p = os.path.join(self.pwd, d_cmd[0])
            if os.path.exists(p):
                return self.loadExecuteFile(p, d_cmd[0], arg)
        if d_cmd[0].endswith('.ifs'):
            arg = 10
            if (len(d_cmd) > 1):
                arg = d_cmd[1]
            p = os.path.join(self.pwd, d_cmd[0], arg)
            if os.path.exists(p):
                return self.loadBatFile(p, d_cmd[0], arg)
        p = os.path.join(self.pwd, d_cmd[0] + '.if')
        arg = 10
        if (len(d_cmd) > 1):
            arg = d_cmd[1]
        if os.path.exists(p):
            return self.loadExecuteFile(p, d_cmd[0], arg)
        p = os.path.join(self.pwd, d_cmd[0] + '.ifs')
        if os.path.exists(p):
            return self.loadBatFile(p, d_cmd[0], arg)
        r = os.popen(cmd)
        return r.read()
        return "command not found"

    # 时间片，执行一个时间片后返回
    def runSlise(self):
        global DEFAULT_SLISE
        global CLOCK_CIRCLE
        print(DEFAULT_SLISE)
        for t in range(0, DEFAULT_SLISE):
            # 关机了就直接返回
            if self.UI.isPowerOn() is False:
                return
            # 有进程就绪，立刻让出 idle
            if self.cpu.pName == '1_IDLE' and self.getPCBNums() > 0:
                self.interupt((PSW_SCHEDULE, ))
                return
            # 总时钟 +1
            self.clk = self.clk + 1
            # 当前进程 cpu 时间 +1
            self.cpu.cpuTime = self.cpu.cpuTime + 1
            # 执行一条语句
            self.cpu.clock()
            # 刷新 UI
            self.refreshUIList()
            self.refreshStatus(t + 1)
            # 把 wait 队列中的 PCB ，等待时间 -1 ，减到0，移出等待队列
            devices = []
            for l in self.waitPCB:
                for v in l:
                    # 剩余时间 为 0 则移除队列
                    if v.leftWaitTime <= 0:
                        self.addProcessToReadyList(v)
                        l.remove(v)
                        return
                    # 已等待时间 +1
                    v.waitTime = v.waitTime + 1
                    # 总 io 时间 +1
                    v.allWaitTime = v.allWaitTime + 1 
                    if v.dev in devices:
                        continue
                    devices.append(v.dev)
                    # 剩余时间 -1
                    v.leftWaitTime = v.leftWaitTime - 1
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
            self.interupt((PSW_SCHEDULE, 'schedule'))
            self.runSlise()
