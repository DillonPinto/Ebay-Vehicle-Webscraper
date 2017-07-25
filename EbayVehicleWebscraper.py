"""
Author: Dillon Pinto
Date: 7/24/2017

"""


from bs4 import BeautifulSoup as soup
from peewee import *
import requests
import time







db = SqliteDatabase('Cars_and_trucks.db')





class Vehicle(Model):

    
    #Default to -1 if info is not provided
    title = TextField(unique=True)
    numOfBids = IntegerField()#can be -1
    makeYear = IntegerField()#can be -1
    mileage = DoubleField()
    timeLeft = TimeField()#can be -1
    buyNowPrice = DoubleField()#can be -1
    bidPrice = DoubleField()#can be -1

    class Meta:
        database = db




def initializeDB():
    
    """Create the table and database if they don't exist"""
    db.connect()
    db.create_tables([Vehicle],safe=True)





class EbayWebScraper():

    


    

    def saveToDB(self,title1, numOfBids1, timeLeft1, bidPrice1,buyNowPrice1, makeYear1, mileage1):
        Vehicle.create(title = title1,
                       numOfBids=numOfBids1,
                       timeLeft = timeLeft1,
                       bidPrice = bidPrice1,
                       buyNowPrice = buyNowPrice1,
                       makeYear = makeYear1,
                       mileage = mileage1
                       )






        

    def generateURL(self, pageNum):

        #Generates and passes the URL to the requests
        if pageNum == 1:
            return "https://www.ebay.com/sch/Cars-Trucks-/6001/i.html"

        else:
            return "https://www.ebay.com/sch/Cars-Trucks/6001/i.html?_pgn="+str(pageNum)+"&_skc=100"






         

    def scrape(self, pageNum):

        #scrapes the web page, retrieves it's html text
        page = requests.get(self.generateURL(pageNum))
        page_html = page.text

        pageSoup = soup(page_html, "html.parser")
        
        return pageSoup






    def processData(self,title, numOfBids, timeLeft,bidPrice,buyNowPrice, makeYear, mileage):

            #Remove spaces and unnecessary words from the title
            title = ' '.join(title.split()).replace("New listing","")

            
            #Process the number of bids from a string phrase to an integer.
            numOfBids = numOfBids.replace("or Best Offer","-1").replace("Buy It Now","-1").replace(" bids",("")).replace(" bid",(""))
            numOfBids = int(' '.join(numOfBids.split()))

            #time in hours
            timeLeft = int(timeLeft)

            #Removes characters and casted to a float/double for possible further calculations
            bidPrice = float(' '.join(bidPrice.split()).replace("$","").replace(".","").replace(",","").split(" ", 1)[0])
            buyNowPrice = float(' '.join(buyNowPrice.split()).replace("$","").replace(".","").replace(",",""))

           


            #Casted to an integer type for possible further calculations

            try:
                makeYear = int(' '.join(makeYear.split()).replace("Year: ",""))

            except ValueError:
                makeYear = -1

            try:
                mileage = float(' '.join(mileage.split()).replace("Mileage: ","").replace(",",""))

            except ValueError:
                mileage = -1

            

            self.saveToDB(title, numOfBids, timeLeft,bidPrice,buyNowPrice, makeYear, mileage)            



            
            
                   
    def parse(self,pageSoup):
        
        containers = pageSoup.findAll("li",{"class":"sresult lvresult clearfix li"})




        for container in containers:

            #Get title
            titleContainer = container.find("a",{"class": "vip"})
            title = titleContainer.text

            #Get number of bids
            numOfBidsContainer = container.find("li",{"class": "lvformat"})
            numOfBids = numOfBidsContainer.text

            

            #Get time left for bidding to end
            try:

                timeLeft = container.find("li",{"class": "timeleft"}).span.span["timems"]
                
            except Exception as AttrError:
                #-1 due to time not given in listing
                timeLeft = -1


            
            #Get the current bid and the buy now price
            priceTag = container.find_all("li",{"class": "lvprice prc"})
            bidPrice = priceTag[0].text
            
            try:
                buyNowPrice = priceTag[1].text
            except Exception:
                buyNowPrice = "-1"




            extraInfoContainer = container.find("ul",{"class": "lvdetails left space-zero full-width"}).findChildren()
            
            makeYear = extraInfoContainer[0].text
            mileage = extraInfoContainer[1].text
            

                


            #process date to be stored
            self.processData(title, numOfBids, timeLeft,bidPrice,buyNowPrice, makeYear, mileage)



            
        


            

            

if __name__ == "__main__":

    
    initializeDB()
    EbWbScrpr = EbayWebScraper()

    for i in range(1,50):
        EbWbScrpr.parse( EbWbScrpr.scrape(i) )
