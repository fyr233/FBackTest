import requests
import time
import datetime

baseurl = "https://data.binance.vision/data/futures/um/daily/trades/ETCUSDT/"

def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(days=1)
        date = dt.strftime("%Y-%m-%d")
    return dates

def main():
    dates = dateRange("2021-11-30", "2021-12-06")
    for date in dates:
        r = requests.get(baseurl + "ETCUSDT-trades-" + date + ".zip")
        print(date, r.status_code)
        with open("./data/binance/ETC_USDT/" + "ETCUSDT-trades-" + date + ".zip", 'wb') as f:
            f.write(r.content)
        time.sleep(10)

if __name__=='__main__':
    main()