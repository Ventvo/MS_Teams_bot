import time
import re
import os.path
from os import path
import sqlite3
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import schedule
import browser_handler
import db_handler
import credetials


def scheduled():
    join_class = browser_handler.join_class
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
    browser_handler.start_browser()
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # join_class("Maths","15:13","15:15","sunday")
    op_main = 0
    while not op_main == 5:
        op_main = int(input("1. Modify Timetable\n2. View Timetable\n3. Start Bot\n4. Exit\nEnter option : "))

        if op_main == 1:
            db_handler.add_timetable()
        elif op_main == 2:
            db_handler.view_timetable()
        elif op_main == 3:
            scheduled()
    exit(0)
