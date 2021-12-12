import time

def FMZ_CDelay(ms):
    pass

def FMZ_C(f, *argv):
    if len(argv) > 0:
        return f(*argv)
    else:
        return f()

def FMZ_N(v, n):
    return round(v, n)

def IsVirtual():
    return True

def Log(*arg):
    print(*arg)

def LogStatus(*arg):
    pass

def LogProfit(*arg):
    pass

def LogProfitReset(*arg):
    pass

def GetCommand():
    return ""

