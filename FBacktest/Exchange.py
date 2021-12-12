from datetime import datetime, timedelta, timezone
import math
import random
import copy
import matplotlib.pyplot as plt

price_list = []
allvalue_list = []
slop_list = []

class Exchange:
    def __init__(self, data, fee, bktest_time, position=None, account=None):
        self.data = data
        self.fee = fee#手续费
        self.bktest_time = int(datetime.timestamp(bktest_time.replace(tzinfo=timezone.utc)) * 1000)#毫秒
        self.starttime_ms = int(datetime.timestamp(self.data.starttime) * 1000)
        self.endtime_ms = int(datetime.timestamp(self.data.endtime) * 1000)

        self.position = position if position else [
            {"Type":0, "Amount":0, "Price":0},
            {"Type":1, "Amount":0, "Price":0}
        ]
        self.account = account if account else {"Balance":100000}

        self.direction = 0
        self.price = 0
        self.level = 1
        self.orders_pending = []#未完成订单
        self.orders_closed = []#已成交订单

        self.oldposition = [
            {"Type":0, "Amount":0, "Price":0},
            {"Type":1, "Amount":0, "Price":0}
        ]

#内部函数
    #bktime增加t（ms）
    def UpdateBkTime(self, t):
        nowtime = self.bktest_time + t
        
        #判断这一段时间里有没有限价单成交
        max, min = self.data.GetMaxMin(self.bktest_time, nowtime)
        for order in self.orders_pending:
            if (order["Type"] == 0 and order["Price"] > min) or (order["Type"] == 1 and order["Price"] < max):#买单/卖单成交
                self.CompleteOrder(order)

        self.bktest_time = nowtime

    #查找bktime时刻的价格
    def GetPrice(self):
        self.UpdateBkTime(100)
        if self.bktest_time > self.endtime_ms:#毫秒
            print("达到回测终点")
            self.EndBackTest()
            raise "达到回测终点"
        
        index, time, price = self.data.GetPrice(self.bktest_time)
        if time == 0:
            print("达到回测终点")
            self.EndBackTest()
            raise "达到回测终点"

        #self.UpdateBkTime(time - self.bktest_time)
        self.bktest_time = time
        self.price = price
        
        return price

    def GetBuyValue(self, price):
        return self.position[0]["Amount"] * (price - self.position[0]["Price"]) + self.position[0]["Amount"] * self.position[0]["Price"] / self.level

    def GetSellValue(self, price):
        return self.position[1]["Amount"] * (self.position[1]["Price"] - price) + self.position[1]["Amount"] * self.position[1]["Price"] / self.level

    def CompleteOrder(self, order):

        value = order["Price"] * order["Amount"]#名义交易额

        if order["Type"] == 1 and order["Offset"] == 1:#平多
            if order["Amount"] > self.position[0]["Amount"]:
                print("平多仓位不足!")
                self.EndBackTest()
                raise "平多仓位不足!"
            
            #计算旧Value
            oldvalue = self.GetBuyValue(order["Price"])
            #更新amount
            self.position[0]["Amount"] -= order["Amount"]
            #计算新Value
            newvalue = self.GetBuyValue(order["Price"])
            #将Value差转入余额
            self.account["Balance"] += (oldvalue - newvalue)
            self.account["Balance"] -= value * self.fee
            
            nowtime = datetime.fromtimestamp(self.bktest_time/1000).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(nowtime, "成交", "平多", order["Price"], order["Amount"])

        elif order["Type"] == 1 and order["Offset"] == 0:#开空
            if self.account["Balance"] < value / self.level:
                print("余额不足!", self.account["Balance"], value)
                self.EndBackTest()
                raise "余额不足!"

            #计算旧Value
            oldvalue = self.GetSellValue(order["Price"])
            #更新持仓均价
            self.position[1]["Price"] = (self.position[1]["Amount"]*self.position[1]["Price"]\
                + order["Price"] * order["Amount"])/(self.position[1]["Amount"] + order["Amount"])
            #更新amount
            self.position[1]["Amount"] += order["Amount"]
            #计算新Value
            newvalue = self.GetSellValue(order["Price"])
            #将Value差从余额扣除
            self.account["Balance"] -= (newvalue - oldvalue)
            self.account["Balance"] -= value * self.fee

            nowtime = datetime.fromtimestamp(self.bktest_time/1000).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(nowtime, "成交", "开空", order["Price"], order["Amount"])

        elif order["Type"] == 0 and order["Offset"] == 0:#开多
            if self.account["Balance"] < value / self.level:
                print("余额不足!", self.account["Balance"], value)
                self.EndBackTest()
                raise "余额不足!"

            #计算旧Value
            oldvalue = self.GetBuyValue(order["Price"])
            #更新持仓均价
            self.position[0]["Price"] = (self.position[0]["Amount"]*self.position[0]["Price"]\
                + order["Price"] * order["Amount"])/(self.position[0]["Amount"] + order["Amount"])
            #更新amount
            self.position[0]["Amount"] += order["Amount"]
            #计算新Value
            newvalue = self.GetBuyValue(order["Price"])
            #将Value差从余额扣除
            self.account["Balance"] -= (newvalue - oldvalue)
            self.account["Balance"] -= value * self.fee

            nowtime = datetime.fromtimestamp(self.bktest_time/1000).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(nowtime, "成交", "开多", order["Price"], order["Amount"])

        elif order["Type"] == 0 and order["Offset"] == 1:#平空
            if order["Amount"] > self.position[1]["Amount"]:
                print("平空仓位不足!")
                self.EndBackTest()
                raise "平空仓位不足!"

            #计算旧Value
            oldvalue = self.GetSellValue(order["Price"])
            #更新amount
            self.position[1]["Amount"] -= order["Amount"]
            #计算新Value
            newvalue = self.GetSellValue(order["Price"])
            #将Value差转入余额
            self.account["Balance"] += (oldvalue - newvalue)
            self.account["Balance"] -= value * self.fee
            
            nowtime = datetime.fromtimestamp(self.bktest_time/1000).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(nowtime, "成交", "平空", order["Price"], order["Amount"])

        #已成交订单加入orders_closed
        self.orders_closed.append(order)
        self.orders_closed[-1]["Status"] = 1
        #在orders_pending中删除
        if order in self.orders_pending:
            self.orders_pending.remove(order)

        #记录信息
        allvalue = self.account["Balance"] + self.GetBuyValue(order["Price"]) + self.GetSellValue(order["Price"])
        price_list.append(order["Price"])
        allvalue_list.append(allvalue)
        slop_list.append(0 if (self.position[0]["Amount"] - self.position[1]["Amount"]) == 0 else
            (self.position[0]["Amount"] - self.position[1]["Amount"]) / (self.position[0]["Amount"] + self.position[1]["Amount"]))

    def Plot(self):
        #价值价格图
        plt.clf()
        plt.plot(price_list, allvalue_list)
        plt.scatter(price_list, allvalue_list)
        plt.show()

        #价值图
        plt.clf()
        plt.plot(allvalue_list)
        plt.show()

        #斜率价格图
        plt.clf()
        plt.plot(price_list, slop_list)
        plt.scatter(price_list, slop_list)
        plt.show()

    def EndBackTest(self):
        self.Plot()

