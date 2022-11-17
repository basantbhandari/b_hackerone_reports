"""
This script runs first.

It will scroll through hacktivity until the appearance of URL of the first report in data.csv.
Then script searches for all new reports' URLs and add them to data.csv.

To use it without modifications you should put non-empty data.csv file
in the same directory with this script (current data.csv is good), because
scrolling through the whole hacktivity is almost impossible for now.
"""

import time
import csv
import logging
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By


def get_program_name():
    return input("Enter program name: ")


def default(data_chunk, i):
    try:
        return data_chunk[i]
    except Exception as e:
        return None


def extract_reports(raw_reports):
    reports = []
    for raw_report in raw_reports:
        data = raw_report.text
        data_chunks = data.split('\n')
        reports.append({
            "upvote": default(data_chunks, 0),
            "title": default(data_chunks, 1),
            "disclosed date from current date": default(data_chunks, 2),
            "reported from to": default(data_chunks, 3),
            "status": default(data_chunks, 4),
            "severity": default(data_chunks, 5),
            "bounty": default(data_chunks, 6)
        })
    return reports


def fetch():
    page_loading_timeout = 10
    data_keys = ["upvote", "title", "disclosed date from current date", "reported from to", "status", "severity", "bounty"]
    data_keys.sort()
    counter = 0
    page = 0
    program_name = get_program_name()
    hacker_one_url = f'https://hackerone.com/hacktivity?querystring={program_name}&filter=type:public&order_direction=' \
                     f'DESC&order_field=latest_disclosable_activity_at&followed_only=false&collaboration_only=false'
    driver = Chrome(options=ChromeOptions())

    try:
        driver.get(hacker_one_url)
    except Exception as e:
        logging.error(e, exc_info=True)

    driver.implicitly_wait(page_loading_timeout)
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(page_loading_timeout)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            counter += 1
            if counter > 1:
                reports = extract_reports(driver.find_elements(By.CLASS_NAME, "fade"))
                break
        else:
            counter = 0
        last_height = new_height
        page += 1
        print('Page:', page)

    driver.close()

    with open(f'{program_name}_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data_keys)
        writer.writeheader()
        writer.writerows(reports)


if __name__ == '__main__':
    fetch()
