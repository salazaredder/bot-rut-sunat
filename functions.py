import os
import zipfile
import time
import datetime
import random
import string
import sys
import json
import logging
import re
import smtplib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIME_WAIT = 30
FREQUENCY = 5


def proxy_to_dict(proxy):
    p1 = re.compile('(?P<url>[\w_\-\.]*):(?P<port>\d{1,5}):(?P<user>\S*):(?P<password>\S*)')
    p2 = re.compile('(?P<user>\S*):(?P<password>\S*):(?P<url>[\w_\-\.]*):(?P<port>\d{1,5})')
    x1 = p1.match(proxy)
    x2 = p2.match(proxy)
    if x1:
        return x1.groupdict()
    elif x2:
        return x2.groupdict()
    else:
        return False


def get_firefox_options(proxy):
    options = {}
    if proxy:
        options['proxy'] = {
            'http': f'http://{proxy["user"]}:{proxy["password"]}@{proxy["url"]}:{proxy["port"]}',
            'https': f'https://{proxy["user"]}:{proxy["password"]}@{proxy["url"]}:{proxy["port"]}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    return options


def get_firefox_driver(proxy):
    options = get_firefox_options(proxy)
    return wire_webdriver.Firefox(executable_path=GeckoDriverManager().install(), seleniumwire_options=options)


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


def get_background_js(proxy):
    return """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt("%s")
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (proxy['url'], proxy['port'], proxy['user'], proxy['password'])


def get_chrome_driver(proxy=False, user_agent=None, bot_name='bot_develop'):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    if proxy:
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        plugin_file = f'tmp/proxy_auth_plugin_{bot_name}.zip'
        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", get_background_js(proxy))
        chrome_options.add_extension(plugin_file)
    driver = webdriver.Chrome(executable_path='chromedriver/chromedriver', options=chrome_options)
    return driver


def get_element_by_xpath(driver, xpath):
    return WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def get_elements_by_xpath(driver, xpath):
    return WebDriverWait(driver, TIME_WAIT).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath))
    )


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def read_file_config(file, bot_name='bot_develop'):
    try:
        logging.info(f'Bot {bot_name} {datetime.datetime.now()}:: Reading conf file {file}')
        with open(file) as json_file:
            data = json.load(json_file)
    except:
        logging.error(f'Bot {bot_name} {datetime.datetime.now()}:: Error reading conf file {file}')
        exit()
    return data


def print_log(created_at, bot_name='bot_develop'):
    total = datetime.datetime.now() - created_at
    logging.info('----------------------------------------------')
    logging.info(f'Bot {bot_name} {datetime.datetime.now()}:: Bot life time is {seconds_to_str(total.seconds)}')


def str_to_time(value):
    occurrences = value.count(':')
    if occurrences == 0:
        x = time.strptime(value, '%S')
    elif occurrences == 1:
        x = time.strptime(value, '%M:%S')
    elif occurrences == 2:
        x = time.strptime(value, '%H:%M:%S')
    duration_track = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
    return duration_track


def seconds_to_str(value):
    h = int(value / 3600)
    m = int((value % 3600) / 60)
    s = int((value % 3600) % 60 % 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def send_email(receiver, subject, msg, bot_name='bot_develop'):
    """
    :param receiver: email receiver
    :param subject: email subject
    :param msg: email message
    :param bot_name: bot name
    :return:
    """
    if not os.environ.get('BS_SMTP_SERVER') or not os.environ.get('BS_SMTP_PORT') or \
            not os.environ.get('BS_SMTP_USER') or not os.environ.get('BS_SMTP_PASS') or \
            not os.environ.get('BS_EMAIL_DEFAULT'):
        logging.error(
            f'Bot {bot_name} {datetime.datetime.now()} :: You can\'t send emails. Please set the environment variables first')
        return
    message = f"""From: SpotyBot <{os.environ.get('BS_EMAIL_DEFAULT')}>
To: {receiver}
Subject: {subject}

{msg}."""
    try:
        server = smtplib.SMTP(os.environ.get('BS_SMTP_SERVER'), int(os.environ.get('BS_SMTP_PORT')))
        server.login(os.environ.get('BS_SMTP_USER'), os.environ.get('BS_SMTP_PASS'))
        server.sendmail(os.environ.get('BS_EMAIL_DEFAULT'), receiver, message)
        logging.info(f'Bot {bot_name} {datetime.datetime.now()} :: Your email has been sended')
    except:
        logging.error(f'Bot {bot_name} {datetime.datetime.now()} :: Error sending email')


class Error(Exception):
    """Base class for other exceptions"""
    pass


class CloseNavigator(Error):
    """Raised when the input value is too small"""
    pass
