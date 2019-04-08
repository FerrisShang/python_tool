from daemon import Daemon
from time import sleep
import logging


class Pantalaimon(Daemon):
    def __init__(self, pidfile):
        Daemon.__init__(self, pidfile)

    def run(self):
        idx = 0
        while True:
            logging.debug("This is a debug log: {}".format(idx))
            sleep(1)
            idx += 1


if __name__ == '__main__':
    logging.basicConfig(filename='test.log', level=logging.DEBUG, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    pineMarten = Pantalaimon('test.pid')
    pineMarten.start()