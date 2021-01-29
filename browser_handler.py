from selenium import webdriver
import sqlite3
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import datetime

import bot
import discord_webhook

driver = webdriver.Chrome(service_log_path='NUL')
URL = "https://teams.microsoft.com"

# put your teams credentials here
credentials = {'email': 'email here', 'passwd': 'passwd here'}


def start_browser():
    driver.get(URL)

    WebDriverWait(driver, 10000).until(ec.visibility_of_element_located((By.TAG_NAME, 'body')))

    if "login.microsoftonline.com" in driver.current_url:
        login()


def login():
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
