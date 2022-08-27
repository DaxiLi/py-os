
from tkinter import *


import CPU


def terminalFrame():
    print('draw terminal Frame')


class DeskTop:
    # DeskTop = None
    DeskTop = Tk()
    topFrame = None
    midFrame = None
    terminalBox = None
    window_width = 1000

    commandCallBackFunc = None
    powerOnInitFunc = None

    # topFrame  item
    Power = False
    TextPower = '开机'
    TextProcessName = StringVar()
    TextCurrentInstrument = StringVar()
    TextRegisterX = StringVar()
    TextPID = StringVar()
    TextRegisterA = StringVar()
    TextRegisterB = StringVar()
    TextRank = StringVar()
    TextTimeClock = StringVar()
    TextTimeSlice = StringVar()
    TextCPUTime = StringVar()
    ButtonPower = False

    # mid Frame
    ListboxReady = None
    ListboxReadyPidList = None
    ListboxReadyWaitTimeList = None
    ListboxReadyProcessNameList = None
    ListboxReadyWaitAllTimeList = None
    ListboxReadyCPUTimeList = None
    ListboxReadyLevelList = None

    ListboxWait = None
    ListboxWaitPidList = None
    ListboxWaitWaitTimeList = None
    ListboxWaitProcessNameList = None
    ListboxWaitAllTimeList = None
    ListboxWaitWaitReason = None
    ListboxWaitCPUTimeList = None

    # terminal Frame
    TextAreaTerminalBox = None
    inputTerminalInputBox = StringVar()
    commandEntry = None

    def __init__(self):
        print("init")
        self.mainFrame()

    def isPowerOn(self):
        return self.Power

    def setPowerOnInitFunc(self, f):
        self.powerOnInitFunc = f

    def setCommandCallBackFunc(self, f):
        self.commandCallBackFunc = f

    def refreshCPU(self, cpu, pid, clk, slice):
        print('refresh status')
        self.TextProcessName.set(cpu.pName)
        self.TextPID.set(pid)
        self.TextRegisterA.set('{:04x}'.format(cpu.RA))
        self.TextRegisterB.set('{:04x}'.format(cpu.RB))
        self.TextRegisterX.set('{:04x}'.format(cpu.RX))
        self.TextCurrentInstrument.set(cpu.instruments[cpu.PC])
        self.TextCPUTime.set(cpu.cpuTime)
        self.TextTimeClock.set(str(clk))
        self.TextTimeSlice.set(str(slice))

    def refreshList(self, list_name, list_value, clk):
        if list_name == 'R':
            self.ListboxReadyPidList.delete(0, "end")
            self.ListboxReadyProcessNameList.delete(0, 'end')
            self.ListboxReadyWaitTimeList.delete(0, 'end')
            self.ListboxReadyCPUTimeList.delete(0, 'end')
            self.ListboxReadyWaitAllTimeList.delete(0, 'end')
            self.ListboxReadyLevelList.delete(0, 'end')
            for val in list_value:
                self.ListboxReadyPidList.insert('end', val.pid)
                self.ListboxReadyProcessNameList.insert('end', val.pName)
                self.ListboxReadyWaitTimeList.insert('end', val.waitTime)
                self.ListboxReadyCPUTimeList.insert('end', val.cpuTime)
                self.ListboxReadyWaitAllTimeList.insert('end', clk - val.startTime)
                self.ListboxReadyLevelList.insert('end', val.rank)
        elif list_name == 'W':
            self.ListboxWaitPidList.delete(0, "end")
            self.ListboxWaitProcessNameList.delete(0, 'end')
            self.ListboxWaitWaitTimeList.delete(0, 'end')
            self.ListboxWaitWaitReason.delete(0, 'end')
            self.ListboxWaitAllTimeList.delete(0, 'end')
            self.ListboxWaitCPUTimeList.delete(0, 'end')
            for val in list_value:
                self.ListboxWaitPidList.insert('end', val.pid)
                self.ListboxWaitProcessNameList.insert('end', val.pName)
                self.ListboxWaitWaitTimeList.insert('end', val.waitTime)
                self.ListboxWaitWaitReason.insert('end', 'IO')
                self.ListboxWaitCPUTimeList.insert(0, val.cpuTime)
                self.ListboxWaitAllTimeList.insert(0, clk - val.startTime)
        else:
            print('unknow list name ' + str(list_name))

    def powerToggle(self, btn):
        print("power toggle")
        self.refreshList('W', [], 0)
        self.refreshList('R', [], 0)
        self.clearTextTerminalArea()
        if self.Power:
            btn['text'] = '开机'
            btn['bg'] = 'green'
            self.setPower(False)
            self.commandEntry['state'] = 'disable'
        else:
            btn['text'] = '关机'
            btn['bg'] = 'red'
            self.setPower(True)
            self.commandEntry['state'] = 'normal'
            self.terminalWelCom()
            if self.powerOnInitFunc:
                self.powerOnInitFunc()

    def setPower(self, status):
        self.Power = status
        self.refreshCPU(CPU.CPU(), '', 0, 0)

    def mainFrame(self):
        self.DeskTop.title("pyos")
        self.DeskTop.geometry("1000x920")
        self.topFrame()
        self.midFrame()
        self.terminalBox()

    def topFrame(self):
        print("draw status Frame")
        self.topFrame = Frame(self.DeskTop, width=self.window_width, height=200)

        px = 5
        py = 10
        left = Frame(self.topFrame, width=self.window_width, height=100)
        left.pack(fill=NONE, side=LEFT)
        c = 1
        r = 1
        Label(left, text="pid").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextPID).grid(column=c, row=r + 1,
                                                                                                 padx=px, pady=py)
        c = c + 1

        Label(left, text="当前进程名").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextProcessName).grid(column=c, row=r + 1,
                                                                                                 padx=px, pady=py)
        # self.TextProcessName.set('SYSTEM')
        c = c + 1

        Label(left, text="当前指令:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextCurrentInstrument).grid(column=c,
                                                                                                       row=r + 1,                                                                                           padx=10, pady=10)
        # self.TextCurrentInstrument.set("NOP")
        c = c + 1

        Label(left, text="优先级:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextRank).grid(column=c,
                                                                                                       row=r + 1,                                                                                           padx=10, pady=10)
        self.TextRank.set("0")
        c = c + 1

        Label(left, text="寄存器X:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextRegisterX).grid(column=c, row=r + 1,
                                                                                               padx=10, pady=py)
        self.TextRegisterX.set("0000")
        c = c + 1

        Label(left, text="寄存器A:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextRegisterA).grid(column=c, row=r + 1,
                                                                                               padx=10, pady=py)
        self.TextRegisterA.set("0000")
        c = c + 1

        Label(left, text="寄存器B:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextRegisterB).grid(column=c, row=r + 1,
                                                                                               padx=10, pady=py)
        self.TextRegisterB.set("0000")
        c = c + 1

        Label(left, text="总时钟周期:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextTimeClock).grid(column=c, row=r + 1,
                                                                                               padx=px, pady=py)
        self.TextTimeClock.set('0')
        c = c + 1

        Label(left, text="已运行:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextCPUTime).grid(column=c, row=r + 1,
                                                                                               padx=px, pady=py)
        self.TextCPUTime.set('0')
        c = c + 1

        Label(left, text="时间片:").grid(column=c, row=r, padx=px, pady=py)
        Label(left, height=1, relief='raised', width=10, textvariable=self.TextTimeSlice).grid(column=c, row=r + 1,
                                                                                               padx=px, pady=py)
        self.TextTimeSlice.set('0')
        c = c + 1

        b = Button(self.topFrame, width=10, height=2, text=self.TextPower)
        b['command'] = lambda: self.powerToggle(b)
        b.pack(side=RIGHT)
        # self.TextPower.set('On')
        b['text'] = '开机'

        self.topFrame.pack()

    def midFrame(self):
        print("draw processFrame")
        self.midFrame = Frame(self.DeskTop, width=self.window_width, height=400)

        leftFrame = LabelFrame(self.midFrame, text="就绪队列", width=int(self.window_width / 2), height=400)
        leftFrame.pack(side=LEFT, padx=10)

        l = LabelFrame(leftFrame, text='PID', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxReadyPidList = Listbox(l, height=21, width=10)
        self.ListboxReadyPidList.pack(side=LEFT)

        l = LabelFrame(leftFrame, text='进程名', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxReadyProcessNameList = Listbox(l, height=21, width=10)
        self.ListboxReadyProcessNameList.pack(side=LEFT)

        l = LabelFrame(leftFrame, text='优先级', height=400, width=3)
        l.pack(side=LEFT)
        self.ListboxReadyLevelList = Listbox(l, height=21, width=6)
        self.ListboxReadyLevelList.pack(side=LEFT)

        l = LabelFrame(leftFrame, text='等待时间', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxReadyWaitTimeList = Listbox(l, height=21, width=10)
        self.ListboxReadyWaitTimeList.pack(side=LEFT)

        l = LabelFrame(leftFrame, text="CPU时间", height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxReadyCPUTimeList = Listbox(l, height=21, width=10)
        self.ListboxReadyCPUTimeList.pack(side=LEFT)

        l = LabelFrame(leftFrame, text='总时间', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxReadyWaitAllTimeList = Listbox(l, height=21, width=10)
        self.ListboxReadyWaitAllTimeList.pack(side=LEFT)

        rightFrame = LabelFrame(self.midFrame, text="阻塞队列", width=int(self.window_width / 2), height=400)
        rightFrame.pack(side=RIGHT, padx=10)

        l = LabelFrame(rightFrame, text='PID', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitPidList = Listbox(l, height=21, width=10)
        self.ListboxWaitPidList.pack(side=LEFT)

        l = LabelFrame(rightFrame, text='进程名', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitProcessNameList = Listbox(l, height=21,width=12)
        self.ListboxWaitProcessNameList.pack(side=LEFT)

        l = LabelFrame(rightFrame, text='阻塞原因', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitWaitReason = Listbox(l, height=21, width=10)
        self.ListboxWaitWaitReason.pack(side=LEFT)

        l = LabelFrame(rightFrame, text='阻塞时间', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitWaitTimeList = Listbox(l, height=21, width=10)
        self.ListboxWaitWaitTimeList.pack(side=LEFT)

        l = LabelFrame(rightFrame, text='总时间', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitAllTimeList = Listbox(l, height=21, width=10)
        self.ListboxWaitAllTimeList.pack(side=LEFT)

        l = LabelFrame(rightFrame, text='CPU时间', height=400, width=int(self.window_width / 8))
        l.pack(side=LEFT)
        self.ListboxWaitCPUTimeList = Listbox(l, height=21, width=10)
        self.ListboxWaitCPUTimeList.pack(side=LEFT)

        self.midFrame.pack()
    #
    # def listenerCommand(self, s):
    #     if len(s.get()) < 2:
    #         s.set('>>')
    #         return
    #     if s.get()[0] != '>':
    #         s.set('>>' + s.get())
    #     if s.get()[1] != '>':
    #         s.set('>' + s.get())
    #     if s.get()[len(s.get()) - 1] == "\n":
    #         print('do ' + s.get())
    #     print(s.get())

    def clearTextTerminalArea(self):
        self.TextAreaTerminalBox['state'] = 'normal'
        self.TextAreaTerminalBox.delete(1.0, 'end')
        self.TextAreaTerminalBox.see("end")
        self.TextAreaTerminalBox['state'] = 'disable'

    def addTextToTerminalArea(self, s):
        self.TextAreaTerminalBox['state'] = 'normal'
        self.TextAreaTerminalBox.insert('end', s)
        self.TextAreaTerminalBox.see("end")
        self.TextAreaTerminalBox['state'] = 'disable'

    def click(self, event=None):
        print('hello ' + self.inputTerminalInputBox.get())
        cmd = self.inputTerminalInputBox.get()
        self.addTextToTerminalArea(cmd + "\n")
        self.inputTerminalInputBox.set('')
        if self.commandCallBackFunc:
            res = self.commandCallBackFunc(cmd)
            if res:
                self.addTextToTerminalArea(res + "\n")

    def terminalBox(self):
        self.terminalBox = LabelFrame(self.DeskTop, text='控制台', width=50, height=460)
        self.terminalBox.pack()
        self.TextAreaTerminalBox = Text(self.terminalBox, width=130, height=24, state='disabled', undo=False, autoseparators=False)
        self.TextAreaTerminalBox.pack()

        cmdBox = Frame(self.terminalBox, width=10, height=1)
        cmdBox.pack()
        Label(cmdBox, text='>>', width=3, height=1).pack(side=LEFT)
        # self.inputTerminalInputBox.trace("w", lambda name, index, mode, sv=self.inputTerminalInputBox: self.listenerCommand(sv))
        self.commandEntry = Entry(cmdBox, state='disable', validate='key', textvariable=self.inputTerminalInputBox, width=127)
        # commandEntry = Text(self.terminalBox, width=110, height=1)
        self.commandEntry.bind('<Return>', self.click)
        self.commandEntry.pack(side=RIGHT)

    def terminalWelCom(self):
        self.addTextToTerminalArea('''
Pyos simulate!
____         ___  ____  
|  _ \ _   _ / _ \/ ___| 
| |_) | | | | | | \___ \ 
|  __/| |_| | |_| |___) |
|_|    \__, |\___/|____/ 
       |___/             
please input command!
\n'''
                                   )

    def show(self):
        print('show')
        # self.terminalWelCom()
        self.DeskTop.mainloop()
