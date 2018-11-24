# Author: Andrey Filonov
# andrey.filonov@gmail.com
# 12.11.2017

from math import pi, sqrt, sin, cos
import sys
import time
import getopt
import configparser
import os.path

__all__ = ['Encoder']

config_file = 'qpsk_encoder.ini'


class Encoder:
    def __init__(self):

        if os.path.isfile(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)

            self.filter_width = 2 * int(config['Options']['FilterWidth'])  # default value 10
            self.read_buffer_size = int(config['Options']['ReadBufferSize'])  # default value 1024
            self.symbol_width = int(config['Options']['SymbolWidth'])  # default value 4
            self.beta = float(config['Options']['Beta'])  # default value 0.25
            if self.beta > 1:
                self.beta = 1
            elif self.beta < 0:
                self.beta = 0
            self.rounding = int(config['Options']['CsvRounding'])
        else:  # if .ini file is not found
            self.filter_width = 2 * 10  # default value 10
            self.read_buffer_size = 1024  # default value 1024
            self.symbol_width = 4  # default value 4
            self.beta = 0.25  # default value 0.25
            self.rounding = 3  # default value 3

        self.filter_buffer = []
        for i in range(0, self.filter_width + self.read_buffer_size - 1):
            self.filter_buffer.append(0.0)

        self.constellation = []
        for i in range(0, 4):
            arg = pi * (2 * i + 1) / 4  # constellation#1: points at pi/4, pi*(3/4), pi*(5/4), pi*(7/4)
            # arg = pi * (i/2)  # alternative constellation#2: points at 0, pi/2, pi, pi*(3/2)

            self.constellation.append(cos(arg) + sin(arg)*(0+1j))
        self.constellation = tuple(self.constellation)

    def __repr__(self):
        return 'QPSK encoder'

    def modulator(self, inp):
        """
        inp: input array of bits to be modulated 
        input bits are being splitted into the pairs of 4 possible qpsk symbols: 00, 01, 10, 11
        11 - constellation point at pi/4
        01 - constellation point at pi*(3/4)
        00 - constellation point at pi*(5/4)
        10 - constellation point at pi*(7/4)
        :return: array of modulated complex numbers. The size of output list is inp*symbol_width
        """
        out = []
        m = self.symbol_width
        for i in range(0, len(inp), 2):

            if inp[i] == '1':
                if inp[i + 1] == '1':
                    out += [self.constellation[0]] * m  # 11
                else:
                    out += [self.constellation[3]] * m  # 10
            else:
                if inp[i + 1] == '1':
                    out += [self.constellation[1]] * m  # 01
                else:
                    out += [self.constellation[2]] * m  # 00
        return out

    def filter(self, coeffs, samples):
        """
        :param coeffs: tuple of a filter coefficients to apply to input samples
        :param samples: list of input samples
        :return: filtered: list of filtered samples, size = len(samples)
        """

        samples_length = len(samples)

        self.filter_buffer = self.filter_buffer[0:self.filter_width-1] + samples
        filtered = []

        for s in range(0, samples_length):
            sample_pos = self.filter_width + s - 1
            accumulator = 0.0

            for k in range(0, self.filter_width):
                accumulator += self.filter_buffer[sample_pos] * coeffs[k]  # convolution
                sample_pos -= 1

            filtered.append(accumulator)

        for i in range(0, self.filter_width-1):
            self.filter_buffer[i] = self.filter_buffer[i+samples_length]  # shift the unprocessed values to the working zone

        return filtered


def rrc(beta, filter_width, Ts):
    """
    https://en.wikipedia.org/wiki/Root-raised-cosine_filter 
    :param beta: roll-off factor
    :param filter_width: The width of the filter, samples
    :param Ts: The width of a symbol, samples
    :return: impulse response of the filter, the tuple of filter_width float numbers coefficients
    """
    rrc_out = []
    for i in range(0, filter_width):
        rrc_out.append(0.0)
    if beta != 0.0:
        t1 = Ts/(4*beta)
    else:
        t1 = Ts

    for p in range(0, filter_width):
        t = (p - filter_width / 2)
        if t == 0.0:
            rrc_out[p] = (1 + beta*(4/pi - 1))
        elif t == t1 or t == -t1:
            if beta != 0.0:
                arg = pi/(4*beta)
                s = (1 + 2/pi)*sin(arg)
                c = (1 - 2/pi)*cos(arg)
                rrc_out[p] = (s + c) * (beta/sqrt(2))
            else:
                rrc_out[p] = 0
        else:
            pts = pi*t/Ts
            bt = 4*beta*t/Ts
            s = sin(pts*(1-beta))
            c = cos(pts*(1+beta))
            div = pts*(1 - bt*bt)
            rrc_out[p] = (s + bt*c)/div
    return tuple(rrc_out)


def bytes2bits(byte):
    # gets a byte and converts it into a list of bits
    return tuple(bin(byte).lstrip('0b').zfill(8))


class Output:

    def __init__(self):
        self.counter = 1
        if os.path.isfile(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            self.rounding = int(config['Options']['CsvRounding'])
            self.benchmark = config['Debug'].getboolean('Benchmark')  # default value is False
        else:
            self.rounding = 3  # default value
            self.benchmark = False  # default value is False

    def csv_converter(self, inp):

        if self.benchmark:
            return

        f = "%." + str(self.rounding) + "f"
        for i in inp:
            print(str(self.counter) + "," + f % i.real + "," + f % i.imag)
            self.counter += 1
# ====================================


def main(argv):
    # debug = True
    debug = False

    if debug:
        source = open("input2.txt", "rb")
    else:
        source = sys.stdin.buffer

    encoder = Encoder()

    buffer = []
    rrc_coefficients = rrc(encoder.beta, encoder.filter_width, encoder.symbol_width)

    output = Output()
    start = time.time()
    byte = source.read(1)
    bytes_counter = 1
    while len(byte) == 1:
        buffer += encoder.modulator(bytes2bits(int.from_bytes(byte, byteorder='big')))

        if len(buffer) >= encoder.read_buffer_size:
            filtered = encoder.filter(rrc_coefficients, buffer)
            output.csv_converter(filtered)
            buffer = []
        byte = source.read(1)
        bytes_counter += 1
    if len(buffer) > 0:
        filtered = encoder.filter(rrc_coefficients, buffer)
        output.csv_converter(filtered)

    if output.benchmark:
        total_time = time.time() - start
        encoding_rate = bytes_counter * 8 / total_time
        print("%.0f" % encoding_rate + " bits/sec")

if __name__ == '__main__':
    main(sys.argv[1:])
