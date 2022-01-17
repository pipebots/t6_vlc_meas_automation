import time
import datetime
import logging
from typing import Union
import ipaddress
import pyvisa


class E4438C():
    def __init__(self, instr_name: str, address: Union[str, int],
                 visamr: pyvisa.ResourceManager,
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

        self.vendor = None
        self.model_number = None
        self.serial_number = None
        self.fw_version = None

        self._frequency = None
        self.frequency_unit = "Hz"

        self._power = None
        self.power_unit = "dBm"

        self._output_enabled = None
        self._mod_enabled = None

        self.reset()
        self._log_details()

    def __del__(self):
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
        logger_handler.setLevel(logging.DEBUG)

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
            level=logging.DEBUG,
        )
        logger.info("Logger configuration done")

        return logger

    def _op_complete(self):
        response = self.instr_conn.query("*OPC?", self.query_delay)
        return response == "1"

    def reset(self):
        self.instr_conn.write("*RST")
        time.sleep(0.25)
        self.instr_conn.write("*CLS")
        time.sleep(0.25)

    def _log_details(self):
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
        return (self._frequency, self.frequency_unit)

    @frequency.setter
    def frequency(self, new_params: Union[str, int, float]):
        try:
            new_freq, unit = new_params.split()
        except (ValueError, AttributeError) as error:
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
        except (ValueError, AttributeError) as error:
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
