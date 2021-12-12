# FBackTest
一个使用[FMZ](http://fmz.com)相同接口的tick级回测引擎。https://www.fmz.com/api  
- 纯py实现，完全开源。
- 纯本地回测，需要下载tick数据到本地。 https://data.binance.vision/
- 目前只支持币安U本位永续合约。
- 目前只支持python。
- 目前只支持市价单、限价单，不支持止盈止损等其他类型。
- 只实现了FMZ的部分接口。
- 还在开发中，完成度不高。

网页版的FMZ不支持币安合约实盘级回测，[FMZ的python本地回测](https://github.com/fmzquant/backtest_python)没有开源引擎c++核心，报错时难以debug。而模拟级回测又十分的不准，因此开发了**FBackTest**供自己回测。
