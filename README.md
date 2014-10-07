LOGSUP-LEDTUBE
D.Block, 10-7-2014

Code, device tree, and upstart files for the LPD8806-based LED strips/tubes we
use as decorations. From a bare OS install, requires the python Adafruit_BBIO
library.

CODE:
A few files are in here together - it's currently fully-functional using
ledtube-hardcode.py. ledtube-fromcfg.py is a replacement in-progress that sources
LED sequences from a config file. It is functional but incomplete - I don't recommend
using it, and the upstart file does not reference it.

SUPPORT:
logsup-ledtube is an upstart config set up so that the tubes are plug-and-play.

The included dts file is a SPI dt overlay that's proven to be most useful with the 
strips; the one that ships with Adafruit_BBIO hasn't played nicely with the code here.
The matching dtbbo is included as a convenience.

setup.py is configured to install the python files to /opt, and then install and 
configure firmware and upstart.