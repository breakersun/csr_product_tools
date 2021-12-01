import logging
import pathlib
import shutil

_logger = logging.getLogger(__name__)


class CSRControllerBase:
    def __init__(self, cmder: str = None):
        self.cmder = cmder

    def __iter__(self):
        return self.cmder.__iter__()

    def check_path(self):
        _cmder = shutil.which(self.cmder)
        if _cmder:
            _logger.info(f'{self.cmder} is found in PATH')
            self.cmder = _cmder
            return

        _cmder = pathlib.Path.cwd() / 'tools' / self.cmder
        if _cmder.is_file():
            _logger.info(f'{self.cmder} is found')
            self.cmder = _cmder
            return

        _logger.warning(f'{self.cmder} is not found')
        raise FileNotFoundError(f'{self.cmder} is not found')


if __name__ == '__main__':
    FORMAT = "%(levelname)7s %(asctime)s [%(filename)13s:%(lineno)4d] %(message)s"
    DATEFMT = "%H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFMT)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    tester = CSRControllerBase('e2cmd.exe')
    tester.check_path()
    print(tester)
