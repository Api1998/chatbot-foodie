from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db_connect import MySQLClient
import utils

# Initialize Mysql database client

db = MySQLClient(
        host='localhost',
        user='root',
        password='root',
        database='masala_kadai' 
    )

# Define lifespan for fastAPI app

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    print("Application startup: Database connected")

    yield 

    db.disconnect()
    print("Application shutdown: Database disconnected")

app = FastAPI(lifespan=lifespan)

in_progress_orders = {}    # Dictionary to store the on going orders based on session ids

# Endpoint that handles all the requests from Dialog flow

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = utils.get_session_id(output_contexts[0]["name"])

    intent_handler_dict = {
        'add order - context: ongoing-order': add_to_order,
        'remove order - context: ongoing-order': remove_from_order,
        'complete order - context: ongoing-order': complete_order,
        'track order - context: ongoing-tracking': track_order,
        'new order': new_order,
    }

    return intent_handler_dict[intent](parameters, session_id)


# Handler fucntions

def save_to_db(order: dict):
    next_order_id = db.get_next_order_id()

    # Insert individual items along with quantity in orders table
    for food_item, quantity in order.items():
        rcode = db.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1

    # Now insert order tracking status
    db.insert_order_tracking(next_order_id, "in progress")

    return next_order_id

def complete_order(parameters: dict, session_id: str):
    if session_id not in in_progress_orders:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = in_progress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db.get_total_order_price(order_id)

            fulfillment_text = f"Awesome. We have placed your order. " \
                           f"Here is your order id # {order_id}. " \
                           f"Your order total is {order_total} which you can pay at the time of delivery!"

        del in_progress_orders[session_id]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in in_progress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    food_items = parameters["food-item"]
    current_order = in_progress_orders[session_id]

    removed_items = []
    absent_items = []
    fulfillment_text = ""

    for item in food_items:
        if item not in current_order:
            absent_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text += f'Removed {",".join(removed_items)} from your order!'

    if len(absent_items) > 0:
        fulfillment_text += f' Your current order does not have {",".join(absent_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = utils.order_dict_to_str(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        new_order_dict = dict(zip(food_items, quantities))

        if session_id in in_progress_orders:
            current_order_dict = in_progress_orders[session_id]

            for key, value in new_order_dict.items():
                current_order_dict[key] = current_order_dict.get(key, 0) + value
            in_progress_orders[session_id] = current_order_dict
        else:
            in_progress_orders[session_id] = new_order_dict

        order_str = utils.order_dict_to_str(in_progress_orders[session_id])
        fulfillment_text = f"So far your order has: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = db.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for your order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with given order id: {order_id} please recheck the order id"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def new_order(parameters: dict, session_id: str):

    if session_id in in_progress_orders:
        del in_progress_orders[session_id]
        fulfillment_text = """Your incomplete order is dropped.
        Starting new order. Specify food items and quantities. For example, you can say, (I would like to order two samosa and one tandoori roti). 
        Also, we have only the following items on our menu: Paneer Tika, Butter Chicken, Idly, Masala Tea, Masala Dosa, Vegetable Biryani, Tandoori roti, and Samosa.
        """

    else:
        fulfillment_text = """Ok, starting a new order. You can say things like (I want two Masala Dosa and one Masala Tea). 
        Make sure to specify a quantity for every food item! Also, we have only the following items on our menu: Paneer Tika, Butter Chicken, Idly, Masala Tea, Masala Dosa, Vegetable Biryani, Tandoori roti, and Samosa.
        """

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })