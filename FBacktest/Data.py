import os
from datetime import datetime, timedelta, timezone
import copy
import numpy as np
#import numba

class Data:

    def __init__(self, datapath, currency, starttime, endtime):
        self.datapath = datapath
        self.currency = currency
        self.starttime = starttime.replace(tzinfo=timezone.utc)
        self.endtime = endtime.replace(tzinfo=timezone.utc)
        

        self.KLines = []
        self.RecordsMax = 100#返回的K线条数上限

        self.LoadData()
        self.GenerateKLines()

    def TsToKLIndex(self, time):
        return int((time - self.time_offset) / (60*1000))

    def Ts2Minute(self, time):
        return int((time - self.time_offset) / (60*1000))

    def Ts2Second(self, time):
        return int((time - self.time_offset) / (1000))

    def GetDataFileNames(self):
        dates = dateRange(self.starttime, self.endtime)
        return [self.currency + "-trades-" + date + ".csv" for date in dates]

    def LoadData(self):
        print("Loading Data...", end='')
        
        #读取tick数据
        self.rawdata = []
        files = self.GetDataFileNames()
        for fname in files:
            day_tickdata = np.loadtxt(self.datapath + fname, 
                #dtype={'names': ('id', 'price', 'coinamount', 'usdtamount', 'timestamp', 'isbuyer'), 
                #    'formats': (np.int64, np.float32, np.float32, np.float32, np.int64, np.int64)},
                dtype = np.float64,
                delimiter=',',
                converters={5: lambda s: (s=='true') + 0}
                )
            self.rawdata.append(day_tickdata)
        
        #合并tick数据
        self.TickData = np.reshape(np.concatenate(tuple(self.rawdata)),(-1, 6))
        del self.rawdata
        print(self.TickData.shape)

        self.time_offset = self.TickData[0][4]

        #遍历tick数据，建立索引
        self.MinuteIndex = np.full((int((self.TickData[-1][4] - self.TickData[0][4]) / (60*1000) + 1),), -1, dtype=np.int64)
        self.SecondIndex = np.full((int((self.TickData[-1][4] - self.TickData[0][4]) / (1000) + 1),), -1, dtype=np.int64)
        for i in range(self.TickData.shape[0]):
            ts = self.TickData[i][4]
            minite = self.Ts2Minute(ts)
            second = self.Ts2Second(ts)

            if self.MinuteIndex[minite] == -1:
                self.MinuteIndex[minite] = i
            if self.SecondIndex[second] == -1:
                self.SecondIndex[second] = i
        for i in range(1, self.SecondIndex.shape[0]):
            if self.SecondIndex[i] == -1:
                self.SecondIndex[i] = self.SecondIndex[i-1]
        #print(self.SecondIndex.shape, self.MinuteIndex.shape)
        #print(len([i for i in self.SecondIndex if i==0]))





        '''
        self.tickdata = [0]*int((datetime.timestamp(self.endtime) - datetime.timestamp(self.starttime)) / 60 + 1)
        self.time_offset = int(datetime.timestamp(self.starttime) * 1000)

        print("Loading Data...", end='')
        #rawdata = []

        files = self.GetDataFileNames()

        for fname in files:
            with open(self.datapath + fname, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    words = line.split(',')
                    #id, 价，量，额，时间戳，买方
                    d = [int(words[0]), float(words[1]), float(words[2]), float(words[3]), int(words[4]), words[5]=='true']
                    #rawdata.append(d)
                    minuteindex = self.TsToKLIndex(d[4])
                    if minuteindex >= len(self.tickdata):
                        break
                    if self.tickdata[minuteindex]==0:
                        self.tickdata[minuteindex] = [(d[4], d[1], d[2], d[3])]
                    else:
                        self.tickdata[minuteindex].append((d[4], d[1], d[2], d[3]))
        
        #print("Done. rawData Length:", len(rawdata))
        #print("Parsing rawData...", end='')
        '''
        
        
        '''
        for d in rawdata:
            minuteindex = self.TsToKLIndex(d[4])
            if minuteindex >= len(self.tickdata):
                break
            
            if self.tickdata[minuteindex]==0:
                self.tickdata[minuteindex] = [(d[4], d[1])]
            else:
                self.tickdata[minuteindex].append((d[4], d[1]))
        '''
        print("Done. tickdata Length:", len(self.TickData))
        

    #计算所有分钟级K线
    def GenerateKLines(self):
        print("Generating KLines...", end='')
        self.KLines = np.zeros((len(self.MinuteIndex), 6))
        
        for i in range(self.KLines.shape[0] - 1):
            try:
                p = self.TickData[self.MinuteIndex[i]: self.MinuteIndex[i+1], 1]
                a = self.TickData[self.MinuteIndex[i]: self.MinuteIndex[i+1], 2]
            except:
                p = self.TickData[self.MinuteIndex[i]: self.TickData.shape[0] - 1, 1]
                a = self.TickData[self.MinuteIndex[i]: self.TickData.shape[0] - 1, 2]
            #时间ms，开，高，低，收，量
            self.KLines[i, 0] = i*60*1000 + self.time_offset
            self.KLines[i, 1] = p[0]
            self.KLines[i, 2] = np.max(p)
            self.KLines[i, 3] = np.min(p)
            self.KLines[i, 4] = p[-1]
            self.KLines[i, 5] = np.sum(a)

        print("Done. KLines Length:", self.KLines.shape[0])
    
    '''
    def GenerateKLines(self):
        print("Generating KLines...", end='')
        self.KLines = np.zeros((len(self.MinuteIndex), 6))
        
        for i in range(self.KLines.shape[0]):
            #范围data
            try:
                p = self.TickData[self.MinuteIndex[i]: self.MinuteIndex[i+1]]
                p = [t[1] for t in self.tickdata[i] if t!=0]
                a = [t[2] for t in self.tickdata[i] if t!=0]
            except:
                print(self.tickdata[i])
            #时间ms，开，高，低，收，量
            self.KLines[i, 0] = i*60*1000 + self.time_offset
            self.KLines[i, 1] = p[0]
            self.KLines[i, 2] = np.max(p)
            self.KLines[i, 3] = np.min(p)
            self.KLines[i, 4] = p[-1]
            self.KLines[i, 5] = np.sum(a)

        print("Done. KLines Length:", self.KLines.shape[0])
    '''

    def GetPrice(self, time):
        
        second = self.Ts2Second(time)
        sindex = self.SecondIndex[second] if second >= 0 else 0
        
        sindex_max = self.TickData.shape[0]
        td = self.TickData
        while sindex < sindex_max:
            if td[sindex, 4] >= time:
                return sindex, td[sindex, 4], td[sindex, 1]
            sindex += 1

        return 0, 0, 0

    #获取时间段内的最大最小值
    def GetMaxMin(self, time1, time2):
        i1, ts1, pr1 = self.GetPrice(time1)
        i2, ts2, pr2 = self.GetPrice(time2)
        p = self.TickData[i1:i2, 1]
        if i1==i2:
            return self.TickData[i1, 1], self.TickData[i1, 1]
        return np.max(p), np.min(p)

    #此处合并K线用的是滑动窗口，而非固定时间点，会和交易所不一致
    def GetRecords(self, p, time):#p单位分钟
        p = int(p)
        end = self.Ts2Minute(time)
        records = []
        for i in range(self.RecordsMax):
            endindex = end - i*p
            startindex = end - (i+1)*p
            if startindex < 0:
                break
            record = {
                "Time"  : self.KLines[startindex, 0], 
                "Open"  : self.KLines[startindex, 1], 
                "High"  : np.max(self.KLines[startindex: endindex, 2]),
                "Low"   : np.min(self.KLines[startindex: endindex, 3]),
                "Close" : self.KLines[endindex, 4], 
                "Volume": np.sum(self.KLines[startindex: endindex, 5])   
            }
            records.append(record)
        records.reverse()

        #重新计算最后一分钟
        last_id, _, _ = self.GetPrice(time)
        pr = self.TickData[self.MinuteIndex[end]: last_id, 1]
        am = self.TickData[self.MinuteIndex[end]: last_id, 2]
        if len(pr) == 0:
            pr = [self.TickData[self.MinuteIndex[end], 1]]
        if len(am) == 0:
            am = [0]
        records.append(
            {
                "Time"  : self.KLines[end, 0], 
                "Open"  : self.KLines[end, 1], 
                "High"  : np.max(pr), 
                "Low"   : np.min(pr), 
                "Close" : pr[-1], 
                "Volume": np.sum(am), 
            }
        )
        return records
        
def dateRange(beginDate, endDate):
    dates = []
    dt = copy.deepcopy(beginDate)
    
    while dt <= endDate:
        date = dt.strftime("%Y-%m-%d")
        dates.append(date)
        dt = dt + timedelta(days=1)

    return dates

if __name__=='__main__':
    data = Data(
        datapath = r"data/binance/ETC_USDT/", 
        currency = 'ETCUSDT',
        starttime=datetime.strptime("2021-10-20 00:00:00", "%Y-%m-%d %H:%M:%S"), 
        endtime=datetime.strptime("2021-10-27 00:00:00", "%Y-%m-%d %H:%M:%S")
    )