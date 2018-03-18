import time
import logging
import os
import re
import traceback
from urllib.request import urlretrieve
from urllib.parse import quote, urlencode

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

class PinterestAPI:
    def __init__(self, path=None, access_token=None, timeout=30):
        self.base_path = path
        self.access_token = access_token
        self.timeout = timeout
        self.api = 'https://api.pinterest.com/v1/'

        if not os.path.isdir(self.base_path):
            os.makedirs(self.base_path)
            
    def api_call(self, url):
        response = requests.get(url, timeout=self.timeout)
        return response.json()
            
    def save_image(self, url, i):
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
        self.path = self.base_path+'/'+'_'.join(re.split('\W+', board_id))
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
            
        logging.info('boards crawling started...')
        images_data, n_pins = [], 0
        query = {
            'access_token': self.access_token,
            'limit': 100,
            }
        url = '{}boards/{}/pins/?{}'.format(self.api, quote(board_id), urlencode(query))
        try:
            while True:
                board = self.api_call(url)
                images_data.extend(board['data'])
                url = board['page']['next']
                if url is None:
                    break
                
            for i, image_data in enumerate(tqdm.tqdm(images_data)):
                try:
                    image_url = self.get_image_url_from_pin_url(image_data["url"])
                    if image_url:
                        self.save_image(image_url, i)
                        n_pins += 1
                except:
                    pass

            logging.info('%i pins from `%s` saved successfully!' % (n_pins, board_id))
            
        except Exception as e:
            logging.error(traceback.format_exc())