import binascii
import datetime
import logging
import socket
import time
from ipaddress import ip_address


class PSU72:
    def __init__(self, address: str, logger: logging.Logger = None):
        self.logger = logger if logger is not None else self.__get_logger()

        try:
            ip_address(address)
        except ValueError as error:
            self.logger.warning("%s is not a valid IP address", address)
            raise ValueError("Please use a valid IP address") from error
        else:
            self._ipaddress = address

        # ! This might be hard-coded in the instrument firmware. No reason to
        # ! change it unless something else is using the same port on the
        # ! controlling PC.
        self._udp_port = 18190
        self._buf_size = 1024

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as err:
            self.logger.critical(f"Error creating socket: {err}")
            raise RuntimeError("Could not create UDP socket")
        else:
            self.logger.info("Successfully created UDP socket")

        try:
            self._sock.bind(('0.0.0.0', self._udp_port))
        except socket.error as err:
            self.logger.critical(f"Error binding socket: {err}")
            raise RuntimeError("Could not bind socket - port in use?")
        else:
            self.logger.info("Successfully bound socket to UDP port")

        self._sock.setblocking(False)

        try:
            self._sock.connect((self._ipaddress, self._udp_port))
        except socket.error as err:
            self.logger.critical(f"Error connecting to remote: {err}")
            raise RuntimeError("Could not connect to PSU - check if on?")
        else:
            self.logger.info("Successfully connected to remote PSU")

        # * Lock the front panel while PSU is remotely controlled
        self._sock.send(b'LOCK1\n')

        # * 100 ms delay between sending a command and receiving the response
        self._recv_delay = 0.1

    def __del__(self):
        self.logger.info("Closing UDP connection to remote PSU")
        self._sock.send(b'LOCK0\n')
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

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
        log_filename = "_".join(["PSU", timestamp])
        log_filename = ".".join([log_filename, "log"])

        logger = logging.getLogger("PSU")

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

    @property
    def identity(self):
        cmd = b'*IDN?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        return response.strip().decode()

    @property
    def status(self):
        cmd = b'STATUS?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        response = binascii.hexlify(response[:-1])
        response = int(response, base=16)

        if response & 0b1:
            print("Channel 1 set to Constant Voltage (CV)")
        else:
            print("Channel 1 set to Constant Current (CC)")

        if (response >> 6) & 0b1:
            print("Channel 1 output is set to ON")
        else:
            print("Channel 1 output is set to OFF")

        if (response >> 1) & 0b1:
            print("Channel 2 set to Constant Voltage (CV)")
        else:
            print("Channel 2 set to Constant Current (CC)")

        if (response >> 7) & 0b1:
            print("Channel 2 output is set to ON")
        else:
            print("Channel 2 output is set to OFF")

        tracking_mode = ((response >> 3) & 0b1) << 1 + ((response >> 2) & 0b1)
        if tracking_mode == 2:
            print("Channels tracking in parallel")
        elif tracking_mode == 1:
            print("Channels tracking in series")
        else:
            print("Channels are independent")

    @property
    def tracking(self):
        print("Please use the `status` command instead")

    @tracking.setter
    def tracking(self, new_state: int):
        if 0 <= new_state <= 2:
            cmd = f'TRACK{new_state}\n'
            self._sock.send(cmd.encode())
        else:
            raise ValueError(
                "Tracking state must be 0 (independent), 1 (series), or "
                "2 (parallel)"
            )

    @property
    def ch1_output(self):
        print("Please use the `status` command instead")

    @ch1_output.setter
    def ch1_output(self, new_state: bool):
        if new_state:
            cmd = b'OUT1:1\n'
        else:
            cmd = b'OUT1:0\n'
        self._sock.send(cmd)
        self.logger.info(f"Channel 1 output set to {new_state}")

    @property
    def ch2_output(self):
        print("Please use the `status` command instead")

    @ch2_output.setter
    def ch2_output(self, new_state: bool):
        if new_state:
            cmd = b'OUT2:1\n'
        else:
            cmd = b'OUT2:0\n'
        self._sock.send(cmd)
        self.logger.info(f"Channel 2 output set to {new_state}")

    @property
    def ch1_voltage(self) -> float:
        cmd = b'VSET1?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        voltage = float(response.strip())
        self.logger.info(f"Channel 1 voltage is set to {voltage} V")

        return voltage

    @ch1_voltage.setter
    def ch1_voltage(self, new_voltage: float):
        cmd = f'VSET1:{new_voltage}\n'
        self._sock.send(cmd.encode())

        self.logger.info(f"Channel 1 voltage set to {new_voltage} V")

    @property
    def ch2_voltage(self) -> float:
        cmd = b'VSET2?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        voltage = float(response.strip())
        self.logger.info(f"Channel 2 voltage is set to {voltage} V")

        return voltage

    @ch2_voltage.setter
    def ch2_voltage(self, new_voltage: float):
        cmd = f'VSET2:{new_voltage}\n'
        self._sock.send(cmd.encode())

        self.logger.info(f"Channel 2 voltage set to {new_voltage} V")

    @property
    def ch1_current(self) -> float:
        cmd = b'ISET1?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        current = float(response.strip())
        self.logger.info(f"Channel 1 current is set to {current} A")

        return current

    @ch1_current.setter
    def ch1_current(self, new_current: float):
        cmd = f'ISET1:{new_current}\n'
        self._sock.send(cmd.encode())

        self.logger.info(f"Channel 1 current set to {new_current} A")

    @property
    def ch2_current(self) -> float:
        cmd = b'ISET2?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        current = float(response.strip())
        self.logger.info(f"Channel 2 current is set to {current} A")

        return current

    @ch2_current.setter
    def ch2_current(self, new_current: float):
        cmd = f'ISET2:{new_current}\n'
        self._sock.send(cmd.encode())

        self.logger.info(f"Channel 2 current set to {new_current} A")

    @property
    def ch1_out_voltage(self) -> float:
        cmd = b'VOUT1?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        out_voltage = float(response.strip())
        self.logger.info(f"Channel 1 actual output voltage is {out_voltage} V")

        return out_voltage

    @property
    def ch2_out_voltage(self) -> float:
        cmd = b'VOUT2?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        out_voltage = float(response.strip())
        self.logger.info(f"Channel 2 actual output voltage is {out_voltage} V")

        return out_voltage

    @property
    def ch1_out_current(self) -> float:
        cmd = b'IOUT1?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        out_current = float(response.strip())
        self.logger.info(f"Channel 1 actual output current is {out_current} A")

        return out_current

    @property
    def ch2_out_current(self) -> float:
        cmd = b'IOUT2?\n'
        self._sock.send(cmd)
        time.sleep(self._recv_delay)
        response = self._sock.recv(self._buf_size)

        out_current = float(response.strip())
        self.logger.info(f"Channel 2 actual output current is {out_current} A")

        return out_current
