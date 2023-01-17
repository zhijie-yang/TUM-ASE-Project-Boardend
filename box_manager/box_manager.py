import enum
import traceback
import os
import time
from threading import RLock
import logging
from transitions.extensions import LockedMachine
from led_manager import LedManager
from photo_resistor import PhotoResistor
from rfid_manager.reader import RfidReader
from utils.singleton import Singleton


logger = logging.getLogger(__name__)

BOX_STATUS_REFRESH_RATE = 10
BOX_STATUS_REFRESH_INTERVAL = 1.0 / BOX_STATUS_REFRESH_RATE


class BoxManagerError(Exception):  # pylint: disable=missing-class-docstring
    pass


class BoxManager(object, metaclass=Singleton):
    """ Singleton, manage box manager life cycle
    """
    class States(enum.Enum):
        """ State of SFM
        """
        ERROR = -1
        STOPPED = 0
        STANDBY = 1
        STARING = 2
        CUSTOMER_OPEN = 3
        DELIVERER_OPEN = 4
        READER = 5

    transitions = [
        ['start', States.STOPPED, States.STARING],
        ['stop', [States.STANDBY, States.ERROR], States.STOPPED],
        ['reset', States.ERROR, States.STOPPED],
        ['start_success', States.STARING, States.STANDBY],
        ['error', '*', States.ERROR],
        ['open_by_customer', States.STANDBY, States.CUSTOMER_OPEN],
        ['open_by_deliverer', States.STANDBY, States.DELIVERER_OPEN],
        ['closed', [States.CUSTOMER_OPEN, States.DELIVERER_OPEN], States.STANDBY],
    ]

    def __init__(self):
        self._lock = RLock()
        self._machine = LockedMachine(
            states=self.States, transitions=self.transitions, initial=self.States.STOPPED)

        self._reader = RfidReader()
        self._led = LedManager()
        self._sensor = PhotoResistor()

    def reset(self):
        if not self._machine.is_ERROR():
            raise BoxManagerError(
                "cannot reset box manager when status {} != ERROR".format(self._machine.state))  # pylint: disable=consider-using-f-string
        with self._lock:
            try:
                pass
            finally:
                self._machine.reset()

    def start(self, timeout: int = 60) -> bool:
        """ Try to start box manager with given parameters; will block the thread until return.
        """
        with self._lock:
            try:
                if not self._machine.is_STOPPED():
                    return True, 'Project is running! Stop the running project first!'
                self._machine.start()
                # TODO start the reader and other tasks
            except Exception as e:  # pylint: disable=invalid-name
                logger.error("Start error: {}".format(e)  # pylint: disable=logging-format-interpolation, consider-using-f-string
                             )
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

    @staticmethod
    def _check_closed_timeout(start_time: float, timeout: float = 10.0) -> bool:
        """ Checks if the box is closed within time. 

        Args:
            timeout (float, optional): Timeout. Defaults to 10.0.

        Returns:
            bool: result
        """
        return time.time() >= (start_time + timeout)

    def _warn_timeout(self):
        """ Light the red led and set state machine to timeout statue.
        """
        with self._lock:
            self._machine.open_timeout()
        self._led.turn_on_red()

    def _block_until_closed(self, timeout: float = 10.0):
        """ Blocked checking if the box is closed within time. Makes red light flash
            if not. Unblocks until the box is properly closed. Should be called with
            green LED on.

        Args:
            timeout (float, optional): _description_. Defaults to 10.0.
        """
        if not self._led.get_status_green():
            self._box_error()

        start_time: float = time.time()
        opened_before: bool = False
        # If the box is never opened
        while self._sensor.is_closed():
            if self._check_closed_timeout(start_time, timeout):
                with self._lock:
                    self._machine.closed()
                self._led.turn_off_green()
                return
            if self._sensor.is_opened():
                opened_before = True
                break
            time.sleep(BOX_STATUS_REFRESH_INTERVAL)
        self._led.turn_off_green()
        # The open permission is expired, i.e.
        # the box is either opened or the timeout is reached.
        while not self._sensor.is_closed():
            if self._check_closed_timeout(start_time, timeout):
                self._led.turn_on_red()
            time.sleep(BOX_STATUS_REFRESH_INTERVAL)
        # Finally closes
        with self._lock:
            self._machine.closed()
        if opened_before:
            self._led.turn_off_red()

    def _box_error(self):
        with self._lock:
            self._machine.error()

    def _auth_error(self):
        self._led.turn_on_red()
        time.sleep(1.0)
        self._led.turn_off_red()

    def open_by_customer(self):
        """Transit status to CUSTOMER_OPEN.
        """
        # TODO authentication, and sets the flag
        flag: bool = True
        flag = flag and self._sensor.is_closed()
        # flag = flag and auth.authentication()
        if not flag:
            self._box_error()
            return False
        with self._lock:
            self._machine.open_by_customer()
        self._led.turn_on_green()
        self._block_until_closed()
        # TODO update box status

    def __enter__(self):
        return self

    # exc_type: type, exc_value: Exception, tb: traceback.TracebackException
    def __exit__(self, *args):
        self._reader.__exit__(*args)
        self._led.__exit__(*args)
        # TODO also sensor manager
