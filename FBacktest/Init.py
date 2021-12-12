from datetime import datetime

if __name__=="__main__":
    import Exchange
    import Public_Functions
    import Data
else:
    from . import Exchange
    from . import Public_Functions
    from . import Data

#回测设置
bktest_config = {
    "start": "2021-11-25 00:00:00",
    "end": "2021-12-05 00:00:00",
    "exchanges": [
        {"eid":"Futures_Binance","currency":"ETC_USDT","quotePrecision":3,"basePrecision":2,"fee":[0.02,0.04]}
        ],
    "datapath": r"data/binance/ETC_USDT/"
}

#全局变量
PERIOD_M1 = 1*60
PERIOD_M5 = 5*60

data = Data.Data(
    datapath = bktest_config["datapath"], 
    currency = "ETCUSDT",
    starttime=datetime.strptime(bktest_config["start"], "%Y-%m-%d %H:%M:%S"), 
    endtime=datetime.strptime(bktest_config["end"], "%Y-%m-%d %H:%M:%S")
    )
exchange = Exchange.Exchange(
    data=data,
    fee=bktest_config["exchanges"][0]["fee"][1]/100, 
    bktest_time=datetime.strptime(bktest_config["start"], "%Y-%m-%d %H:%M:%S"), 
    position=[{"Type":0, "Amount":0, "Price":0}, {"Type":1, "Amount":0, "Price":0}], 
    account={"Balance":1000}
    )

#策略参数
sleeptime = 500
marginlevel	= 10


def Sleep(ms):
    exchange.UpdateBkTime(ms)


def SelfTest():
    import time
    
    print('自检：')
    print('tick数据长度', len(data.TickData))
    print('mindex[:10]', data.MinuteIndex[:10])
    print('sindex[:10]', data.SecondIndex[:10])
    print('tick数据[:3]', data.TickData[:3])
    print('sindex测试', data.GetPrice(data.TickData[0, 4]))
    print(exchange.GetCurrency())
    print(exchange.level)
    for i in range(10):
        print(exchange.bktest_time, exchange.GetTicker())
        Sleep(60*1000)

    #市价单
    exchange.SetDirection("sell")
    exchange.Sell(-1, 1)
    print(exchange.GetPosition())
    exchange.SetDirection("buy")
    exchange.Buy(-1, 1)
    print(exchange.GetPosition())
    Sleep(60*1000)
    exchange.SetDirection("closebuy")
    exchange.Sell(-1, 1)
    print(exchange.GetPosition())
    exchange.SetDirection("closesell")
    exchange.Buy(-1, 1)
    print(exchange.GetPosition())
    print(exchange.GetAccount())

    #限价单
    exchange.SetDirection("sell")
    exchange.Sell(40, 1)
    print(exchange.GetPosition())
    exchange.SetDirection("buy")
    exchange.Buy(55, 1)
    print(exchange.GetPosition())
    exchange.SetDirection("closebuy")
    exchange.Sell(45, 1)
    print(exchange.GetPosition())
    exchange.SetDirection("closesell")
    exchange.Buy(55, 1)
    print(exchange.GetPosition())
    print(exchange.GetAccount())

    #GetTicker性能
    start_t = time.time()
    for i in range(0, 10000):
        exchange.GetTicker()
        Sleep(100)
    end_t = time.time()
    print('万次GetTicker用时', end_t - start_t)

if __name__=="__main__":
    SelfTest()