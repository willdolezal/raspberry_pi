#!/usr/bin/env python
# # -*- coding: utf-8 -*-

"""StockTicker.Py : A python script that makes use of ScrollPhat HD on Raspberyr Pi to produce live
near real-tme stock quotes. Makes use of screen scraping (or Stock API) to grab specific stock prices
and displays them in a standard scrolling ticker format. Heavily borrows code for Advanced Scrolling 
Pimoroni library to make the ticker have a more animated look.


Requires: Raspberry Pi + ScrollPhat HD  	
https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-scroll-phat-hd

Author: Abrandao.com
Date: 2-25-2018


"""

import subprocess
import socket
import os
import time
import urllib2
import re
from datetime import datetime
try:
  import scrollphathd
except ImportError:
  raise ImportError('Error Importing Module: scrollphathd Check hardware')


print("""
StockTicker.py a Scroll pHAT HD python script for Live stock quotes.
Advanced scrolling example which displays a message line-by-line
Press Ctrl+C to exit.
""")

#Ticker mode: 
# True: a scrolling ticker refrreshing all stocks continuously
# False: on specific alert price/percent change  displays stock
classic_ticker_mode=True # set to False to use Alert style

#Stock symbols Change stock symbols to match your favorites 
#percent represents trigger % change value stock to appear when classic_ticker_mode=False
stock_tickers = {'DJI': 0.02, 'F': 0.02, "T": 0.02,"GE": 0.02,"BP": 0.02,"TEVA": 0.02,"ROKU": 0.02,"GRMN": 0.02,"GLD": 0.02 }


# Uncomment to rotate 180 degrees, useful for flippy rpi upside down easier with usb cord
scrollphathd.rotate(180)

#Ticker Title
TICKER_TITLE="Stock Ticker"

# Dial down the brightness
scrollphathd.set_brightness(0.2)

# If rewind is True the scroll effect will rapidly rewind after the last line
rewind = True

#how long to wait secs.  before refreshing data and blanking screen
REFRESH_INTERVAL = 10

# Delay is the time (in seconds) between each pixel scrolled
delay = 0.02


#LCD Lines buffer -Global 
lines = []

def is_connected(ip='172.217.12.142'):  
  try:
     # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((ip, 80), 2)
    return True
  except:
     pass
  return False

def scrollLine(msg):
	scrollphathd.write_string(msg, x=0, y=0, font=font5x7, brightness=0.1)
	scrollphathd.show()
	scrollphathd.scroll()

	return   

# Call external shell script to try and reconnect...
# source shell script: https://gist.github.com/mharizanov/5325450	
def wifi_reconnect():
	global lines
	result=False

	print "Trying to reconnect:"
	scrollLine("Trying to reconnect...Reseting Wlan0 ")
	# try to recover the connection by resetting the LAN	
	return result


def stockquote(symbol):
    quote=[]

    # Stock screen scraping code,  I know this is not the best way ... its quick and dirty :)
    # this can be revised to use an API-key based stock price tool
    # I just wanted something simple and frictionless to get this out.. 
    #  Consider rewriting this section using  https://pypi.python.org/pypi/googlefinance  
    # or using pandas-datareader https://github.com/pydata/pandas-datareader 
    # package allows for reading in data from sources such as Google, Yahoo! Finance, World Bank,…
    # see example here: https://www.datacamp.com/community/tutorials/finance-python-trading

    # but for this example lets screen scrape 
    base_url = 'http://finance.google.com/finance?q='
    content = urllib2.urlopen(base_url + symbol).read()
    m = re.search('id="ref_(.*?)">(.*?)<', content)
    q = re.search('id="ref_(.*?)_c">(.*?)<', content)
    z = re.search('id="ref_(.*?)_c">(.*?)<', content)
    if m:
		quote.append( m.group(2) )
		quote.append( q.group(2) )
		quote.append( z.group(2) )
    else:
        quote = 'no quote available for: ' + symbol
    return quote

	
