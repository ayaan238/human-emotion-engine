import time, requests, datetime, json, os

API = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

state = {
    "last_period": None,
    "history": [],
    "win": 0,
    "loss": 0,
    "cw": 0,
    "cl": 0,
    "mw": 0,
    "ml": 0
}

def bs(n): return "B" if n >= 5 else "S"

def zigzag(h):
    if len(h) < 4: return False
    s = "".join(bs(x) for x in h[:4])
    return s in ("BSBS","SBSB")

def time_mode():
    t = datetime.datetime.now().hour*60 + datetime.datetime.now().minute
    if 360 <= t < 600: return "MORNING"
    if 600 <= t < 1080: return "NORMAL"
    if 1080 <= t < 1410: return "EVENING"
    return "NIGHT"

def predict():
    h = state["history"]
    if len(h) < 4: return "WAIT"
    if zigzag(h): return "SKIP"

    B = sum(1 for x in h if x >= 5)
    S = len(h) - B

    human = "BIG" if B>S else "SMALL" if S>B else ("BIG" if h[0]>=5 else "SMALL")
    if time_mode() in ("EVENING","NIGHT"):
        return "SMALL" if human=="BIG" else "BIG"
    return human

def save_log():
    with open("daily_log.json","w") as f:
        json.dump(state,f,indent=2)

print("SERVER STARTED")

while True:
    try:
        r = requests.get(API,timeout=10).json()["data"]["list"]
        period = r[0]["issueNumber"]
        number = int(r[0]["number"])

        if state["last_period"] is None:
            state["history"] = [int(x["number"]) for x in r[:10]]
            state["last_period"] = period
            continue

        if period != state["last_period"]:
            state["last_period"] = period
            prediction = predict()

            if prediction in ("BIG","SMALL"):
                real = "BIG" if number>=5 else "SMALL"
                if real == prediction:
                    state["win"]+=1; state["cw"]+=1; state["cl"]=0
                    state["mw"]=max(state["mw"],state["cw"])
                else:
                    state["loss"]+=1; state["cl"]+=1; state["cw"]=0
                    state["ml"]=max(state["ml"],state["cl"])

            state["history"].insert(0,number)
            state["history"]=state["history"][:10]
            save_log()

    except Exception as e:
        print("ERR",e)

    time.sleep(1)
