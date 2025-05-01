from lib import *

#Platform: "stockity.id" / "binomo2.com"
trader = MyWebSocket("your_email", "your_password", platform="binomo2.com")
while not trader.ws:
    time.sleep(0.5)

# TRADE BID
ref = trader.bid(trend="call", amount=14000, asset_ric="Z-CRY/IDX", wallet_type="demo", minute=1)
print("Ref ID:", ref)

# RESULT BID
result = trader.wait_bid(ref)
print("Result:", result)

# CLOSE CONNECTION
trader.ws.close()
