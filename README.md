# Stockity Option Trading API Library

A Python library for automated trading on the Stockity / Binomo platform using WebSocket. Ideal for manual strategies, auto signal bots, or advanced integration.

## 🚀 Main Features

- Custom moded websocket-client module
- WebSocket authentication to Stockity / Binomo
- Execute orders (call/put)
- Wait for trade result (win/loss)
- Easy to integrate with signal bots

---

## 📦 Installation

```bash
pip install requests
```

---

## 🧪 Simple Usage Example

```python
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
```

---

## 📡 Example with Text-Based Signals

```python
from lib import *

#Platform: "stockity.id" / "binomo2.com"
trader = MyWebSocket("your_email", "your_password", platform="binomo2.com")
while not trader.ws:
    time.sleep(0.5)

signals = """
05:15 S
05:19 B
05:24 S
05:29 B
"""

asset_ric = "Z-CRY/IDX"

for signal in signals.split("\n"):
    if ":" in signal:
        timex = signal.split(" ")[0] + ":00"
        timex = datetime.datetime.strptime(timex, "%H:%M:%S").time()
        now = datetime.datetime.now()
        timex_today = datetime.datetime.combine(now.date(), timex)
        if timex_today > now:
            sleep = (timex_today - now).total_seconds()
            print(f"Waiting signal {sleep:.2f} seconds")
            time.sleep(sleep)

            signal_type = signal.split(" ")[1].lower()
            trend = "call" if "b" in signal_type else "put"
            ref = trader.bid(trend=trend, amount=14000, asset_ric=asset_ric, wallet_type="demo", minute=1)
            result = trader.wait_bid(ref)
            
            # COMPENSATION 1
            # if result["status"] == "lose":
            #     trader.bid(trend=trend, amount=28000, asset_ric=asset_ric, wallet_type="demo", minute=1)

trader.ws.close()
```

---

## 💼 Business or Custom Integration

Want to use this library for business purposes, signal bots, or integrate with other platforms like **Olymp Trade**, **Binomo**, etc?

📲 Contact me: [https://wa.me/+6289625658302](https://wa.me/+6289625658302)

---

## 📄 License

This project is licensed under the MIT License.
