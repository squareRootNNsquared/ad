### Low-Resolution Methodology

Process past data, process current data.

Past data builds network with each event in stream, current data builds network and generates statistics with each event in stream. Statistics generate anomalous events to be sequentially logged. s runs a local server from which ad accepts information in the mimicing of a stream of current data. To operate the program s.py must be run before and concurrent with ad.py.

ad in /src/ad.py corresponds to Anomaly Detection
s in /src/s.py corresponds to Server

The following libraries and packages are made use of in this project:

 os
 sys
 SocketServer
 socket
urllib2
 datetime
 time
 json
 ast
 math

