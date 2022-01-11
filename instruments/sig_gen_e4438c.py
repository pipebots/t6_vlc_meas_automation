import time
from logging import Logger
from typing import Union
import ipaddress
import pyvisa


class SignalGeneratorE4438C():
    def __init__(self, instr_name: str, address: Union[str, int],
                 visamr: pyvisa.ResourceManager, logger: Logger):
        if isinstance(address, str):
            try:
                ipaddress.ip_address(address)
                instr_address = f"TCPIP0::{address}::INST0:INSTR"
            except ValueError as error:
                logger.warning("%s is not a valid IP address", address)
                raise ValueError("Please use a valid IP address") from error

        elif isinstance(address, int):
            if 0 <= address <= 30:
                instr_address = f"GPIB0::{address}::INSTR"
            else:
                raise ValueError("Please use a valid GPIB address")
        else:
            raise RuntimeError("Please use a valid IPv4 or GPIB address")

        try:
            self.instr_conn = visamr.open_resource(
                instr_address, read_termination="\n", write_termination="\n"
            )
            self.logger = logger
            self.name = instr_name
            self.logger.info("Established connection with %s", self.name)
            time.sleep(0.25)
        except pyvisa.VisaIOError as error:
            logger.critical("Could not connect to %s", instr_name)
            logger.critical("Error message: %s", error.args)
            raise RuntimeError("Could not connect to instrument") from error

        self.vendor = None
        self.model_number = None
        self.serial_number = None
        self.fw_version = None

        self.frequency = None
        self.power = None
        self.mod_state = None
        self.output_state = None

        self.instr_reset()
        self.instr_log_details()

    def instr_reset(self):
        self.instr_conn.write("*RST")
        time.sleep(0.25)
        self.instr_conn.write("*CLS")
        time.sleep(0.25)

    def instr_log_details(self):
        idn_response = self.instr_conn.query("*IDN?")
        (self.vendor,
         self.model_number,
         self.serial_number,
         self.fw_version) = idn_response.split(",")
        self.logger.info("Instrument vendor: %s", self.vendor)
        self.logger.info("Instrument model number: %s", self.model_number)
        self.logger.info("Instrument serial number: %s", self.serial_number)
        self.logger.info("Instrument firmware version: %s", self.fw_version)
