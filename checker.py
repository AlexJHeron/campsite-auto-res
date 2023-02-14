#import modules

import ast
import configparser
import time
import ntplib
import schedule
import PySimpleGUI as sg
import csv
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException 

#read checker.ini file
config = configparser.ConfigParser()

config.read('checker.ini')

RETRIES = int(config.get("common", "retries"))
USERNAME = config.get("common", "username")
PASSWORD = config.get("common", "password")
NUM_RESERVATIONS = int(config.get("common", "num_reservations"))

#read csv file which should house the list of campsites at the campground
def import_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader) # skip the header row
        return [row for row in reader]


filename = "glacierviewcampground.csv"
options = import_csv(filename)

numbers = [str(i) for i in range(1, 11)]

#PySimpleGui 
layout =[  
[sg.CalendarButton('Click here to choose check-in date', close_when_date_chosen=True,  target='-IN-', location=(800,600), no_titlebar=False, format='%m/%d/%Y' ), sg.Input(key='-IN-', size=(20,1)), ],
[sg.Text('How many days would you like to stay for'), sg.Combo(numbers, size=(10, 1), key="number")],
[sg.Text('Select a campsite:'), sg.Combo(list(map(lambda x: f'{x[0]} - {x[1]}', options)), size=(30, 1), key='option')],
[sg.Button('START'), sg.Button('CANCEL')]
]

Window = sg.Window ('Campsite Reservation Tool', layout)

#pull time from time.nist.gov which should account for network latency according to their documentation
def get_current_time():
    c = ntplib.NTPClient()
    response = c.request('time.nist.gov')
    return response.tx_time

def add_to_cart():
	print("Executing action at", time.ctime(get_current_time()))
	elem = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, 'add-cart-campsite')))
	elem.click()

def animate_loading():
    while True:
        for i in range(4):
            sys.stdout.write('\rLoading' + '.' * i)
            time.sleep(0.5)
            sys.stdout.flush()

def checksites():
	site_ready = False
	num_retries = 0

	# Loop through sites // not needed since running on one campsite at a time
	for site in SITES:

		url = url_request.format(**site)
		driver.get(url)

	# Enter username
	username_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'ga-global-nav-log-in-link')))
	username_field = driver.find_element(By.ID, 'ga-global-nav-log-in-link').click()
	username_field = driver.find_element(By.ID, 'email')
	username_field.send_keys(USERNAME);

	# Enter password
	password_field = driver.find_element(By.ID, 'rec-acct-sign-in-password')
	password_field.send_keys(PASSWORD);
	password_field.send_keys(Keys.ENTER);

	scroll_locator = (By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div[2]/div/div/div[1]/div/ul/li[1]/button")
	scroll = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(scroll_locator))
	scroll.click()
		
	while site_ready == False:
			#error checking for if site is available
			try: #check to see if your check in date is available
				elem = driver.find_element(By.XPATH, '//*[@aria-label="Choose '+ day_of_week+', '+ check_in_date +' as your check-in date. It’s available."]')
			except NoSuchElementException:		
				if num_retries < RETRIES:
					print('Not yet reservable, retrying...')
					num_retries += 1
					driver.refresh()
					scroll_locator = (By.XPATH, "/html/body/div[1]/div/div[4]/div/div[1]/div[2]/div[2]/div/div/div[1]/div/ul/li[1]/button")
					scroll = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(scroll_locator))
					scroll.click()
				else:
					print('Not yet reservable. Exceeded number of retries.')
					return False
			
			else: #select check in and check out dates
				site_ready = True
				#click on check in day
				elem = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Choose '+ day_of_week+', '+ check_in_date +' as your check-in date. It’s available."]')))	
				elem.click()
				
				#click on check out day
				elem = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Choose '+ day_of_week2+', '+ check_out_date +' as your check-out date. It’s available."]')))	
				elem.click()
				
				print('Ready to add to cart')
				



while True: #using PySimpleGui gather information from users and write it to the checker.ini file
	Event, Values = Window.read()
	if Event == sg.WIN_CLOSED or Event == 'CANCEL' :
		break
	if Event == 'START':
		date_string = Values["-IN-"]
		selected_number = int(Values["number"])
		option = Values['option']
		for row in options:
			if f'{row[0]} - {row[1]}' == option:
				campsite = row[2]
				config['reservation_1'] = {'ARV_DATE': date_string, 'LENGTH_OF_STAY': selected_number, 'sites': [{'site_id': campsite}]}
		with open('checker.ini', 'w') as configfile:
			config.write(configfile)
		break	
Window.close()           
#this is where the magic happens, get the information submitted via the GUI and make them into useable variables        
for i in range(NUM_RESERVATIONS):
	count = str(i + 1)
	options = Options()
	driver = webdriver.Firefox(options=options)
	driver.maximize_window()
	
	ARV_DATE = config.get("reservation_" + count, "arv_date")
	LENGTH_OF_STAY = config.get("reservation_" + count, "length_of_stay")
	SITES = ast.literal_eval(config.get("reservation_" + count, "sites"))
	
	LENGTH_OF_STAY =int(LENGTH_OF_STAY)
	
	#convert check in date to useable format and add number of days of stay to find check out date
	date_in = ARV_DATE
	date_convert = datetime.strptime(date_in, '%m/%d/%Y')
	check_in_date = datetime.strftime(date_convert, '%B %-d, %Y')
	day_of_week = date_convert.strftime('%A')
	date_convert2 = datetime.strptime(date_in, '%m/%d/%Y')
	new_date = date_convert2 + timedelta(days=LENGTH_OF_STAY)
	check_out_date = datetime.strftime(new_date, '%B %-d, %Y')
	day_of_week2 = new_date.strftime('%A')
	url_request = 'http://www.recreation.gov/camping/campsites/{site_id}'
	selected_site = checksites()
	break

#add to cart at the right time!
#currently set to execute action at 8am, might need this to change due to timezone, I have not done extensive testing.
stop_animation = False
while not stop_animation:
    animate_loading()
    schedule.every().day.at("08:00").do(add_to_cart)
    while True:
        schedule.run_pending()
        if schedule.jobs:
            stop_animation = True
            break
        time.sleep(1)





	
