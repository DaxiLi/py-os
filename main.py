# This is a sample Python script.
import threading
import GUI
import OS
import CPU


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
    # new 一个 UI
    D = GUI.DeskTop()
    # new 一个 CPU
    cpu = CPU.CPU()
    # new 一个 OS
    os = OS.OS(ui=D, cpu=cpu)
    # 设置中断回调函数， CPU 在遇到错误或IO的情况时，会调用该方法处理中断
    cpu.setInteruptFunc(os.interupt)
    # UI 命令行回调函数，UI 在获取用户输入后，调用该接口通知 OS
    D.setCommandCallBackFunc(os.commandCallBack)
    # OS 初始化接口，UI 在接到 开机动作时（按下开关机），会调用该接口通知 OS
    D.setPowerOnInitFunc(os.powerOnInitFunc)

    # 这个地方本来应该让 UI 作为子线程，当时没想好，改了会出错，暂且这样
    t = threading.Thread(target=os.run)
    t.start()
    D.show()

