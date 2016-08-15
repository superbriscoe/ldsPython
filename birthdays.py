from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
import re
from datetime import date, timedelta, datetime
import calendar
import pprint

def convertDate(dateStr, format1, format2=None):
    date = datetime.strptime(dateStr, format1).date()
    if format2 is None:
        return date
    return date.strftime(format2)

def getBirthdaysFromSite():
    os.environ["webdriver.chrome.driver"] = os.path.join(os.getcwd(),"chromedriver")

    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://ident.lds.org/sso/UI/Login?service=credentials")
    assert "Sign in" in driver.title
    elem = driver.find_element_by_name("IDToken1")
    elem.clear()
    elem.send_keys("AndrewBriscoe")
    elem = driver.find_element_by_name("IDToken2")
    elem.clear()
    elem.send_keys("Lindsay121")
    elem.send_keys(Keys.RETURN)

    driver.get("https://www.lds.org/mls/mbr/report/birthday-list?lang=eng")
    assert "Birthday List" in driver.title

    time.sleep(4)
    el = driver.find_element_by_id('month')
    for option in el.find_elements_by_tag_name('option'):
        if option.text == 'January':
            option.click() # select() in earlier versions of webdriver
            break
    time.sleep(4)
    el = driver.find_element_by_id('months')
    for option in el.find_elements_by_tag_name('option'):
        if option.text == 'Months to show: 12':
            option.click() # select() in earlier versions of webdriver
            break

    time.sleep(1) 
    rows = driver.find_elements_by_class_name("vcard")
    birthdays = {}
    for row in rows:
        bday = row.find_element_by_class_name("bday").text 
        birthday = datetime.strptime(bday + ", 2016", "%d %b, %Y").date()
        name = row.find_element_by_class_name("first").text
        name_parts = [x for x in re.split(" |,", name) if x != ""]
        name = "{} {}".format(name_parts[1], name_parts[0])
        values = birthdays.get(bday,[])
        values.append(name)
        birthdays[birthday] = values
    driver.close()
    
    return birthdays

def getSundayDate():
    today = date.today()

    if today.weekday() == calendar.SUNDAY:
        #Today is Sunday so pretend like its monday
        today = today + timedelta(days=1)

    return today + timedelta((calendar.SUNDAY - today.weekday())%7)

def getDateRanges(sunday):
    pMonday = sunday - timedelta(days=6)
    nSaturday = sunday + timedelta(days=6)
    return (pMonday, nSaturday)



def getBirthdays(birthdays, start, end):
    birthdays_in_range = [birthday for (birthday, values) in birthdays.items() if birthday >= start and birthday <= end]
    birthdayLists = ""
    for birthday in sorted(birthdays_in_range):
        date = birthday.strftime("%d %b")
        names = ",".join(birthdays[birthday])
        birthdayLists = birthdayLists + "{}  {}\n".format(date, names)
    return birthdayLists
   

def generateBirthdayList():
    birthdays = getBirthdaysFromSite()
    sunday = getSundayDate()
    start, end = getDateRanges(sunday)
    return getBirthdays(birthdays, start, end)


print(generateBirthdayList())