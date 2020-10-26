import json
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

client = MongoClient('127.0.0.1', 27017)
db = client['mailru_letters']
collection = db['letters']

with open("mailru.json", "r") as infile:
    json_content = json.load(infile)
    infile.close()

login_value = json_content['login']
password_value = json_content['password']

chrome_options = Options()
chrome_options.add_argument('start-maximized')
driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

driver.get('https://mail.ru/')

# Ввод логина
login_elem = driver.find_element_by_id('mailbox:login-input')
login_elem.send_keys(login_value)
login_elem.send_keys(Keys.ENTER)

# Ввод пароля
password_elem = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'mailbox:password-input'))
        )
password_elem.send_keys(password_value)
password_elem.send_keys(Keys.ENTER)

list_of_links = []
# Пролистаем все письма и соберем все ссылки.
# (Число 20 подорано эмпирическим путем, но здесь можно попробовать сделать лучше,
# например, вычислить минимальное число итераций,
# исходя из общее количества писем (можно узнать, нажав на "Выделить все"))
for i in range(20):
    read_status_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'llc__read-status')))
    actions = ActionChains(driver)
    letters = driver.find_elements_by_class_name('js-letter-list-item')
    for itm in letters:
        link = itm.get_attribute('href')
        list_of_links.append(link)

    actions.move_to_element(letters[-1])
    actions.perform()

# Прочитаем каждое письмо по ссылке
list_tmp = []
for itm in set(list_of_links):
    driver.get(itm)
    send_info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'letter__author')))
    sender = send_info.find_element_by_class_name('letter-contact').text
    when_sended = send_info.find_element_by_class_name('letter__date').text
    header = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h2'))).text
    body = driver.find_element_by_class_name('letter-body').text
    list_tmp.append({'Sender': sender, 'When sended': when_sended, 'Header': header, 'Body': body})

collection.delete_many({})
collection.insert_many(list_tmp)

driver.close()
client.close()


