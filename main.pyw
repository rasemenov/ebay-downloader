import logging
from multiprocessing import cpu_count
import tkinter as tk
import ebay_pics.gui.forms as forms
import ebay_pics.settings as env
import ebay_pics.tools.downloader as downloader
import ebay_pics.tools.link_manager as manager
import ebay_pics.tools.controller as controller


logger = logging.getLogger(__name__)


def configure_logging():
    fm_str = '%(asctime)-15s - %(levelname)-8s - %(filename)-15s - ' \
             '%(lineno)-3s - %(message)s'
    logging.basicConfig(level=getattr(logging, env.LOGGING_LEVEL),
                        filename='execution_details.log', filemode='w', format=fm_str)


def main():
    root = tk.Tk()
    root.geometry("800x800+650+150")
    root.resizable(False, False)
    frame = forms.ButtonFrame(root).start()
    canvas = forms.ItemsList(root).start()
    clear_btn = forms.ClearButton(root).start()
    getter = downloader.Downloader()
    proxy = controller.Controller(getter, manager.LinkManager, root, frame, canvas)
    frame.assign_file_callback(proxy.add_lots)
    frame.assign_start_callback(proxy.run)
    clear_btn.assign_callback(proxy.remove_lots)
    root.protocol("WM_DELETE_WINDOW", proxy.kill_all)
    logger.debug('Starting tk mainloop')
    root.mainloop()


if __name__ == '__main__':
    if env.LOGGING_STATUS == 'ON':
        configure_logging()
    logger.info('Starting on machine with number of CPU: {}'.format(cpu_count()))
    logger.info('Start main function')
    main()
