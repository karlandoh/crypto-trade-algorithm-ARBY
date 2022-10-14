import pyotp
#google = '' #BITTREX
#google = '' #EXMO
#google = '' #HITBTC2
google = '' #OCEANEX
google = '' #COINBASEPRO

totp = pyotp.TOTP(google)
