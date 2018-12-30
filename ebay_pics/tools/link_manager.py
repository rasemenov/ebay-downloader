import os
import re
import sys
import logging
import unicodedata
import ebay_pics.settings as env
from ebay_pics.tools.utils import dedupl


logger = logging.getLogger(__name__)


class LinkManager:
    def __init__(self, main_page, downloader):
        logger.debug('Creating LinkManager with {}'.format(main_page))
        self._main_page = main_page
        self._getter = downloader
        self._links = []
        self._item_link = re.compile('href="(http[s]://www.ebay\\.\S+/itm/\S*)"')
        self._page_id = re.compile('http.*://www.ebay.*/itm.*/(.*)\?')
        self._bonus_page = 'https://vi.vipr.ebaydesc.com/ws/eBayISAPI.dll?' \
                           'ViewItemDescV4&item='
        self._headers = {'Accept-Language': 'en_EN', 'Content-Language': 'en_EN',
                         'Cache-Control': 'no-cache'}

    def _get_main(self):
        if os.path.isfile(self._main_page):
            logger.info('Reading local main page')
            with open(self._main_page, encoding='utf-8') as file:
                self._main_page = file.read()
        else:
            logger.info('Downloading remote main page')
            self._main_page = self._getter.download(self._main_page,
                                                    headers=self._headers)[0]
            self._main_page = str(self._main_page, encoding='utf-8')

    def _find_links(self):
        logger.debug('Start looking for links in main page')
        raw_links = self._item_link.findall(self._main_page)
        prep_links = []
        for copies in raw_links:
            logger.debug('Processing raw link {}'.format(copies))
            if copies.find('thumbs') == -1:
                for phrase in ('?hash', '&hash'):
                    if copies.find(phrase) != -1:
                        copies = copies[:copies.find(phrase)]
                        copies += '{}_ul=EN'.format(phrase[0])
                        logger.debug('Insert ul=EN into raw link {}'.format(copies))
                if copies not in prep_links:
                    prep_links.append(copies)
                    logger.debug('Append {} to resulted list'.format(copies))
        self._links.extend(prep_links)

    def _find_id(self, link):
        logger.debug('Searching for lot ID')
        return self._page_id.findall(link)[0]

    def _get_bonus_link(self, link):
        logger.debug('Creating bonus page link')
        return ''.join((self._bonus_page, self._find_id(link)))

    def get_number_of_links(self):
        self._get_main()
        self._find_links()
        return len(self._links)

    def __iter__(self):
        return zip(self._links, (self._get_bonus_link(link) for link in self._links))


class PictureGetter:
    def __init__(self, prefix, downloader, link, bonus, dir_save):
        self._prefix = prefix
        self._getter = downloader
        self._link = link
        self._bonus = bonus
        self._dir_save = dir_save
        self._pics = None
        self._page = None
        self._bonus_page = None
        self._title = None
        self._pic_link = re.compile('src="(http[s]://i.ebayimg\\.[a-z]{2,3}/images/\S*)"')
        self._bonus_pic = re.compile('src="(.*?\.jpg)"')
        self._title_template = '<span id="vi-lkhdr-itmTitl" class="u-dspn">(.*)</span>'
        self._headers = {'Accept-Language': 'en_EN', 'Content-Language': 'en_EN',
                         'Cache-Control': 'no-cache'}
        self._char_map = {char: '_' for char in [':', '?', '&', '/', '\\', '<', '>',
                                                 '|', '*']}
        logger.debug('Created PictureGetter with link {} & bonus {}'.format(link, bonus))

    def _download_page(self):
        self._page = self._getter.download(self._link)[0]
        self._page = str(self._page, encoding='utf-8')
        self._bonus_page = self._getter.download(self._bonus)[0]
        self._bonus_page = str(self._bonus_page, encoding='utf-8')
        logger.info('Downloaded main and bonus pages')

    def _find_pics(self, bonus=False):
        if not bonus:
            self._pics = self._pic_link.findall(self._page)
            logger.debug('{}'.format(self._pics))
            logger.debug('{}'.format(self._link))
            logger.info('Found images in main lot page')
        else:
            self._pics = self._bonus_pic.findall(self._bonus_page)
            logger.info('Found images in bonus lot page')
        self._pics = dedupl([re.sub('(-l.*).jpg', '-l1600.jpg', pic)
                             for pic in self._pics])
        logger.info('List of pictures to download {}'.format(self._pics))

    def download_pics(self):
        try:
            logger.info('Trying to download main and bonus lot pages')
            self._download_page()
        except TypeError as err:
            logger.error('Lot pages download failed')
            logger.exception(err)
            return
        self._find_pics()
        self._get_title()
        self._write_data(self._getter.download(self._pics), self._title)

    def download_bonus(self):
        logger.debug('Trying to download bonus page')
        if self._title is None:
            logger.debug('No bonus page was provided')
            return
        self._find_pics(True)
        if len(self._pics) > 0:
            logger.info('Found images on bonus page')
            self._write_data(self._getter.download(self._pics), self._title, True)

    def _get_title(self):
        tmp_title = re.findall(self._title_template, self._page)[0]
        tmp_title = tmp_title.translate(str.maketrans(self._char_map))
        tmp_title = unicodedata.normalize('NFD', tmp_title)
        self._title = tmp_title.encode('ascii', 'ignore').decode('ascii')
        logger.debug('Found title for items lot {}'.format(self._title))

    def _write_data(self, files, name, bonus=False):
        logger.debug('Writing images to disk {}'.format(self._dir_save))
        bonus_str = '_bonus' if bonus else ''
        for picno, file in enumerate(files):
            if sys.getsizeof(file) > env.SKIP_SIZE:
                if not os.path.exists(self._dir_save):
                    logger.info('Creating directory {}'.format(self._dir_save))
                    os.mkdir(self._dir_save)
                pic_file = os.path.join(self._dir_save, '{}_{}{}_{}.jpg')
                pic_file = pic_file.format(self._prefix, name, bonus_str, picno)
                with open(pic_file, 'wb') as pic:
                    pic.write(file)
                logger.info('Finished writing {} to disk'.format(name))
