"""Example for Secure Auctions as a double auction

We want to enable trading of goods between different parties by finding the best possible price for both parties.
This is done by using a double auction, where both sides create bids and offers.
For this we use a SecureBid and a SecureOffer Class based on lists

"""


from mpyc.runtime import mpc

from typing import List  
from dataclasses import dataclass 
from mpyc import asyncoro
import asyncio 
import numpy as np

secint=mpc.SecInt(32)

@dataclass
class Order(object):   
    Side: bool  
    Quantity: mpc.SecInt(32)
    Price: mpc.SecInt(32)  
    
class Market(object):
    def __init__(self, PriceRange: int):
        self.Bids: List[Order] = []
        self.Offers: List[Order] = []
        self.PriceRange: int = PriceRange

    def AddOrder(self, order: Order):
        if order.Side>0:
            self.Offers.append(order)
        else:
            self.Bids.append(order)  
    
    def ComputeClearingPrice(self) -> int:  
        l=mpc.input(secint(0),0)
        smallest_z=mpc.input(secint(100000),0)
        this_z=mpc.input(secint(0),0)
        for i in range (0, self.PriceRange):
            accumulatedSupply=0
            accumulatedDemand=0
            for offer in self.Offers:
                accumulatedSupply= accumulatedSupply+mpc.if_else(offer.Price <= i, offer.Quantity, 0)
            for bid in self.Bids:
                accumulatedDemand=accumulatedDemand+mpc.if_else(bid.Price >= i,bid.Quantity, 0)
            this_z=accumulatedSupply-accumulatedDemand
            l=mpc.if_else(mpc.abs(this_z)<mpc.abs(smallest_z),i,l)
            smallest_z=mpc.if_else(mpc.abs(this_z)<=mpc.abs(smallest_z),this_z,smallest_z)
            
        return l
        
        
                
async def main():               
    # Create market instance and test orders
    await mpc.start() 
    market = Market(PriceRange=100) 
    for i in range(0, 50):    
        buyOrder = Order( Side=False, Quantity=mpc.input(mpc.SecInt(32)(np.random.randint(0,100)),0), Price=mpc.input(mpc.SecInt(32)(np.random.randint(0,100)),0))
        market.AddOrder(buyOrder)
        sellOrder = Order(Side=True, Quantity=mpc.input(mpc.SecInt(32)(np.random.randint(0,100)),1), Price=mpc.input(mpc.SecInt(32)(np.random.randint(0,100)),1))  
        market.AddOrder(sellOrder) 

    price= market.ComputeClearingPrice()
    price=await mpc.output(price)
    print(price)
    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())