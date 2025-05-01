import websocket, time, json, datetime, threading, requests, uuid, traceback

def log(msg):
    print(datetime.datetime.now().strftime(f"[ %d/%m/%Y %H:%M:%S ] {msg}"))
    
class MyWebSocket:
    def __init__(self, email, password, platform="stockity.id"):
        self.platform = platform
        self.device_id = str(uuid.uuid4().hex)
        self.bids = []; self.user = {"balance": {}}; self.rates = {}
        self.headers = {
            "cookie": f"authtoken=; device_type=web; device_id={self.device_id};",
            "device-id": self.device_id,
            "origin": f"https://{self.platform}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "user-timezone": "Asia/Bangkok"
        }
        self.login(email, password)
        self.ws = None
        threading.Thread(target=self.run, daemon=True).start()

    def login(self, email, password):
        headers = {
            'cookie': f'authtoken=; device_type=web; device_id={self.device_id}',
            'device-id': self.device_id,
            'device-type': 'web',
            'origin': f'https://https://{self.platform}',
            'referer': f'https://https://{self.platform}/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'user-timezone': 'Asia/Bangkok'
        }
        payload = {
            "email": email,
            "password": password
        }
        resp = requests.post(f"https://api.{self.platform}/passport/v2/sign_in?locale=id", headers=headers, json=payload).json()
        self.headers["cookie"] = f"authtoken={resp['data']['authtoken']}; device_type=web; device_id={self.device_id};"
        self.headers["authorization-token"] = resp["data"]["authtoken"]

    def on_open(self, ws):
        log("Conection opened...")
        ws.send({"topic": "connection","event": "phx_join","payload": {},"ref": "","join_ref": "6"})
        ws.send({"topic":"bo","event":"phx_join","payload":{},"ref":"","join_ref":"9"})
        ws.send({"topic":"account","event":"phx_join","payload":{},"ref":"","join_ref":"9"})
        ws.send({"topic":"asset","event":"phx_join","payload":{},"ref":"","join_ref":"26"})
        self.ws = ws
        
    def on_message(self, ws, message):
        message = json.loads(message)
        #print(message)
        try:
            if message["event"] == "balance_changed":
                self.user["balance"][message["payload"]["account_type"]] = int(str(message["payload"]["balance"])[:-2])
                balance = "{:,}".format(self.user["balance"][message["payload"]["account_type"]])
                log(f"Balance {message['payload']['account_type'].upper()} changed: {balance}")

            elif message["event"] == "asset_trading_settings_changed_v2":
                self.rates[message["payload"]["ric"]] = message["payload"]["trading_tools_settings"]["ftt"]["base_payment_rate_standard"]
                log(f"Rate {message['payload']['ric']} changed: {message['payload']['trading_tools_settings']['ftt']['base_payment_rate_standard']}")

            elif message["event"] == "opened":
                bid = [item for item in self.bids if ({"uuid": message["payload"]["uuid"]}.items() <= v.items() for v in item.values())]
                if bid:
                    amount = "{:,}".format(int(str(bid[0]["amount"])[:-2]))
                    log(f"Open bid: {amount} | {bid[0]['asset_ric']} | {bid[0]['wallet_type'].upper()}")
                    bid[0]["payload"] = message["payload"]
                   
            elif message['event'] == "close_deal_batch":
                bid = [item for item in self.bids if ({"asset_ric": message["payload"]["ric"]}.items() <= v.items() for v in item.values())]
                if bid:
                    bid = [item for item in self.bids if "payload" in item and ({"finished_at": message["payload"]["finished_at"]}.items() <= v.items() for v in item["payload"].values())]
                    if bid:
                        if message["payload"]["end_rate"] > bid[0]["payload"]["open_rate"]:
                            result = "call"
                        elif message["payload"]["end_rate"] < bid[0]["payload"]["open_rate"]:
                            result = "put"
                        else:
                            result = "draw"

                        if result == "draw":
                            bid[0]["result"] = result
                            bid[0]["status"] = "draw"
                        elif result == bid[0]["trend"]:
                            bid[0]["result"] = result
                            bid[0]["status"] = "win"
                        else:
                            bid[0]["result"] = result
                            bid[0]["status"] = "lose"
                        amount = "{:,}".format(int(str(bid[0]["amount"])[:-2]))
                        log(f"Close bid: {bid[0]['status'].upper()} | {amount} | {bid[0]['asset_ric']} | {bid[0]['wallet_type'].upper()}")
                        
            elif message.get("ref") and "payload" in message and "response" in message["payload"]:
                bid = [item for item in self.bids if ({"ref": message.get("ref")}.items() <= v.items() for v in item.values())]
                if bid:
                    if message["event"] == "phx_reply" and "uuid" in message["payload"]["response"]:
                        bid[0]["uuid"] = message["payload"]["response"]["uuid"]   
                    elif message["event"] == "phx_reply" and "reasons" in message["payload"]["response"]:
                        log(f"Failed open bid: {json.dumps(message['payload']['response']['reasons'])}")
        except:
            print(f"Error: {traceback.format_exc()}")
            
    def parse_time(self, minute=1):
        if minute == 1 and not int(datetime.datetime.now().strftime("%S")) < 30:
            minute = 2
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:00")
        bid = datetime.datetime.strptime(now, "%d/%m/%Y %H:%M:%S") + datetime.timedelta(minutes=minute)
        return int(time.mktime(bid.timetuple()))

    def bid(self, trend="call", amount=14000, asset_ric="Z-CRY/IDX", wallet_type="demo", minute=1):
        amount = int(str(amount)+"00")
        data = {"wallet_type": wallet_type, "amount": amount, "asset_ric": asset_ric, "trend": trend}
        self.ws.send(
            {
                "topic": "bo",
                "event": "create",
                "payload":{
                    "created_at": int(time.time()*1000),
                    "ric": asset_ric,
                    "deal_type": wallet_type,
                    "expire_at": self.parse_time(minute),
                    "option_type": "turbo",
                    "trend": trend,
                    "tournament_id": None,
                    "is_state": False,
                    "amount": amount
                },
                "ref": "",
                "join_ref": "9"
            }
        )
        data["ref"] = self.ws.ref
        self.bids.append(data)
        return data["ref"]

    def wait_bid(self, ref):
        bid = [item for item in self.bids if ({"ref": ref}.items() <= v.items() for v in item.values())]
        if bid:
            log(f"Waiting bid ref: {ref}")
            while True:
                if "status" in bid[0]:
                    return bid[0]
                time.sleep(.01)
        raise Exception("Ref id not found")
           
    def run(self):
        ws = websocket.WebSocketApp(
            f"wss://ws.{self.platform}/?v=2&vsn=2.0.0",
            header=self.headers,
            on_message=self.on_message,
            on_open=self.on_open
        )
        ws.run_forever(ping_interval=15, reconnect=5, ping_payload=[{"topic": "phoenix","event": "heartbeat","payload": {},"ref": ""},{"topic": "connection","event": "ping","payload": {},"ref": "","join_ref": "6"}])

#Platform: "stockity.id" / "binomo2.com"
trader = MyWebSocket("heryoprek88@gmail.com", "Blogspot2@", platform="binomo2.com")
while not trader.ws:
    time.sleep(0.5)
time.sleep(99)
