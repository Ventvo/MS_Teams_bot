from typing import Any

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os.path
from os import path
import sqlite3
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import discord_webhook

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1,
    "profile.default_content_setting_values.notifications": 1
})

# driver = webdriver.Chrome(chrome_options=opt,service_log_path='NUL')
driver = None
URL = "https://teams.microsoft.com"

# put your teams credentials here
credentials = {'email': '#enter your mail', 'passwd': '#your password'}


def login():
    global driver
    # login required
    print("logging in")
    email_field = driver.find_element_by_xpath('//*[@id="i0116"]')
    email_field.click()
    email_field.send_keys(credentials['email'])
    driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # Next button
    time.sleep(5)
    password_field = driver.find_element_by_xpath('//*[@id="i0118"]')
    password_field.click()
    password_field.send_keys(credentials['passwd'])
    driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # Sign in button
    time.sleep(5)
    driver.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # remember login
    time.sleep(5)


# return driver


def createDB():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE timetable(class text, start_time text, end_time text, day text)''')
    conn.commit()
    conn.close()
    print("Created timetable Database")


def validate_input(regex, inp):
    if not re.match(regex, inp):
        return False
    return True


def validate_day(inp):
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    if inp.lower() in days:
        return True
    else:
        return False


def add_timetable():
    if not path.exists("timetable.db"):
        createDB()
    op_tt = int(input("1. Add class\n2. Done adding\nEnter option : "))
    while op_tt == 1:
        name = input("Enter class name : ")
        start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
        while not validate_input(r"\d\d:\d\d", start_time):
            print("Invalid input, try again")
            start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

        end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
        while not validate_input(r"\d\d:\d\d", end_time):
            print("Invalid input, try again")
            end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

        day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
        while not (validate_day(day.strip())):
            print("Invalid input, try again")
            end_time = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")

        conn = sqlite3.connect('timetable.db')
        c = conn.cursor()

        # Insert a row of data
        c.execute("INSERT INTO timetable VALUES ('%s','%s','%s','%s')" % (name, start_time, end_time, day))

        conn.commit()
        conn.close()

        print("Class added to database\n")

        op_tt = int(input("1. Add class\n2. Done adding\nEnter option : "))


def view_timetable():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM timetable'):
        print(row)
    conn.close()


def join_class(class_name, start_time, end_time):
    global driver

    # try_time = int(start_time.split(":")[1]) + 15
    # try_time = start_time.split(":")[0] + ":" + str(try_time)

    time.sleep(5)

    classes_available = driver.find_elements_by_class_name("name-channel-type")

    for i in classes_available:
        if class_name.lower() in i.get_attribute('innerHTML').lower():
            print("JOINING CLASS ", class_name)
            i.click()
            break

    time.sleep(4)

    try:
        join_button = driver.find_element_by_class_name("ts-calling-join-button")
        join_button.click()

    except any:
        # join button not found
        # refresh every minute until found
        k = 1
        while k <= 15:
            print("Join button not found, trying again")
            time.sleep(60)
            driver.refresh()
            join_class(class_name, start_time, end_time)
            # schedule.every(1).minutes.do(join_class,class_name,start_time,end_time)
            k += 1
        print("Seems like there is no class today.")
        discord_webhook.send_msg(class_name=class_name, status="noclass", start_time=start_time, end_time=end_time)

    time.sleep(4)
    webcam = driver.find_element_by_xpath(
        '//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div,'
        '/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
    if webcam.get_attribute('title') == 'Turn camera off':
        webcam.click()
    time.sleep(1)

    microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
    if microphone.get_attribute('title') == 'Mute microphone':
        microphone.click()

    time.sleep(1)
    join_now_button = driver.find_element_by_xpath(
        '//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2],'
        '/div[1]/div[2]/div/div/section/div[1]/div/div/button')
    join_now_button.click()

    discord_webhook.send_msg(class_name=class_name, status="joined", start_time=start_time, end_time=end_time)

    # now schedule leaving class
    tmp = "%H:%M"

    class_running_time = datetime.strptime(end_time, tmp) - datetime.strptime(start_time, tmp)

    time.sleep(class_running_time.seconds)

    driver.find_element_by_class_name("ts-calling-screen").click()

    driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click()  # come back to homepage
    time.sleep(1)

    driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
    print("Class left")
    discord_webhook.send_msg(class_name=class_name, status="left", start_time=start_time, end_time=end_time)


def start_browser():
    global driver
    driver = webdriver.Chrome(chrome_options=opt, service_log_path='NUL')

    driver.get(URL)

    WebDriverWait(driver, 10000).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))

    if "login.microsoftonline.com" in driver.current_url:
        login()


def scheduled():
    conn = sqlite3.connect('timetable.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM timetable'):
        # schedule all classes
        name = row[0]
        start_time = row[1]
        end_time = row[2]
        day = row[3]

        if day.lower() == "monday":
            schedule.every().monday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "tuesday":
            schedule.every().tuesday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "wednesday":
            schedule.every().wednesday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "thursday":
            schedule.every().thursday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "friday":
            schedule.every().friday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "saturday":
            schedule.every().saturday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))
        elif day.lower() == "sunday":
            schedule.every().sunday.at(start_time).do(join_class, name, start_time, end_time)
            print("Scheduled class '%s' on %s at %s" % (name, day, start_time))

    # Start browser
    start_browser()
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # join_class("Maths","15:13","15:15","sunday")
    op_main = 0
    while not op_main == 4:
        op_main = int(input("1. Modify Timetable\n2. View Timetable\n3. Start Bot\n4. Exit\nEnter option : "))

        if op_main == 1:
            add_timetable()
        elif op_main == 2:
            view_timetable()
        elif op_main == 3:
            scheduled()
    exit(0)
