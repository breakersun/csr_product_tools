import logging
import pathlib
import re
import shlex
import shutil
import subprocess

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

    def executor(self, cmd, match_str=None, return_match=False, return_raw=False):
        """
        excute commander command and return the result
        :param cmd:commands to be executed
        :type cmd:str
        :param match_str:regex string to match the result
        :type match_str:str
        :param return_match:true to return the match result; false to return the Yes/No result
        :type return_match:Boolean
        :param return_raw:true to return the raw result; false to return the match result
        :type return_raw:Boolean
        :return: return_raw == True: return the raw result or False
                 return_raw == False && return_match == return True for Success, False for Fail
                 return_raw == False && return_match == return the match result for success; False for Fail
        :rtype:
        """
        _cmd = [self.cmder] + cmd
        _logger.debug(f'[running] {_cmd}')
        try:
            output = subprocess.check_output(_cmd).decode('utf-8')
        except subprocess.CalledProcessError as e:
            if return_raw:
                return e.output.decode('utf-8')
            else:
                _logger.error(e.output.decode('utf-8'))
                _logger.error(f'[Failed] {_cmd}')
                return False
        _logger.debug(f'[response] {output}')
        if return_raw:
            return output
        if match_str:
            regex = re.compile(match_str)
            for line in output.splitlines():
                m = regex.match(line)
                if m:
                    _logger.debug(line)
                    if return_match:
                        return m.group(1)
                    else:
                        return True
            _logger.debug(f'No match found {match_str}')
            if return_match:
                return None
            else:
                return False
        return True


class E2cmdController(CSRControllerBase):
    def __init__(self):
        super().__init__('e2cmd.exe')
        self.check_path()

    def dump(self, file_name):
        cmd = shlex.split(f'dump {file_name}.img', posix=False)
        return self.executor(cmd)

    def read_words(self, address, size_in_words) -> str:
        cmd = shlex.split(f'readblock {address:x} {size_in_words}', posix=False)
        output = self.executor(cmd, return_raw=True)
        word_regx = re.compile(r'-\s(0x[0-9a-f]{4})')
        words = []
        for line in output.splitlines():
            m = word_regx.search(line)
            if m:
                words.append(m.group(1))

        # covert words to string seperated with space
        return ' '.join(words)


if __name__ == '__main__':
    FORMAT = "%(levelname)7s %(asctime)s [%(filename)13s:%(lineno)4d] %(message)s"
    DATEFMT = "%H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFMT)
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    tester = E2cmdController()
    print(tester.read_words(0x414a, 20))
