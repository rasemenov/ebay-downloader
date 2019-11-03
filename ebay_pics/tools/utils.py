import os
import re
import time
import logging
import unicodedata
from functools import wraps
from urllib.parse import urlsplit, urlunsplit
try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain
import ebay_pics.settings as env


logger = logging.getLogger(__name__)


def dedupl(array):
    unique = set()
    result = []
    for item in array:
        if item not in unique:
            unique.add(item)
            result.append(item)
    return result


def get_main_link(raw_link):
    link_parts = urlsplit(raw_link)
    return link_parts.scheme, link_parts.netloc, link_parts.path


def join_link(*args):
    if len(args) < 5:
        args = list(args)
        args.extend(['' for _ in range(5 - len(args))])
    return urlunsplit(args)


def install_reqeusts():
    pipmain(['install', 'requests'])


def normalize_filename(fname):
    fname = unicodedata.normalize('NFKD', fname).encode('ascii', 'ignore').decode('ascii')
    fname = re.sub('[^\w\s-]', '', fname).strip().lower()
    return re.sub('[-\s]+', '-', fname)


def get_current_dir():
    try:
        cur_dir = env.BASE_DIR
        logger.info('Assigned {} to active directory'.format(cur_dir))
    except AttributeError:
        cur_dir = os.path.dirname(__file__)
        logger.info('Set active directory to program directory')
    return cur_dir


def get_images_dir(page_path):
    folder_name = normalize_filename(os.path.splitext(os.path.basename(page_path))[0])
    if os.path.isfile(page_path):
        base_path = os.path.dirname(page_path)
    else:
        base_path = get_current_dir()
    return os.path.join(base_path, folder_name)


def time_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug('Calling {} with args {} and kwargs {}'.format(func.__name__, args,
                                                                    kwargs))
        start_time = time.time()
        result = func(*args, **kwargs)
        logger.info('It took function {} {:.1f}s '
                    'to execute'.format(func.__name__, time.time() - start_time))
        return result
    return wrapper
