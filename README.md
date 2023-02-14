## campsite-checker

This is a python script which attempts to automate the process of reserving sites on recreation.gov.  It is especially made for sought-after campsites which have limited booking windows.

### Dependencies
* OS X
* Python
* Selenium (current release)
* geckodriver (current release)
* Firefox (current release)

### Current Use - This is a really rough script I put together and I don't actually know what I am doing, if it works it works, if it doesn't... yeah that's to be expected.
* I have updated this script to help automate the campsite reservation process at recreation.gov to help increase the likelyhood of getting a reservation.
* You will need to hardcode your recreation.gov account info into the checker.ini file.
* You may also need to adjust the execution time, it is currently set to 8am and I am not sure how this is affected by timezones. Please see line 113 in checker.py.
* I have also made a csv file for the campground I was using this for, you will need to edit the csv with the campsite ID for the GUI selection to work correctly. 
* Ideally you would want to start running this a few minutes before the reservations are released, I have not done extensive testing but this theory this should work if all the information is correct.


