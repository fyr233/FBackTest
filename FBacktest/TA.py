

def MA(records, period):
    ma = []
    pricelist = [r["Close"] for r in records]
    for i in range(period-1, len(records)):
        ave = sum(pricelist[i-period+1: i+1]) / period
        ma.append(ave)
    ma.reverse()
    return ma

def ATR(records, period):
    return [0,1]