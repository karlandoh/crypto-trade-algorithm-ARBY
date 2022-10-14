![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/Logo%20Inverted%20Small.jpg)




I started this project in 2018 and used this project to help me learn the ins and outs of software engineering/development.

It is a sophisticated cryptocurrency arbitrage algorithm that consists of three components: arbySERVER, arbySELENIUM and arbyS. The algorithm was quite profitable throughout the years of the crypto bear market (2018-2020), and was able to profit on opportunities with up to 50000% gains.

It was created with Python, SQL, Selenium and bash scripts.

The API system was powered mostly by [CCXT trading library](https://github.com/ccxt/ccxt), known as a JavaScript / Python / PHP library for cryptocurrency trading and e-commerce with support for many bitcoin/ether/altcoin exchange markets and merchant APIs. I had also contributed towards fixing bugs for the python fork of the CCXT library throughout this time.


![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/Final%20Project.jpg)
![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/Diagram.jpg)
## Authors

- [@karlandoh](https://www.github.com/karlandoh)


## What is ARBY?

# [1/3] arbySERVER
Retrieve orderbook of every currency over 40+ exchanges.
Each currency will have it’s own SQL table with it’s respective price on that exchange.
Each currency will have it’s own process. In each process, each currency will have it’s own thread.

Coinmarketcap API will be used to determine how many SQL tables must exist and how many table entries (currencies) will exist in each table.

![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/arbySERVER.jpg)



# [2/3] arbySELENIUM
Scrape each exchange to determine if the currency is tradable and if I can withdraw or deposit from each exchange.

Also determine deposit and withdraw fee.

If the withdraw function is disabled, I can only compare a potential higher price, because the currency cannot leave the exchange.

If the deposit function is disabled, I can only compare a potential lower price, because the currency cannot enter the exchange.

If both directions are enabled, I can consider both prices.

Clear the SQL table every 7 days.

![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/arbySELENIUM.jpg)

# [3/3] arbyS
#### arbyMONITOR

* Sort profitable opportunties via percentage gain.
* Use order book to determine HOW much of each currency can be arbitraged.

* Filter trades according to specifications:
    * Ex. At least 5% percent gain.
    * At least 0.0001 BTC per trade for a decent profit..

#### arbyEXEC_real | arbyEXEC_sim

* The trades are filtered through a realistic 5 step simulation, incorporating withdrawal, deposit fees, and real orderbook data.

* The trades are executed according to how much currency is able to be bought or sold at each orderbook price.

* This ENSURES extremely accurate predictions of potential profits of each arbitrage opportunity.

#### arbyTELEGRAM

-	A bot was created to monitor trades, and receive alerts of potential trades. During sleep hours, arbyMONITOR was limited only to proven successful trades to avoid issues that had to be solved right away.
## arbySOUL

arbySOUL was able to monitor scenarios in which the rate of increase of my balance would dip below it's regression. In addition, it was able to analyze scenarios in which the arbitrage opportunity would disappear before I was able to capitalize off it (due to other competitive bots).

* There were a series of options available for every failed step. Sometimes money could be made from a failed trade due to price analysis!
   * This was done by modularizing each of the 5 trade steps of arbyTRADE_sim in order to either:
      * Evaluate the gain or loss if the trade was completed given the updated orderbook. A less than 5% loss was accepted and considered a “write off.”
      * Evaluate a “reversal” where the currency was sold at the current exchange.
      * Simply wait until the orderbook presents an opportunity for “break even, gain or less than 5% loss.”
   * The options were then shown via arbyTELEGRAM, and up to me to decide.

* ARBY operated best when there was an equal distribution of BTC amongst each exchange.
    * arbySOUL would analyze the price required to redistribute balances. A simple expense could be paid in order to distribute the balances evenly and optimize revenue growth.

* Each trade created a txt file with each step logged and timestamped. An additional txt file was created to log ALL trades of that day, and each day had it’s own folder. This was done via bash scripts.
    * This was to help troubleshoot issues and optimize profitable trades.
    * The state of each trade is saved on an excel sheet, to allow multiple trades to occur at once. Active trades are skipped by arbyMONITOR.
    
* A snapshot of each balance on all the exchanges occurs every 30 minutes via arbySOUL and combined to give a “master balance” which would increase over time. This master balance was then used for regression analysis with data software.

![App Screenshot](https://raw.githubusercontent.com/karlandoh/ARBY/master/Readme%20Diagrams/arbyS.jpg)
