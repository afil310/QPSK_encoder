
# QPSK encoder
![License](https://img.shields.io/badge/licence-MIT-blue.svg)

## Description
QPSK encoder with <a href="https://en.wikipedia.org/wiki/Root-raised-cosine_filter">Root-raised-cosine filter</a> reads data from `stdin` and prints encoded data to `stdout`. 
<a href="https://en.wikipedia.org/wiki/Phase-shift_keying#Quadrature_phase-shift_keying_(QPSK)">Quadrature Phase Shift Keying</a> is used for the input data encoding.

Output data format: `<sample number, I, Q>`, where `I(t)` and `Q(t)` are the modulating signals.

If benchmark mode is on, then the encoding speed (bit/s) is printed to `stdout`.

## Parameters
The encoder parameters are set in qpsk_encoder.ini file :
```ini
[Options]
FilterWidth: 10
SymbolWidth: 4
Beta: 0.25
ReadBufferSize: 1
CsvRounding: 3
[Debug]
Benchmark: False
```
- `FilterWidth` - the number of samples to apply the filter.

- `SymbolWidth` - the number of samples per symbol.

- `Beta` - β, or the roll-off factor - the parameter for Root-raised-cosine filter.

- `ReadBufferSize` - the buffer size for data reading from stdin or file.

- `CsvRounding` - the number of decimal places for I and Q rounding.
- `Benchmark`: 
	- `Benchmark: False` - the encoding mode is on.
	- `Benchmark: True`  - the benchmark mode is on. The input data from `stdin` is encoded, but only the encoding speed (bit/s) is printed to `stdout`.

## Requirements
- Python 3
## Usage
Run the encoder from the command line:
```bash
python3 qpsk_encoder.py < input.file > output.csv
```
### Example
```bash
echo 1 | python3 qpsk_encoder.py
```
where
```bash
echo 1
```
prints '1' to `stdout`, and 
```bash
| python3 qpsk_encoder.py
```
reads '1' from `stdin` and encodes it into 32 samples, as there are 8 bits in '1' character and each bit is encoded into 4 samples as `SymbolWidth` parameter is set to 4. 
<details> 
<summary>The resulting output in `stdout` : </summary><p>

```bash
1,-0.046,-0.046
2,-0.113,-0.113
3,-0.150,-0.150
4,-0.111,-0.111
5,0.101,0.101
6,0.375,0.375
7,0.495,0.495
8,0.249,0.249
9,-0.523,-0.523
10,-1.604,-1.604
11,-2.526,-2.526
12,-2.778,-2.778
13,-2.098,-2.006
14,-0.651,-0.426
15,0.996,1.296
16,2.134,2.356
17,2.254,2.144
18,1.296,0.771
19,-0.344,-1.034
20,-2.025,-2.301
21,-3.145,-2.301
22,-3.559,-1.101
23,-3.393,0.667
24,-2.979,2.079
25,-2.646,2.319
26,-2.435,1.400
27,-2.435,-0.277
28,-2.646,-2.025
29,-2.887,-3.145
30,-3.168,-3.559
31,-3.259,-3.393
32,-2.922,-2.979
```

</p></details>


## Author

Andrey Filonov, andrey.filonov@gmail.com

## License
`QPSK encoder` is available under the MIT license. See the LICENSE file for more info.

