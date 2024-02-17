import xml.etree.ElementTree as ET
import time
from datetime import datetime
class Order:
    def __init__(self, order_id, operation, price, volume):
        self.order_id = order_id
        self.operation = operation
        self.price = price
        self.volume = volume

class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []

def process_order_file(file_path):
    order_books = {}
    start_time = time.time()

    start_datetime = datetime.fromtimestamp(start_time)
    print(f"Processing started at: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    

    tree = ET.parse(file_path)
    root = tree.getroot()

    for order_elem in root:
        if order_elem.tag == "AddOrder":
            book_name = order_elem.attrib["book"]
            order_id = int(order_elem.attrib["orderId"])
            operation = order_elem.attrib["operation"]
            price = float(order_elem.attrib["price"])
            volume = int(order_elem.attrib["volume"])

            if book_name not in order_books:
                order_books[book_name] = OrderBook()

            order_book = order_books[book_name]
            new_order = Order(order_id, operation, price, volume)

            if operation == "BUY":
                execute_and_remove_sell_orders(order_book, new_order)
                if new_order.volume > 0:
                    insert_order(order_book.buy_orders, new_order)
            else:
                execute_and_remove_buy_orders(order_book, new_order)
                if new_order.volume > 0:
                    insert_order(order_book.sell_orders, new_order)

    for book_name, order_book in order_books.items():
        print(f"book: {book_name}")
        print(" Buy -- Sell")
        print("==================================")
        for buy_order, sell_order in zip(order_book.buy_orders, order_book.sell_orders):
            print(f" {buy_order.volume}@{buy_order.price:.2f} -- {sell_order.volume}@{sell_order.price:.2f}")
        if len(order_book.buy_orders) > len(order_book.sell_orders):
            for buy_order in order_book.buy_orders[len(order_book.sell_orders):]:
                print(f" {buy_order.volume}@{buy_order.price:.2f} --")
        elif len(order_book.sell_orders) > len(order_book.buy_orders):
            for sell_order in order_book.sell_orders[len(order_book.buy_orders):]:
                print(f" -- {sell_order.volume}@{sell_order.price:.2f}")

    end_time = time.time()
    end_datetime = datetime.fromtimestamp(end_time)
    
    print(f"Processing completed at: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Processing Duration: {:.3f} seconds".format(end_time - start_time))


def execute_and_remove_sell_orders(order_book, new_order):
    sell_orders = order_book.sell_orders
    i = 0
    while i < len(sell_orders):
        sell_order = sell_orders[i]
        if new_order.price >= sell_order.price:
            execution_volume = min(new_order.volume, sell_order.volume)
            new_order.volume -= execution_volume
            sell_order.volume -= execution_volume
            if sell_order.volume == 0:
                sell_orders.pop(i)
            if new_order.volume == 0:
                break
        else:
            break

def execute_and_remove_buy_orders(order_book, new_order):
    buy_orders = order_book.buy_orders
    i = 0
    while i < len(buy_orders):
        buy_order = buy_orders[i]
        if new_order.price <= buy_order.price:
            execution_volume = min(new_order.volume, buy_order.volume)
            new_order.volume -= execution_volume
            buy_order.volume -= execution_volume
            if buy_order.volume == 0:
                buy_orders.pop(i)
            if new_order.volume == 0:
                break
        else:
            break

def insert_order(orders, new_order):
    for i, order in enumerate(orders):
        if new_order.operation == "BUY" and new_order.price > order.price:
            break
        if new_order.operation == "SELL" and new_order.price < order.price:
            break
    else:
        i = len(orders)
    orders.insert(i, new_order)

if __name__ == "__main__":
    process_order_file("orders 1.xml")
