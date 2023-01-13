import enum
import traceback
import os
import time
from threading import RLock
import logging
from transitions.extensions import LockedMachine
from utils.singleton import Singleton

logger = logging.getLogger(__name__)


class BoxManagerError(Exception):
    pass


class BoxManager(object, metaclass=Singleton):
    """ Singleton, manage box manager life cycle
    """
    class States(enum.Enum):
        """ State of SFM
        1. ERROR: all error status.
        2. STOPPED: no project running, waiting for call.
        4. RUNNING: project task running.
        """
        ERROR = -1
        STOPPED = 0
        RUNNING = 1
        STARING = 2
        CUSTOMER_OPEN = 3
        DELIVERER_OPEN = 4
        READER = 5

    transitions = [['start', States.STOPPED, States.STARING],
                   ['stop', [States.RUNNING, States.ERROR], States.STOPPED],
                   ['reset', States.ERROR, States.STOPPED],
                   ['start_success', States.STARING, States.RUNNING],
                   ['error', '*', States.ERROR]]

    def __init__(self):
        self._lock = RLock()
        self._machine = LockedMachine(
            states=self.States, transitions=self.transitions, initial=self.States.STOPPED)

    def reset(self):
        if not self._machine.is_ERROR():
            raise BoxManagerError(
                "cannot reset box manager when status {} != ERROR".format(self._machine.state))
        with self._lock:
            try:
                pass
            finally:
                self._machine.reset()

    def start(self,
              timeout: int = 60) -> bool:
        """ Try to start box manager with given parameters; will block the thread until return.
        """
        with self._lock:
            try:
                if not self._machine.is_STOPPED():
                    return True, 'Project is running! Stop the running project first!'
                self._machine.start()
                # TODO start the reader and other tasks
            except Exception as e:
                logger.error("Start error: {}".format(e.__str__()))
                logger.error(traceback.format_exc())
                self._machine.error()
                raise e
            # wait for success (timeout)
            cur_t = 0
            while cur_t < timeout:
                # TODO only to break if start succeeded
                if True:
                    break
                time.sleep(1)
                cur_t += 1
            if cur_t >= timeout:
                self._machine.error()
                raise BoxManagerError("Starting timeout")
            self._machine.start_success()
            return True