def get_stock_quotes():
	global classic_ticker_mode
	stock_quote_lines=''
	
	for symbol, pct in stock_tickers.items():
		stock_val =stockquote(symbol)
		print "Stocks:  "+symbol+ " $"+stock_val[0]+"  "+stock_val[1]

		if classic_ticker_mode==True :
			stock_quote_lines+= symbol+" "+ stock_val[0] + " "+ stock_val[1] + " | "
		else:
			if stock_val[3] >= pct or stock_val[3] <= pct:
				stock_quote_lines+= symbol+" "+ stock_val[0] + " "+ stock_val[1] + " "

	return stock_quote_lines
	



def  load_data():
	# empty lcd buffer
	lines[:] = []

	print  "Gettig Ticker DATA ..."	
	lines.append(TICKER_TITLE )

	#get Stock quotes
	lines.append( get_stock_quotes() )
	
	now = datetime.now().strftime('%m-%d-%y %H:%M %p')
	lines.append(now )
	print "Time: "+now
	return


def startlcd():
	global scrollphathd, lines , lengths, line_height,offset_left
	
#  Clear buffer
	scrollphathd.clear()  # so we can rebuild it
	scrollphathd.show()


	if is_connected() == False:
		print "No Internet connection available. No data to display" #getip addressss
		lines.append("IP: "+getip_address() )
		lines.append("NO Internet Connection.");

		scrollLine(lines);
	else:
		print "Initial data load"
		load_data()


# Determine how far apart each line should be spaced vertically
	line_height = scrollphathd.DISPLAY_HEIGHT + 2

	# Store the left offset for each subsequent line (starts at the end of the last line)
	offset_left = 0

	# Draw each line in lines to the Scroll pHAT HD buffer
	# scrollphathd.write_string returns the length of the written string in pixels
	# we can use this length to calculate the offset of the next line
	# and will also use it later for the scrolling effect.
	lengths = [0] * len(lines)

	for line, text in enumerate(lines):
		lengths[line] = scrollphathd.write_string(text, x=offset_left, y=line_height * line)
		offset_left += lengths[line]

	# This adds a little bit of horizontal/vertical padding into the buffer at
	# the very bottom right of the last line to keep things wrapping nicely.
	scrollphathd.set_pixel(offset_left - 1, (len(lines) * line_height) - 1, 0)
	return


#check for hardware and make sure no GPIO / hardware faults
  
try:  
   print "Checking Hardware ScrollPhat HD is availble"  
   scrollphathd.scroll_to(0, 0)
   print " Passed!"  

    
except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print "\n", counter # print value of counter  
  
except:  
    # this catches ALL other exceptions including errors.  
    print "Hardware Error SchrollPhat HD is no responding. Check hardware."  
  
#finally:  
#    GPIO.cleanup() # this ensures a clean exit  

### Start main loading 
startlcd()


	
while True:
    # Reset the animation
    scrollphathd.scroll_to(0, 0)
    scrollphathd.show()

    # Keep track of the X and Y position for the rewind effect
    pos_x = 0
    pos_y = 0

    for current_line, line_length in enumerate(lengths):
        # Delay a slightly longer time at the start of each line
        time.sleep(delay*10)

        # Scroll to the end of the current line
        for y in range(line_length):
            scrollphathd.scroll(1, 0)
            pos_x += 1
            time.sleep(delay)
            scrollphathd.show()

        # If we're currently on the very last line and rewind is True
        # We should rapidly scroll back to the first line.
        if current_line == len(lines) - 1 and rewind:
           # for y in range(pos_y):
           #     scrollphathd.scroll(-int(pos_x/pos_y), -1)
           #     scrollphathd.show()
           #     time.sleep(delay)
           print "Sleeping for "+str(REFRESH_INTERVAL)+" seconds"
           time.sleep(REFRESH_INTERVAL)   
           print "Awake refreshing data..."
           startlcd()  #reload new data into LCD display
         

        # Otherwise, progress to the next line by scrolling upwards
        else:
            for x in range(line_height):
                scrollphathd.scroll(0, 1)
                pos_y += 1
                scrollphathd.show()
                time.sleep(delay)
