import os
import pyupbit
from dotenv import load_dotenv

load_dotenv()
access = os.environ.get("ACCESS_TOKEN")
secret = os.environ.get("SECRET_TOKEN")
upbit = pyupbit. Upbit(access, secret)

# 업비트가 지원하는 모든 암호화폐 목록
# print(pyupbit.get_tickers())

print(upbit.get_balance("KRW"))     # 보유 현금 조회
print(upbit.get_balance("KRW-BTC")) # KRW-BTC 조회
print(upbit.get_balance("KRW-SOL")) # KRW-SOL 조회
