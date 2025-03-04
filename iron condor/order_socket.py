
from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=14)


def order_handler(o):
    print(o)



ib.newOrderEvent += order_handler
ib.orderStatusEvent += order_handler
ib.cancelOrderEvent += order_handler

ib.run()