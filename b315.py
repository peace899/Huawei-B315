#  My tool to interact with Huawei B315 router
# Author: Peace Lekalakala (peacester at gmail dot com)
# inspiration: https://gist.github.com/jonathanhoskin/0bc11f55d0ec926c0a457d4110b1f46f

import time
import requests
import xmltodict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# TODO: use WebDriverWait instead of time.sleep function

username = 'admin'
password = 'admin'
modem_ip = '192.168.8.1'


        
def get_browser():
    # Use headless Firefox
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(firefox_options=options)
    
    # Login
    home_url = 'http://{0}{1}'.format(modem_ip, '/html/home.html')
    browser.get(home_url)
    
    time.sleep(3)
    browser.execute_script("return showloginDialog()")
    time.sleep(3)
    login_input = browser.find_elements_by_css_selector('input#username')[0]
    login_input.send_keys(username)
    
    password_input = browser.find_elements_by_css_selector('input#password')[0]
    password_input.send_keys(password)
    
    browser.find_elements_by_css_selector('input#pop_login')[0].click()
    time.sleep(3)
    return browser
    
    
def reset_mobile_data(browser):
    # Switch mobile data on when off or reset connection
    
    status = browser.find_element_by_id('index_connection_status').text
    status = status.split('\n')[0]
    
    if  status == 'Connected':
        # switch off and then on
        browser.find_element_by_id('mobile_connect_btn').click()
        time.sleep(10)
        browser.find_element_by_id('mobile_connect_btn').click()
    else:
        # switch on
        browser.find_element_by_id('mobile_connect_btn').click()


def get_sms_list(browser):
    sms_url = 'http://{0}{1}'.format(modem_ip, '/html/smsinbox.html')
    browser.get(sms_url)
    time.sleep(4)
    
    sms_text = browser.page_source
    soup = BeautifulSoup(sms_text, 'lxml')
    sms_list = iter(soup.find('table').find_all('td'))
    
    messages = [i.text for i in sms_list]
    messages = [messages[x:x+6][-3:] for x in range(0, len(messages), 6)]
    
    all_sms = []
    for message in messages:
        sms = {}
        sms['From'] = message[0]
        sms['Content'] = message[1]
        sms['Date'] = message[2]
        all_sms.append(sms)
    
    return all_sms
    
    
def send_sms(browser, phone_number, message_text):
    sms_url = 'http://{0}{1}'.format(modem_ip, '/html/smsinbox.html')
    browser.get(sms_url)
    time.sleep(4)
    
    new_msg_button = browser.find_element_by_id('message')
    new_msg_button.click()
    time.sleep(3)
        
    reciepient = browser.find_element_by_id('recipients_number')
    reciepient.send_keys(phone_number)
    
    content = browser.find_element_by_id('message_content')
    content.send_keys(message_text)
    
    browser.find_element_by_id('pop_send').click()
    
    
def reboot_router(browser):
    reboot_url = 'http://{0}{1}'.format(modem_ip, '/html/reboot.html')
    browser.get(reboot_url)
    time.sleep(4)
    browser.find_element_by_id('undefined').click()
    print('Rebooting...')
        
    browser.find_element_by_id('pop_confirm').click()
    #6 second sleep, just to give the final Ajax calls time to complete
    time.sleep(6)

    
def get_api_token(browser):
    # For API calls a token is required
    # Get session ID and token after login
    
    browser_cookies = browser.get_cookies()
    
    s = requests.Session()
    cookie = browser_cookies[0]
    s.cookies.set(cookie['name'], cookie['value'])
    
    # open webserver with requests
    token_url = 'http://{0}{1}'.format(modem_ip, '/api/webserver/SesTokInfo')
    response = s.get(token_url)
    ses_tok = xmltodict.parse(response.text)
    sessionID, token = tuple(ses_tok['response'].values())
    return sessionID, token
        
    
browser = get_browser()
#send_sms(browser, '061*****', 'Message sent from Huawei B315 with selenium')
#reboot_router(browser)
smsList = get_sms_list(browser)
print(smsList)
browser.quit()
