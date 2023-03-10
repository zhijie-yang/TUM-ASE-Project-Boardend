import enum
import traceback
import time
from threading import RLock
import logging
from transitions.extensions import LockedMachine
from box_manager.led_manager import LedManager
from box_manager.photo_resistor import PhotoResistor
from rfid_manager.reader import RfidReader
from utils.configure_reader import BOX_STATUS_REFRESH_INTERVAL
from utils.manager_base import ManagerBase
from utils.authenticator import Authenticator
from utils.configure_reader import ConfigureReader


logger = logging.getLogger(__name__)


class BoxManagerError(Exception):  # pylint: disable=missing-class-docstring
    pass


class Roles(enum.Enum):
    """Enum of roles"""

    DELIVERER = 0
    CUSTOMER = 1


class BoxManager(ManagerBase):
    """Singleton, manage box manager life cycle"""

    class States(enum.Enum):
        """State of SFM"""

        ERROR = -1
        STOPPED = 0
        STANDBY = 1
        STARING = 2
        OPEN = 3
        READER = 4

    transitions = [
        ["start", States.STOPPED, States.STARING],
        ["stop", [States.STANDBY, States.ERROR], States.STOPPED],
        ["reset", States.ERROR, States.STOPPED],
        ["start_success", States.STARING, States.STANDBY],
        ["error", "*", States.ERROR],
        ["opened", States.STANDBY, States.OPEN],
        ["closed", States.OPEN, States.STANDBY],
    ]

    def __init__(self):
        self._lock = RLock()
        self._machine = LockedMachine(
            states=self.States,
            transitions=self.transitions,
            initial=self.States.STOPPED,
        )

        self._reader = RfidReader()
        self._led = LedManager()
        self._sensor = PhotoResistor()
        self._config = ConfigureReader()

        self._authencator = Authenticator(self._config.get("backend_url"))
        logger.info("Successfully initialized box manager")

    def reset(self):
        """Resets box manager state machine."""
        if not self._machine.is_ERROR():
            raise BoxManagerError(
                "cannot reset box manager when status {} != ERROR".format(
                    self._machine.state
                )
            )
        with self._lock:
            try:
                pass
            finally:
                self._machine.reset()

    def start(self, timeout: int = 60) -> bool:
        """Try to start box manager with given parameters; will block the thread until return."""
        with self._lock:
            try:
                if not self._machine.is_STOPPED():
                    return True
                self._machine.start()
                # TODO start the reader and other tasks
            except Exception as e:  # pylint: disable=invalid-name
                logger.error(
                    "Start error: {}".format(
                        e
                    )  # pylint: disable=logging-format-interpolation
                )
                logger.error(traceback.format_exc())
                self._machine.error()
                raise e

            if self._authencator.login(
                self._config.get("id"), self._config.get("password")
            ):
                self._machine.start_success()
                logger.info("Successfully started box manager")
                return True
            else:
                logger.error("Fail to register delivery box to backend!!")
                return False

    @staticmethod
    def _check_closed_timeout(start_time: float, timeout: float = 10.0) -> bool:
        """Checks if the box is closed within time.

        Args:
            timeout (float, optional): Timeout. Defaults to 10.0.

        Returns:
            bool: result
        """
        return time.time() >= (start_time + timeout)

    def _warn_timeout(self):
        """Light the red led and set state machine to timeout statue."""
        with self._lock:
            self._machine.open_timeout()
        self._led.turn_on_red()

    def _block_until_closed(self, timeout: float = 10.0):
        """Blocked checking if the box is closed within time. Makes red light flash
            if not. Unblocks until the box is properly closed. Should be called with
            green LED on.

        Args:
            timeout (float, optional): _description_. Defaults to 10.0.

        Returns:
            bool: if box is opened before it closes
        """
        if not self._led.get_status_green():
            self._box_error()

        start_time: float = time.time()
        opened_before: bool = False
        # If the box is never opened
        logger.info("Waiting for box open.")
        while self._sensor.is_closed():
            time.sleep(BOX_STATUS_REFRESH_INTERVAL)
            if self._check_closed_timeout(start_time, timeout):
                with self._lock:
                    self._machine.closed()
                self._led.turn_off_green()
                logger.info("Box did not open within timeout. Auth cancelled.")
                return False
            logger.debug("box opened: {}".format(self._sensor.is_opened()))
            if self._sensor.is_opened():
                opened_before = True
                logger.info("Box opened.")
                break
        self._led.turn_off_green()
        # Resets the start time once box opened
        start_time = time.time()
        # The open permission is expired, i.e.
        # the box is either opened or the timeout is reached.
        while not self._sensor.is_closed():
            if self._check_closed_timeout(start_time, timeout):
                logger.error("Box not close within timeout!!")
                if not self._led.get_status_red():
                    self._led.turn_on_red()
            time.sleep(BOX_STATUS_REFRESH_INTERVAL)
        # Finally closes
        with self._lock:
            self._machine.closed()
        if self._led.get_status_red():
            self._led.turn_off_red()
        if opened_before:
            logger.info("Box closed.")
            return True
        return False

    def _box_error(self):
        # with self._lock:
        # self._machine.error()
        self._led.turn_on_red()
        time.sleep(1.0)
        self._led.turn_off_red()

    def _auth_error(self):
        self._led.turn_on_red()
        time.sleep(1.0)
        self._led.turn_off_red()

    def open_box(self, uid, token) -> bool:
        """Transit status to CUSTOMER_OPEN."""
        # TODO authentication, and sets the flag
        if not self._sensor.is_closed():
            with self._lock:
                self._box_error()
            logger.error("Box was opened unexpectedly.")
        # TODO Auth should return tuple(flag: bool, role: Union[Enum[Customer|Deliever]])
        # (flag, role) = flag and auth.authentication()
        # DELETE ME when auth is implemented
        # (flag, role) = True, Roles.CUSTOMER
        flag = self._authencator.auth(self._config.get("id"), token)

        if not flag:
            logger.error("Authentication failed.")
            self._box_error()
            return False
        logger.info("User {}, uid={} is authorized to open".format(uid, token))
        with self._lock:
            self._machine.opened()
        self._led.turn_on_green()
        if self._block_until_closed():
            self._authencator.update_box(self._config.get("id"), token)
        return True

    def routine_loop(self):
        """Main loop of box manager."""
        if self._sensor.is_opened():
            logger.error("Box was oopened without token!")
        # TODO put requests here to read from backend for commands
        uid, token = self._reader.read()
        if uid is not None:
            self.open_box(uid, token.strip())

    # exc_type: type, exc_value: Exception, tb: traceback.TracebackException
    def __exit__(self, *args):
        self._reader.__exit__(*args)
        self._led.__exit__(*args)
        # TODO also sensor manager
