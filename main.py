# This is a sample Python script.
import threading

import GUI
import OS
import CPU
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def interupt(detail):
    print('interupt')
    print(detail)


def test():
    # d = 2222
    # print(d)
    # print(id(d))
    # a = id(d)
    # a = 3
    # print(d)
    # return
    print('test')
    cpu = CPU.CPU()
    cpu.setInteruptFunc(interupt)
    cpu.RA = 8
    cpu.RB = 1
    # cpu.ALU('io 89l')
    # cpu.ALU('io l89l')
    # cpu.ALU('io 89.00')
    # cpu.ALU('io 89xs')
    # cpu.ALU('io 89709')
    l = [
        'add RA,Rb',
        'RA = 3',
        'RB = 4',
        'RX = 8',
        'INC RA',
        'INC RB',
        'INC RX',
        'DEC RA',
        "DEC Rb",
        "dec RX",
        'SUB RA,RX',

    ]
    for v in l:
        cpu.ALU(v)
    # cpu.ALU('sub')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # test()

    D = GUI.DeskTop()
    cpu = CPU.CPU()
    os = OS.OS(ui=D, cpu=cpu)
    cpu.setInteruptFunc(os.interupt)
    D.setCommandCallBackFunc(os.commandCallBack)
    D.setPowerOnInitFunc(os.powerOnInitFunc)

    t = threading.Thread(target=os.run)
    t.start()
    D.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
