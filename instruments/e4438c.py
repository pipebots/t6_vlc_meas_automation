"""Module holding Signal Generator Classes

"""
import time
import datetime
import logging
from typing import Union, Optional
import ipaddress
import pyvisa


class E4438C():
    """Remote control of an Keysight E4438C Signal Generator using SCPI cmds.

    A class representation of a Keysight E4438C Signal Generator, that provides
    remote control capabilities through the use of SCPI commands. A connection
    is established over a GPIB or a LAN interface. Currently only very basic
    functionality is supported.

    Attributes:
        instr_conn:
        name:
        logger:
        query_delay:
        vendor:
        model_number:
        serial_number:
        fw_version:
        frequency:
        frequency_unit:
        power:
        power_unit:
        output_enabled:
        mod_enabled:
        details:
    """
    def __init__(self, visamr: pyvisa.ResourceManager,
                 address: Union[str, int], instr_name: str,
                 logger: logging.Logger = None):
        if isinstance(address, str):
            try:
                ipaddress.ip_address(address)
                instr_address = f"TCPIP0::{address}::INST0:INSTR"
            except ValueError as error:
                if logger is not None:
                    logger.warning("%s is not a valid IP address", address)
                raise ValueError("Please use a valid IP address") from error

        elif isinstance(address, int):
            if 0 <= address <= 30:
                instr_address = f"GPIB0::{address}::INSTR"
            else:
                if logger is not None:
                    logger.warning("%d is not a valid GPIB address", address)
                raise ValueError("Please use a valid GPIB address")
        else:
            raise RuntimeError("Only IPv4 and GPIB addresses are supported")

        try:
            self.instr_conn = visamr.open_resource(
                instr_address, read_termination="\n", write_termination="\n"
            )
            self.name = instr_name
            self.logger = logger if logger is not None else self.__get_logger()
            self.logger.info("Established connection with %s", self.name)
        except pyvisa.VisaIOError as error:
            if logger is not None:
                logger.critical("Could not connect to %s", instr_name)
                logger.critical("Error message: %s", error.args)
            raise RuntimeError("Could not connect to instrument") from error

        self.query_delay = 0.25

        self.vendor: Optional[str] = None
        self.model_number: Optional[str] = None
        self.serial_number: Optional[str] = None
        self.fw_version: Optional[str] = None

        self._frequency = None
        self.frequency_unit = "Hz"

        self._power = None
        self.power_unit = "dBm"

        self._output_enabled: Optional[bool] = None
        self._mod_enabled: Optional[bool] = None

        self.reset()
        self._log_details()

    def __del__(self):
        """Destructor

        Makes sure to close the VISA connection to the instrument before the
        object is deleted.
        """
        self.logger.info("Closing connection to %s", self.name)
        self.instr_conn.close()

    def __get_logger(self) -> logging.Logger:
        """Sets up a `Logger` object for diagnostic and debug

        A standard function to set up and configure a Python `Logger` object
        for recording diagnostic and debug data.

        Args:
            None

        Returns:
            A `Logger` object with appropriate configurations. All the messages
            are duplicated to the command prompt as well.

        Raises:
            Nothing
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = "_".join([self.name, timestamp])
        log_filename = ".".join([log_filename, "log"])

        logger = logging.getLogger(self.name)

        logger_handler = logging.FileHandler(log_filename)
        logger_handler.setLevel(logging.INFO)

        fmt_str = "{asctime:s} {msecs:.3f} \t {levelname:^10s} \t {message:s}"
        datefmt_string = "%Y-%m-%d %H:%M:%S"
        logger_formatter = logging.Formatter(
            fmt=fmt_str, datefmt=datefmt_string, style="{"
        )

        # * This is to ensure consistent formatting of the miliseconds field
        logger_formatter.converter = time.gmtime

        logger_handler.setFormatter(logger_formatter)
        logger.addHandler(logger_handler)

        # * This enables the streaming of messages to stdout
        logging.basicConfig(
            format=fmt_str,
            datefmt=datefmt_string,
            style="{",
            level=logging.INFO,
        )
        logger.info("Logger configuration done")

        return logger

    def _op_complete(self):
        """Waits for operation to complete

        Queries the instrument for completion of any pending operations. The
        query should only return once everything is complete.

        Returns:
            A `True` or `False` boolean value. Should only ever return `True`
        """

        response = self.instr_conn.query("*OPC?", self.query_delay)
        return response.lower() == "1"

    def reset(self):
        """Resets an instrument to factory default settings

        Standard commands to reset an instrument to factory default settings,
        and to clear the status register of the instrument.
        """

        self.instr_conn.write("*RST")
        time.sleep(0.25)
        self.instr_conn.write("*CLS")
        time.sleep(0.25)

    def _log_details(self):
        """Logs instrument-specific details

        An internal function to log an instrument's vendor, model number, and
        other relevant details.
        """

        idn_response = self.instr_conn.query("*IDN?", self.query_delay)
        (self.vendor,
         self.model_number,
         self.serial_number,
         self.fw_version) = idn_response.split(",")

        self.vendor = self.vendor.strip()
        self.model_number = self.model_number.strip()
        self.serial_number = self.serial_number.strip()
        self.fw_version = self.fw_version.strip()

        self.logger.info("Instrument vendor: %s", self.vendor)
        self.logger.info("Instrument model number: %s", self.model_number)
        self.logger.info("Instrument serial number: %s", self.serial_number)
        self.logger.info("Instrument firmware version: %s", self.fw_version)

    @property
    def details(self):
        """Human-friendly summary of the instrument we are connected to

        Returns a more human-friendly summary of the main details of the
        instrument to which we are connected, including the VISA address.
        """
        print(
            f"{self.vendor} {self.model_number} connected on "
            f"{self.instr_conn.resource_name} with alias {self.name}.\n"
            f"Serial number: {self.serial_number}\n"
            f"Firmware version: {self.fw_version}"
        )

    @property
    def frequency(self):
        if self._frequency is None:
            self._frequency = self.instr_conn.query(
                ":SOURce:FREQuency:CW?", self.query_delay
            )
            self.frequency_unit = "Hz"
        return (self._frequency, self.frequency_unit)

    @frequency.setter
    def frequency(self, new_params: Union[str, int, float]):
        try:
            new_freq, unit = new_params.split()
        except (ValueError, AttributeError) as _:
            new_freq = new_params
            unit = self.frequency_unit

        self.instr_conn.write(f":SOURce:FREQuency:CW {new_freq} {unit}")

        if self._op_complete():
            self._frequency = new_freq
            self.frequency_unit = unit
            print(f"Frequency set to {new_freq} {unit}")
        else:
            print(f"Error setting frequency to {new_freq} {unit}")

    @property
    def power(self):
        if self._power is None:
            self._power = self.instr_conn.query(
                ":SOURce:POWer:LEVel:IMMediate:AMPlitude?", self.query_delay
            )
        return (self._power, self.power_unit)

    @power.setter
    def power(self, new_params: Union[str, int, float]):
        try:
            new_power, unit = new_params.split()
        except (ValueError, AttributeError) as _:
            new_power = new_params
            unit = self.power_unit

        self.instr_conn.write(
            f":SOURce:POWer:LEVel:IMMediate:AMPlitude {new_power} {unit}"
        )

        if self._op_complete():
            self._power = new_power
            self.power_unit = unit
            print(f"Output power set to {new_power} {unit}")
        else:
            print(f"Error setting output power to {new_power} {unit}")

    @property
    def output(self):
        """Returns the state of the Signal Generator's RF Output

        Queries and returns the state of the RF output. The return value of
        the query can be either "1" / "ON" or "0" / "OFF". We convert that to
        a `bool` value of `True` or `False`.

        Returns:
            A `True` / `False` boolean value
        """

        if self._output_enabled is None:
            current_state = self.instr_conn.query(
                ":OUTPut:STATe?", self.query_delay
            )
            self._output_enabled = (
                current_state.lower() == "1" or current_state.lower() == "on"
            )
        return self._output_enabled

    @output.setter
    def output(self, new_state: Union[int, str]):
        """Sets the state of the Signal Generator's RF Output

        This is the corresponding setter method which sets the new state and
        waits for the operation to complete.

        Args:
            new_state: Either an `int` or a `str` with the new state.
                       Acceptable values are 1 / "1" / "on" or 0 / "0" / "off".
                       Other values will fail silently. This is still converted
                       to a boolean value internally.
        """

        self.instr_conn.write(
            f":OUTPut:STATe {new_state}"
        )

        if self._op_complete():
            new_state = str(new_state)
            self._output_enabled = (
                new_state.lower() == "1" or new_state.lower() == "on"
            )
            print(f"Output enabled set to {self._output_enabled}")
        else:
            print(f"Error setting output enabled to {new_state}")

    @property
    def mod_state(self):
        """Returns the state of the Signal Generator's RF modulation setting

        Queries and returns the state of the RF modulation. The return value of
        the query can be either "1" / "ON" or "0" / "OFF". We convert that to
        a `bool` value of `True` or `False`.

        Returns:
            A `True` / `False` boolean value
        """

        if self._mod_enabled is None:
            current_state = self.instr_conn.query(
                ":OUTPut:MODulation:STATe?", self.query_delay
            )
            self._mod_enabled = (
                current_state.lower() == "1" or current_state.lower() == "on"
            )
        return self._mod_enabled

    @mod_state.setter
    def mod_state(self, new_state: Union[int, str]):
        """Enables or disables the Signal Generator's RF modulation setting

        This is the corresponding setter method which sets the new state and
        waits for the operation to complete.

        Args:
            new_state: Either an `int` or a `str` with the new state.
                       Acceptable values are 1 / "1" / "on" or 0 / "0" / "off".
                       Other values will fail silently. This is still converted
                       to a boolean value internally.
        """

        self.instr_conn.write(
            f":OUTPut:MODulation:STATe {new_state}"
        )

        if self._op_complete():
            new_state = str(new_state)
            self._mod_enabled = (
                new_state.lower() == "1" or new_state.lower() == "on"
            )
            print(f"Modulation enabled set to {self._mod_enabled}")
        else:
            print(f"Error setting dodulation enabled to {new_state}")