#Get函数
    def GetTicker(self):
        #self.UpdateBkTime(20)
        self.GetPrice()
        ticker = {"Last":self.price}
        return ticker

    def GetPosition(self):
        self.UpdateBkTime(20)
        #if random.random() > 0.5:
        #    self.oldposition = copy.deepcopy(self.position)
        #print(self.position, self.oldposition)
        return self.position

    def GetAccount(self):
        self.UpdateBkTime(20)
        return self.account

    def IO(self, *argv):
        self.UpdateBkTime(20)
        return self.price

    def GetRecords(self, p):
        self.UpdateBkTime(20)
        if p % 60 != 0:
            raise "周期需为分钟的整数倍"
        return self.data.GetRecords(p/60, self.bktest_time)

    def GetCurrency(self):
        return self.data.currency

    def GetOrders(self):
        return self.orders_pending

#Set函数
    def SetDirection(self, s):
        self.UpdateBkTime(20)
        self.direction = s

    def SetContractType(self, type):
        pass

    def SetMarginLevel(self, l):
        self.level = l

#交易函数
    def Sell(self, price, amount):
        self.UpdateBkTime(100)
        self.GetPrice()
        
        order = dict(
            Id          = random.randint(0, 1e8),       # 交易单唯一标识
            Price       = price,                        # 下单价格，
            Amount      = amount,                       # 下单数量，
            DealAmount  = 0,                            # 成交数量，如果交易所接口不提供该数据则可能使用0填充
            AvgPrice    = 0,                            # 成交均价，注意有些交易所不提供该数据。不提供、也无法计算得出的情况该属性设置为0
            Status      = 0,                            # 订单状态，0未完成，1已完成，2已取消，3其他
            Type        = 1,                            # 订单类型，0买，1卖
            Offset      = 0 if self.direction == "sell" else 1,     # 数字货币期货的订单数据中订单的开平仓方向。0为开仓方向，1为平仓方向
            ContractType= self.data.currency            # 现货订单中该属性为""即空字符串，期货订单该属性为具体的合约代码
        )

        if price > 0:#限价挂单
            self.orders_pending.append(order)
            return 0
        else:#市价单立即成交
            order["Price"] = self.price
            self.CompleteOrder(order)
            return 0

    def Buy(self, price, amount):
        self.UpdateBkTime(100)
        self.GetPrice()
        
        order = dict(
                Id          = random.randint(0, 1e8),       # 交易单唯一标识
                Price       = price,                        # 下单价格，
                Amount      = amount,                       # 下单数量，
                DealAmount  = 0,                            # 成交数量，如果交易所接口不提供该数据则可能使用0填充
                AvgPrice    = 0,                            # 成交均价，注意有些交易所不提供该数据。不提供、也无法计算得出的情况该属性设置为0
                Status      = 0,                            # 订单状态，0未完成，1已完成，2已取消，3其他
                Type        = 0,                            # 订单类型，0买，1卖
                Offset      = 0 if self.direction == "buy" else 1,     # 数字货币期货的订单数据中订单的开平仓方向。0为开仓方向，1为平仓方向
                ContractType= self.data.currency            # 现货订单中该属性为""即空字符串，期货订单该属性为具体的合约代码
            )

        if price > 0:#限价挂单
            self.orders_pending.append(order)
            return 0
        else:#市价单立即成交
            order["Price"] = self.price
            self.CompleteOrder(order)
            return 0


