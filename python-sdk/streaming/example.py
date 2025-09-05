import time
from nxtradstream import NxtradStream

import requests

def getAccessToken(host, apikey, password, twoFa, twoFaType):
    url = "https://" + host + '/v2/api-gw/oauth/individual-token-v2'
    
    headers = {"Authorization": "Bearer " + apikey}
    postParams = {'password': password, 'twoFa': twoFa, 'twoFaTyp': twoFaType}
    
    x = requests.post(url, data = postParams, headers = headers )
    if x.status_code == 200:
        resp = x.json()
        return resp['access_token']

    return None

def connect_cb(_nx_stream, ev):
    
    # {'s': 'connected'}
    # {'s': 'error'}
    # {'s': 'closed'}
    print(ev)

    if (ev['s'] == "connected"):
        # sym_tokens should be in format exchtoken_exchange 
        # NSE-EQ  => NSE
        # NSE Future & Option => NFO
        stream_symbol_list = ["22_NSE", "-1_NSE", "22_NSE", "3045_NSE"]
        events = ["orders", "positions", "trades"]
        _nx_stream.subscribeEvents(events)
        b = _nx_stream.subscribeL1SnapShot(stream_symbol_list)
        _nx_stream.subscribeL1(stream_symbol_list)
        
        _nx_stream.subscribeL2(stream_symbol_list)
        _nx_stream.subscribeL2SnapShot(stream_symbol_list)
        _nx_stream.subscribeGreeks(stream_symbol_list)
        _nx_stream.subscribeOHLC(stream_symbol_list,"1M")# 5M,30M supported
        _nx_stream.unsubscribeOHLC("1M")# 5M,30M supported

    
    elif (ev['s'] == "closed" and ev["reason"] != "Unauthorized Access"):
        time.sleep(5)
        nx_stream.reconnect()
        

def stream_cb(_nx_stream, data):
    print(data)
    
if __name__ == "__main__":

    nxtrad_host = 'api.tradejini.com'

    # To get the apikey, Register with developer portal and select individual from create App.
    apikey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'

    password = "xxxxxxxxx"

     # Please refer the api-doc for complete details about twoFa and twoFatype.
    twoFa = "xxxx"
    twoFaType = "xxxx"

    access_token = getAccessToken(nxtrad_host, apikey, password, twoFa, twoFaType)

    if access_token is None:
        print("Auth: Access token not received. Check the apikey={} or host={} details".format(apikey, nxtrad_host))
        exit(0)

    # # Check the expiry of access token and persist it. 
    # # Reuse the access-token within the expiry period and avoid calling getAccessToken
    # print("Received Access-token={} for the apikey={}".format(access_token, apikey))
    

    # Auth-Token format is apikey:access-token
    auth_token = apikey + ':' + access_token

    nx_stream = NxtradStream(nxtrad_host, stream_cb=stream_cb, connect_cb=connect_cb)
    nx_stream.connect(auth_token)
