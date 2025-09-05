
This SDK is compatible with Python3

sudo apt install python3-pip

pip3 install websocket-client

Refer example.py for getting the access token and subscribing for tokens.

To Run
python3 example.py

## Authorization

- Nxtrad stream requires 'authToken' for authorization.
- AuthToken is a combination of APIkey and accessToken in the format '<APIkey>:<accessToken>'
- APIKey - In order to get the API key, please register at developer portal [https://api.tradejini.com/developer-portal/auth/login]. Once you register with developer portal, an application should be created to generate the API key.
- accessToken - Access token can be received in the response of access-token service or individual token service. Refer API doc website [https://api.tradejini.com/api-doc/] for more details.

- In case if the authtoken is expired or invalid you will get Close message with code "4001" and message as "Unauthorized Access".

In case if you have apikey and access token handy. Please form the authtoken and subscribe for prices else generate it from developer portal api document  [https://api.tradejini.com/api-doc/].

## Streaming Symbol Logic

    Nxtrad stream requires streaming symbol for price subscription. Stream symbol is a combination of exchangeToken and exchangeName in the format <exchangeToken>_<exchangeName>

    exchangeToken - 'excToken' field received from ScripMaster Data API response.
    exchangeName -  exchangeName should be retrieved from the field 'ID'  which is received from ScripMaster Data API response.

 For Example: For ACC NSE symbol, stream symbol would be '22_NSE'

    - Exchange token '22' received from the field 'excToken' 
    - Exchange Name should be retrieved from ID like below,

    For ACC, the ID received from scripmaster data api is EQT_ACC_EQ_NSE (Reference: <idFormat from API : INSTRUMENT_SYMBOL_SERIES_EXCHANGE>)

    The ID should be split using the character underscore'_' and the last string would be retrieved as exchange 'NSE'

    Each Id format mentioned in ScripMaster Groups API Split the 'id' field based on the format provided and use the fields such as exchange, basesymbol, expiry, optionType, Strike Price etc.

 As like above example you can frame streamSymbol list. Socket implementation and how to subscribe for prices details are given below,

## Implementation

- connect will create socket connection for host with particular auth Token.
- subscribeL1 will send level 1 request and provides you data apart from market depth.
- subscribeL1SnapShot will send level 1 snapshot request and provides you snapshot [A last tick data with all fields only once] data apart from market depth.
- subscribeL2 will send level 2 request and provides you data for market depth.
- subscribeL2SnapShot will send level 2 request and provides you snapshot data for market depth.
- subscribeGreeks will send Option greeks request and provides you Option Greeks data.
- subscribeGreeksSnapShot will send Option greeks request and provides you Option Greeks snapshot data.
- subscribeEvents will send a request for an events subscription and provides you the data when subscribed event is triggered. Example change in order status, Change in positions etc.
- subscribeOHLC will send OHLC request with symbol list, interval and provides you OHLC, Volume, time for the particular minute.
- unsubscribeL1, unsubscribeL2, unsubscribeEvents, unsubscribeGreeks and unsubscribeOHLC your unsubcribe the request made priorly respectively.

### Note

    If your are subscribing for some scrips. On next new subscription request the old symbols subscribed will be unsubscribed and only newer subscription list will be taken into count.
    Example : let say on first subscription Symbols [A, B, C, D] are sent . On subsequent subscription request you are sending [E, F].
    Now only E and F will get streamed [A, B, C, D] are unsubscribed.
    
    **if you are calling unsubscribeL1 then all l1 Subscriptions subscribed by you also getUnsubscribed.**

    **if you are calling unsubscribeOHLC then all OHLC Subscriptions made by you only for the particular interval will be unsubscribed other interval subscriptions made by you will be persisted.**

- disconnect will close the socket connection.
- reconnect will create new connection based on the auth Token which passed for connect.
- stream_cb is the method where you get the subscribed streaming response in the data. Here we used it for printing you can use the same as per your wish. Kindly refer below Fields description for response fields.
- connect_cb will transfer the status of socket along with message. Kindly refer below Message description for socket status and message.

## Fields description

    exchSeg - Exchange Segment
    token - Exchange Token
    precision - Decimal precision
    ltp - last traded price
    open - Day's pen price
    high - Day's High price
    low - Day's Low price
    close - Day's Close price
    chng - Change
    chngPer - Change percentage
    atp - Average traded price
    yHigh - 52 week high
    yLow - 52 week low
    ltq - Last traded quantity
    vol - Volume traded today
    ttv - Total traded value
    ucl - Upper circuit limit
    lcl - Lower circuit limit
    OI - Open intrest
    OIChngPer - Open intrest change percentage
    ltt - Last traded time
    bidPrice - Bid price
    qty - Bid/Ask quantity
    no - Bid/Ask orders
    askPrice - Ask price
    symbol - Subscribed symbol for identification.(Combined Exchange Token + Exchange Segment)
    totBuyQty - Total buy quantity
    totSellQty - Total sell quantity
    prevOI - Previous OI 
    dayHighOI - Intraday High OI
    dayLowOI- Intraday Low OI
    marketStatus - Current market status for particular exchange.
    spotPrice - Underlying Spot Symbol price [Available for derivatives]
    dayClose - current day's Close price.
    vwap - computed volume weighted average price.
    itm - In the money proablity
    iv - Implied Volatility
    delta - Delta Option greeks
    gamma - Gamma Option greeks
    theta - Theta Option greeks
    rho - Rho Option greeks
    vega - Vega Option greeks
    highiv - Day high IV
    lowiv - Day low IV
    time - candle time for chart
    type - candle type [support 1M, 5M, 30M]
    minuteOi - Chart Minute OI

### Message description

    Error : {"s": "error", "reason": <error Message>}

    Close : {"s": "closed", "code": <close code>, "reason": <close Message>}

    Open : {"s": "connected"}

## Events Info

### Available Events

    - orders [*Event will be triggered if there is any changes in orders.] 
    - positions [*Event will be triggered if there is any changes in positions.] 
    - trades [*Event will be triggered if trades are happened sucessfully.]

### Events Field description

    type - order type
    trdSym - Trading symbol
    qty -  Quantity
    product - product id
    price - Price to the order.
    * For Event type 'orders' the price refers to orderPrice.
    * For Event type 'trades' the price refers to fillPrice.
    side - order action
    status - order status
    orderId - Exchange order id
    evntType - Event type identifier (Ex : orders, positions or trades)
    exch - Exchange Segment
    msg - order message
    reason - rejected reason
    orderTime - time the order was placed
    actStatus - This field provides the status of the modification or cancellation request of an order. (values: open, closed, completed, rejected)  
