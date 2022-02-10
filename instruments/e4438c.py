"""Module holding Signal Generator Classes

Currently only Keysight's E4438C is included and supported. A lot of work to
be done, including splitting this into base and inherited classes.
"""

import time
import datetime
import logging
from typing import Union, Optional
from ipaddress import ip_address
import pyvisa


class E4438C:
    """Remote control of an Keysight E4438C Signal Generator using SCPI cmds.

    A class representation of a Keysight E4438C Signal Generator, that provides
    remote control capabilities through the use of SCPI commands. A connection
    is established over a GPIB or a LAN interface. Currently only very basic
    functionality is supported.

    Attributes:
        name: A `str` with a human-friendly name for the instrument, used to
              identify it in the logs.
        logger: A `logging.Logger` object to which to save info and diagnostic
                messages.
        query_delay: A `float` with the delay, in seconds, between VISA write
                     and read operations.
        vendor: A `str` with the vendor name, as provided by the instrument
        model_number: A `str` with the model number, as provided by the
                      instrument.
        serial_number: A `str` with the serial number, as provided by the
                       instrument.
        fw_version: A `str` with the firmware version, as provided by the
                    instrument.
        details: A human-friendly `str` with a summary of the instrument's
                 self-reported details.
        frequency: A `float` or an `int` with the CW frequency of the Signal
                   Generator. Currently only supports Hz.
        power: A `float` or an `int` with the RF output power of the Signal
               Generator. Currently only supports dBm.
        output: A `bool` showing the state of the RF output of the instrument,
                i.e. ON / OFF.
        mod_state: A `bool` showing whether modulation is enabled or not.
    """

    def __init__(self, visamr: pyvisa.ResourceManager,
                 address: Union[str, int], instr_name: str,
                 logger: logging.Logger = None):
        """Establishes a VISA connection to an instrument and presets it

        Establishes a remote connection to a Keysight E4438C Signal Generator,
        over either GPIB or LAN interface. Presets the instrument and writes
        certain details, as reported by it, to a log file. Allows programmatic
        control over CW frequency, RF output power, and modulation state.

        Args:
            visamr: A `pyvisa.ResourceManager` object used to establish a
                    remote connection to the instrument. Normally this object
                    is shared with other instruments, and is expected to be
                    initialised before the instrument.
            address: A `str` with an IPv4 address or an `int` with a GPIB
                     address. Only primary GPIB addresses, i.e. 0 - 30 are
                     supported.
            instr_name: A `str` with a a name, or alias, for the instrument,
                        to identify it more easily in the logs.
            logger: An optional `logging.Logger` object to which to write
                    diagnostic and info messages. If one is not supplied,
                    a new one is created internally.

        Raises:
            ValueError: If an invalid IPv4 or GPIB address is specified.
            RuntimeError: If a different type of address is specified, or if
                          a remote connection to the instrument cannot be
                          established.
        """

        if isinstance(address, str):
            try:
                ip_address(address)
                instr_address = f"TCPIP0::{address}::inst0::INSTR"
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
            self._instr_conn = visamr.open_resource(
                instr_address, read_termination="\n", write_termination="\n"
            )
            self.name = instr_name
            self.logger = logger if logger is not None else self.__get_logger()
            self.logger.info("Established connection to %s", self.name)
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

        self._frequency: Optional[float] = None
        self._frequency_unit = "Hz"

        self._power: Optional[float] = None
        self._power_unit = "dBm"

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
        self._instr_conn.close()

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

        response = self._instr_conn.query("*OPC?", self.query_delay)
        return response.lower() == "1"

    def reset(self):
        """Resets an instrument to factory default settings

        Standard commands to reset an instrument to factory default settings,
        and to clear the status register of the instrument.
        """

        self._instr_conn.write("*RST")
        time.sleep(self.query_delay)
        self._instr_conn.write("*CLS")
        time.sleep(self.query_delay)

    def _log_details(self):
        """Logs instrument-specific details

        An internal function to log an instrument's vendor, model number, and
        other relevant details.
        """

        idn_response = self._instr_conn.query("*IDN?", self.query_delay)
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
            f"{self._instr_conn.resource_name} with alias {self.name}.\n"
            f"Serial number: {self.serial_number}\n"
            f"Firmware version: {self.fw_version}"
        )

    @property
    def frequency(self):
        """Returns the CW frequency to which the Signal Generator is set

        Queries, if necessary, the CW frequency to which the Signal Generator
        is currently set, and returns it together with its unit.

        Returns:
            A `tuple` consisting of the frequency in Hz as a `float` and the
            unit used internally, as a `str`.
        """

        if self._frequency is None:
            self._frequency = float(self._instr_conn.query(
                ":SOURce:FREQuency:CW?", self.query_delay
            ))
        return (self._frequency, self._frequency_unit)

    @frequency.setter
    def frequency(self, new_freq: Union[int, float]):
        """Sets the CW frequency of the Signal Generator

        Sends the SCPI command to set a CW frequency, waits for the operation
        to complete, and confirms success.

        Notes:
            There is no bounds checking right now, nor are units different
            than Hz supported. This will change in the future.

        Args:
            new_freq: An `int` or a `float` with the new frequency.
                      The value should be in Hz.
        """

        self._instr_conn.write(
            f":SOURce:FREQuency:CW {new_freq} {self._frequency_unit}"
        )

        if self._op_complete():
            self._frequency = float(new_freq)
            print(f"Frequency set to {self._frequency} {self._frequency_unit}")
        else:
            print(
                f"Error setting frequency to {new_freq} {self._frequency_unit}"
            )

    @property
    def power(self):
        """Returns the RF output power to which the Signal Generator is set

        Queries, if necessary, the RF output power to which the Signal
        Generator is currently set, and returns it together with its unit.

        Returns:
            A `tuple` consisting of the power in dBm as a `float` and the
            unit used internally, as a `str`.
        """

        if self._power is None:
            self._power = float(self._instr_conn.query(
                ":SOURce:POWer:LEVel:IMMediate:AMPlitude?", self.query_delay
            ))
        return (self._power, self._power_unit)

    @power.setter
    def power(self, new_power: Union[int, float]):
        """Sets the RF output power of the Signal Generator

        Sends the SCPI command to set a RF output power, waits for the
        operation to complete, and confirms success.

        Notes:
            There is no bounds checking right now, nor are units different
            than dBm supported. This will change in the future.

        Args:
            new_freq: An `int` or a `float` with the new RF output power.
                      The value should be in dBm.
        """

        self._instr_conn.write(
            f":SOURce:POWer:LEVel:IMMediate:AMPlitude"
            f" {new_power} {self._power_unit}"
        )

        if self._op_complete():
            self._power = float(new_power)
            print(f"Output power set to {self._power} {self._power_unit}")
        else:
            print(
                f"Error setting output power to {new_power} {self._power_unit}"
            )

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
            current_state = self._instr_conn.query(
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

        self._instr_conn.write(
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
            current_state = self._instr_conn.query(
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

        self._instr_conn.write(
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
