import re
import unicodedata
import logging
import time
from functools import wraps
try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain


logger = logging.getLogger(__name__)


def dedupl(array):
    unique = set()
    result = []
    for item in array:
        if item not in unique:
            unique.add(item)
            result.append(item)
    return result


def install_reqeusts():
    pipmain(['install', 'requests'])


def normalize_filename(fname):
    fname = unicodedata.normalize('NFKD', fname).encode('ascii', 'ignore').decode('ascii')
    fname = re.sub('[^\w\s-]', '', fname).strip().lower()
    return re.sub('[-\s]+', '-', fname)


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
