import os
import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
from dotenv import load_dotenv

load_dotenv()
access = os.environ.get("ACCESS_TOKEN")
secret = os.environ.get("SECRET_TOKEN")
k = 0.42 # hyperparameter

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", k)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995) # 수수료 감안해서 매수
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc) # 전량 매도
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

# https://docs.conda.io/en/latest/miniconda.html
# 위 홈페이지에서 Python 3.8 버전의 Miniconda를 다운 받아서 같은 방법으로 설치해주세요.
# 설치 후, VS code에서 Python 3.8.10 64-bit ('base': conda) 로 선택 후에 똑같은 방법으로 다시 cmd 창에서 아래 명령어를 실행해 주세요.
# pip install pyupbit
# pip install schedule
# conda install -c conda-forge fbprophet
# pip install pystan --upgrade
# 그리고, python 파일 실행하시면 됩니다.

# Importing plotly failed. Interactive plots will not work. 발생 시
# pip install --upgrade plotly 실행
