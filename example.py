
isFBackTest = True
if isFBackTest:
    print("当前平台：FBackTest")
    from FBacktest import TA
    from FBacktest import Public_Functions
    from FBacktest.Public_Functions import *
    from FBacktest.Chart import *
    from FBacktest.Init import *
    _C = Public_Functions.FMZ_C
    _N = Public_Functions.FMZ_N
    _CDelay = Public_Functions.FMZ_CDelay

import time
import json
import math
import numpy as np
import matplotlib.pyplot as plt 

def onTick():
    ticker = exchange.GetTicker()
    Log(ticker)
    
def main():
    
    while True:
        onTick()
        Sleep(sleeptime)

def init():
    Log("初始化！")
    
    _CDelay(100)
    _C(exchange.SetContractType, "swap")#永续
    _C(exchange.SetMarginLevel, marginlevel)#杠杆
    
    LogProfitReset()
    
def onexit():
    Log("结束！")

if __name__ == "__main__":
    init()
    main()