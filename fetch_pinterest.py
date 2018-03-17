import time
import logging
import os
import traceback
from urllib.request import urlretrieve

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import tqdm
import requests
from bs4 import BeautifulSoup

class TqdmLoggingHandler(logging.Handler):

    def __init__ (self, level = logging.NOTSET):
        super (self.__class__, self).__init__ (level)

    def emit (self, record):
        try:
            msg = self.format (record)
            tqdm.tqdm.write (msg)
            self.flush()
        except:
            self.handleError(record)

logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[logging.FileHandler('./logfile.log'), TqdmLoggingHandler()])

for name in ["requests", "urllib3", "selenium"]:
    logging.getLogger(name).setLevel(logging.WARNING)

def get_search_result(config):
    try:
        options = Options()
        no_of_pins = config.no_of_pins

        if config.headless_mode:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(chrome_options=options)
        driver.get('https://pinterest.com/')
        time.sleep(3)
        logging.info('url opened')

        #search for log in button
        elem = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div[2]/div[2]/button')
        elem.click()
        time.sleep(3)

        elem = driver.find_element_by_id("email")
        elem.send_keys(config.usr)
        time.sleep(1)
        elem = driver.find_element_by_id("password")
        elem.send_keys(config.pwd)
        time.sleep(1)
        elem.send_keys(Keys.RETURN)
        logging.info('logged in')

        time.sleep(5)
        #search for search input
        elem = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/input')
        elem.send_keys(config.query)
        time.sleep(3)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)
        logging.info('search query sent')

        elem = driver.find_element_by_tag_name("body")
        pins_list = set()

        logging.info('getting pins...')
        while no_of_pins > 0:
            post_elems = driver.find_elements_by_class_name('pinWrapper')
            prev_pins_len = len(pins_list)
            for pin in post_elems:
                try:
                    pin_link = pin.find_element_by_tag_name('a').get_attribute('href')
                except:
                    pass
                pins_list.update([pin_link])
            diff = len(pins_list) - prev_pins_len
            if diff:
                no_of_pins -= diff
                for i in range(config.step):
                    elem.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.25)
            else:
                break
        pins_list = list(pins_list)
        driver.close()

        logging.info('getting pins finished!')

        if not os.path.isdir('./data'):
            os.makedirs('./data')

        with open('./data/pins_list.txt', 'w') as f:
            for pin in pins_list:
                f.write(pin+'\n')

        logging.info('pins list saved!')

    except Exception as e:
        try:
            driver.close()
        except:
            pass
        logging.error(traceback.format_exc())

class PinterestAPI:
    def __init__(self, path=None, access_token=None, timeout=30):
        self.path = path
        self.access_token = access_token
        self.timeout = timeout

        if not os.path.isdir(self.path):
            os.makedirs(self.path)
            
    def save_image(self, url, i):
        if url:
            extension = url.split('.')[-1]
            saved_image_path = urlretrieve(url, "{}/{}.{}".format(self.path, str(i), extension))

    def get_image_url_from_pin_url(self, url):
        r = requests.get(url, timeout=self.timeout)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            images = [x['src'] for x in soup.findAll('img')]
            if len(images) > 0:
                return images[0]
            return False
    
    def get_pins_from_board(self, board_id):
        logging.info('boards crawling started...')
        try:
            response = requests.get('https://api.pinterest.com/v1/boards/'+board_id+'/pins/', timeout=self.timeout,
                                    params={'access_token':self.access_token, 'page_size':10e6})
            imageDatas = response.json()['data']
            for i, imageData in enumerate(tqdm.tqdm(imageDatas)):
                image_url = self.get_image_url_from_pin_url(imageData["url"])
                self.save_image(image_url, i)
            logging.info('pins saved successfully!')
            
        except Exception as e:
            logging.error(traceback.format_exc())
                
    def get_pins(self, pins_list):
        logging.info('pins downloading started...')
        try:
            if type(pins_list) != list:
                pins_list = list(pins_list)

            for i, pin in enumerate(tqdm.tqdm(pins_list)):
                try:
                    response = requests.get('https://api.pinterest.com/v1/pins/'+pin.split('/')[-2], timeout=self.timeout,
                                            params={'access_token':self.access_token})
                except:
                    pass
                imageData = response.json()['data']['url']
                image_url = self.get_image_url_from_pin_url(imageData)
                self.save_image(image_url, i)
            logging.info('pins saved successfully!')

        except Exception as e:
            logging.error(traceback.format_exc())