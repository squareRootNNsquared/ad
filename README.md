### Low-Resolution Methodology

Process past data, process current data.

Past data builds network with each event in stream, current data builds network and generates statistics with each event in stream. Statistics generate anomalous events to be sequentially logged.

ad in /src/ad.py corresponds to Anomaly Detection
s in /src/s.py corresponds to Server

s runs a local server from which ad accepts information in the mimicing of a stream. s.py must be run before and concurrent with ad.py.
