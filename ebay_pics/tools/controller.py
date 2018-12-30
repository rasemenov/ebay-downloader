import os
import threading
import time
import logging
from ebay_pics.tools.link_manager import PictureGetter
from ebay_pics.tools.utils import normalize_filename


logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, getter, link_manager, root, file_storage, items_list):
        logger.debug('Creating Controller instance')
        self._getter = getter
        self._manager = link_manager
        self._root = root
        self._file_storage = file_storage
        self._items_list = items_list
        self._active = False
        self._thread = None
        self._stop = False
        self._condition = threading.Condition()

    def add_lots(self):
        logger.info('Adding new lots to list')
        for file in self._file_storage.files:
            if file not in self._items_list.items.keys():
                self._items_list.add_list(os.path.basename(file), path=file)
                logger.info('Add {} to ItemsList'.format(file))

    def remove_lots(self):
        logger.info('Removing lots')
        key_set = list(self._items_list.items.keys())[:]
        for key in key_set:
            if self._items_list.items[key].done or not self._items_list.items[key].started:
                if self._file_storage.page_link.get() == key:
                    self._file_storage.page_link.set('')
                self._items_list.remove_list(key)
                logger.info('Calling remove_list() with {}'.format(key))

    def download(self):
        logger.info('Enter Controller.download()')
        if self._active:
            logger.debug('Oops, it\'s already active. Returning')
            return
        self._active = True
        while True:
            time.sleep(0.1)
            page = None
            for item in self._items_list.items.values():
                if not item.done:
                    logger.info('Found fresh lot to download {}'.format(item.path))
                    page = item
                    break
            if page is None:
                logger.debug('No pages in the queue. Returning')
                self._active = False
                return
            item_num = int(self._file_storage.item_num.get())
            logger.info('User demanded {} to download'.format(item_num))
            folder_name = normalize_filename(os.path.splitext(
                os.path.basename(page.path))[0])
            dir_save = os.path.join(os.path.dirname(page.path), folder_name)
            logger.info('All images will be saved into {}'.format(dir_save))
            manager = self._manager(page.path, self._getter)
            page.set_active(manager.get_number_of_links())
            try:
                for num, (link, bonus) in enumerate(manager):
                    with self._condition:
                        if self._stop:
                            logger.info('Get stop signal inside inner loop')
                            self._condition.notify()
                            return
                    if (num + 1) > item_num:
                        logger.debug('Demanded {} lots - only have '
                                     '{} lots'.format(item_num, num + 1))
                        break
                    try:
                        pic_getter = PictureGetter(num, self._getter, link,
                                                   bonus, dir_save)
                        pic_getter.download_pics()
                        pic_getter.download_bonus()
                    except Exception as err:
                        logger.exception(err)
                    finally:
                        page.add_one_done()

            except Exception as err:
                logger.exception(err)
            page.set_done()

    def run(self):
        logger.info('Get call to Controller.run')
        self._thread = threading.Thread(target=self.download)
        self._thread.start()
        logger.debug('Exiting run() with #threads {}'.format(threading.active_count()))

    def kill_all(self):
        logger.info('Trying to close app')
        with self._condition:
            logger.debug('Changing _stop to True')
            self._stop = True
        if self._thread:
            logger.debug('Joining threads')
            self._thread.join()
        logger.debug('Destroying root')
        self._root.destroy()
        logger.info('Bye-bye')
