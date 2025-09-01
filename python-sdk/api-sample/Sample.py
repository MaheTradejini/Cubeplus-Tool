## After running python3 setup.py install --user

import time
import openapi_client
from openapi_client.api import authorization_api
from openapi_client.api import orders_api
from openapi_client.models.place_order_response import PlaceOrderResponse
from openapi_client.models.get_orders200_response import OrdersResponse
from openapi_client.models.get_positions200_response import PositionsResponse
from openapi_client.models.get_holdings200_response import HoldingResponse

# Api key can be obtained from the developer portal https://app.tradejini.com/developer-portal
apikey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Form the auth key in the format: Bearer<space><ApiKey>
authKey = "Bearer " + apikey

# Get the access token by providing\ the user credentials and the authToken
password = "xxxxxxx"
two_fa = "xxxxxx"
two_fa_typ = "xxxxxx"


def set_access_token(client):
    with client:
        try:
            auth_api = authorization_api.AuthorizationApi(client)
            api_response = auth_api.updated_individual_token(authKey, password, two_fa, two_fa_typ)
            auth_token = apikey + ":" + api_response.access_token
            client.configuration.access_token = auth_token
        except openapi_client.ApiException as e:
            # Change to logger if you wish
            print("Exception when calling AuthorizationApi->updated_individual_token: %s\n" % e)


def place_limit_order(client):
    with client:
        order_placement = orders_api.OrdersApi(client)
        place_order_resp = order_placement.place_order("EQT_RELIANCE_EQ_NSE", 10, "buy", "limit", "delivery", "day",
                                                       limit_price=2400.55, trig_price=0.00, disc_qty=3,
                                                       amo=False, mkt_prot=2.0, remarks="")
        if isinstance(place_order_resp.actual_instance, PlaceOrderResponse):
            resp = place_order_resp.actual_instance
            if resp.s.lower() == "ok":
                # handle as your wish
                print("msg " + resp.d.msg)
                print("OrderId: " + resp.d.order_id)
            else:
                # handle as your wish
                print("Error : " + resp.to_json())
        else:
            # handle as your wish
            print("Error : Not Success Response  : " + place_order_resp.to_json())


def fetch_order_book(client):
    with client:
        orders = orders_api.OrdersApi(client)
        orders_resp = orders.get_orders(False)
        if isinstance(orders_resp.actual_instance, OrdersResponse):
            resp = orders_resp.actual_instance
            if resp.s.lower() == "ok":
                # handle as your wish
                print("Order Records :: " + resp.to_json())
            else:
                # handle as your wish
                print("Error : " + resp.to_json())
        else:
            # handle as your wish
            print("Error : Not Success Response  : " + orders_resp.to_json())


def fetch_positions(client):
    with client:
        positions = orders_api.OrdersApi(client)
        positions_resp = positions.get_positions(False)
        if isinstance(positions_resp.actual_instance, PositionsResponse):
            resp = positions_resp.actual_instance
            if resp.s.lower() == "ok":
                print("Position Records :: " + resp.to_json())
            else:
                print("Error : " + resp.to_json())
        else:
            # handle as your wish
            print("Error : Not Success Response  : " + positions_resp.to_json())


def fetch_holdings(client):
    with client:
        holdings = orders_api.OrdersApi(client)
        holdings_resp = holdings.get_holdings(False)
        if isinstance(holdings_resp.actual_instance, HoldingResponse):
            resp = holdings_resp.actual_instance
            if resp.s.lower() == "ok":
                # handle as your wish
                print("Holdings Records :: " + resp.to_json())
            else:
                # handle as your wish
                print("Error : " + resp.to_json())
        else:
            # handle as your wish
            print("Error : Not Success Response  : " + holdings_resp.to_json())


if __name__ == '__main__':
    api_client = openapi_client.ApiClient()

    set_access_token(api_client)

    place_limit_order(api_client)

    fetch_order_book(api_client)

    fetch_positions(api_client)

    fetch_holdings(api_client)
