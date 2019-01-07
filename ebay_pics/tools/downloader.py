try:
    import requests
except ImportError:
    from ebay_pics.tools.utils import install_reqeusts
    install_reqeusts()
    import requests
import logging
import multiprocessing as mp
from ebay_pics.tools.utils import time_execution


logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self):
        self._pool = mp.Pool(processes=mp.cpu_count() - 1)

    @time_execution
    def download(self, links, headers=None, params=None):
        args = self._prepare_args(links, headers, params)
        response = self._pool.map(self._run_download, args)
        return response

    @staticmethod
    def _run_download(args):
        logger.info('Process {} started with {}'.format(mp.current_process().name, args))
        link, headers, params = args
        try:
            return requests.get(link, headers=headers, params=params, timeout=20).content
        except requests.RequestException as err:
            logger.error('Problem with {}'.format(link))
            logger.exception(err)

    @staticmethod
    def _prepare_args(links, headers, params):
        args = []
        if isinstance(links, list):
            for item in links:
                args.append((item, headers, params))
        else:
            args.append((links, headers, params))
        return args

    def __del__(self):
        self._pool.close()
        self._pool.join()
