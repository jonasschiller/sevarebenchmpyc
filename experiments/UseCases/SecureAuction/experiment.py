"""Example for Secure Auctions as a double auction

We want to enable trading of goods between different parties by finding the best possible price for both parties.
This is done by using a double auction, where both sides create bids and offers.
For this we use a SecureBid and a SecureOffer Class based on lists

"""


from mpyc.runtime import mpc

from typing import List  
from dataclasses import dataclass  
import numpy as np
import sys

secint=mpc.SecInt(32)
@dataclass
class Order(object):   
    Side: bool  
    Quantity: mpc.SecInt(32)
    Price: mpc.SecInt(32)  
    
# class Market(object):
#     def __init__(self, PriceRange: int):
#         self.Bids: List[Order] = []
#         self.Offers: List[Order] = []
#         self.PriceRange: int = PriceRange

#     def AddOrder(self, order: Order):
#         if order.Side>0:
#             self.Offers.append(order)
#         else:
#             self.Bids.append(order)  
    
#     def ComputeClearingPrice(self) -> int:  
#         l=mpc.input(secint(0),0)
#         smallest_z=mpc.input(secint(100000),0)
#         this_z=mpc.input(secint(0),0)
#         for i in range (0, self.PriceRange):
#             accumulatedSupply=0
#             accumulatedDemand=0
#             for offer in self.Offers:
#                 accumulatedSupply= accumulatedSupply+mpc.if_else(offer.Price <= i, offer.Quantity, 0)
#             for bid in self.Bids:
#                 accumulatedDemand=accumulatedDemand+mpc.if_else(bid.Price >= i,bid.Quantity, 0)
#             this_z=accumulatedSupply-accumulatedDemand
#             l=mpc.if_else(mpc.abs(this_z)<mpc.abs(smallest_z),i,l)
#             smallest_z=mpc.if_else(mpc.abs(this_z)<=mpc.abs(smallest_z),this_z,smallest_z)
            
#         return l
 
class Market(object):
    def __init__(self, PriceRange: int):
        self.Bids: List[List[int]] = []
        self.Offers: List[List[int]] = []
        self.PriceRange: int = PriceRange

    def AddOrder(self, order: Order):
        if order.Side>0:
            self.Offers.append([order.Price, order.Quantity])
        else:
            self.Bids.append([order.Price, order.Quantity])  

async def get_arrays(Bids, Offers,size):
    bids_prices = mpc.SecInt(32).array(5*np.ones(size,np.int32))
    bids_quantities = mpc.SecInt(32).array(5*np.ones(size,np.int32))
    offers_prices = mpc.SecInt(32).array(5*np.ones(size,np.int32))
    offers_quantities = mpc.SecInt(32).array(5*np.ones(size,np.int32))
    return bids_prices, bids_quantities, offers_prices, offers_quantities

async def ComputeClearingPrice(Bids, Offers, PriceRange,size): 
    bids_prices, bids_quantities, offers_prices, offers_quantities= await get_arrays(Bids, Offers,size)
    l=secint(0)
    smallest_z=secint(100000)
    this_z=secint(0)
    for i in range (1, PriceRange):
        accumulatedSupply=0
        accumulatedDemand=0
        bid_comp=mpc.np_less(bids_prices,i)
        offer_comp=mpc.np_less(i,offers_prices)
        accumulatedSupply=mpc.sum(list(mpc.np_multiply(offers_quantities,offer_comp)))
        accumulatedDemand=mpc.sum(list(mpc.np_multiply(bids_quantities,bid_comp)))
        this_z=accumulatedSupply-accumulatedDemand
        l=mpc.if_else(mpc.abs(this_z)<mpc.abs(smallest_z),i,l)
        smallest_z=mpc.if_else(mpc.abs(this_z)<=mpc.abs(smallest_z),this_z,smallest_z)
    return l       
        
                
async def main():               
    # Create market instance and test orders
    if len(sys.argv) > 1:
        input_size = int(sys.argv[1])
        #price_range = int(sys.argv[2])
    else:
        print("No argument provided.")
    await mpc.start() 
    market = Market(PriceRange=100) 
    for i in range(0, input_size):    
        buyOrder = Order( Side=False, Quantity=mpc.SecInt(32)(5), Price=mpc.SecInt(32)(5))
        market.AddOrder(buyOrder)
        sellOrder = Order(Side=True, Quantity=mpc.SecInt(32)(5), Price=mpc.SecInt(32)(5))
        market.AddOrder(sellOrder) 

    price=await ComputeClearingPrice(market.Bids, market.Offers, 100,input_size)
    print(await mpc.output(price)) 
    await mpc.shutdown()
    
       
if __name__ == '__main__':
    mpc.run(main())