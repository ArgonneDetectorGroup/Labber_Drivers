LABBER_PATH = '/Program Files (x86)/Labber/Script/'
LABBER_SERVER = 'localhost'
VOLTMETER = 'Stanford Research SIM 970 Voltmeter'
VOLTMETER_QUANT = 'Ch4 Voltage'

# LABBER_PATH should be added to PYTHON_PATH already. If not, uncomment the next two lines
# import sys
# sys.path.append(LABBER_PATH)

import Labber as lab
import InstrumentDriver

def VtoP(voltage):
    return 10**(2*(voltage-5.5))

class Driver(InstrumentDriver.InstrumentWorker):
    
    def performOpen(self, options={}):
        """Try to connect to the voltmeter. Start it up if necessary."""
        self.voltmeter = None

        self.client = lab.connectToServer(LABBER_SERVER)
        instruments = self.client.getListOfInstruments()

        for hardware, config in instruments:
            if hardware == VOLTMETER:
                self.voltmeter = self.client.connectToInstrument(VOLTMETER, dict(name=config['name']))

        assert self.voltmeter is not None, "ERROR: Could not find a voltmeter!"

        if not self.voltmeter.isRunning():
            self.voltmeter.startInstrument()

        assert self.voltmeter.isRunning() == True, "ERROR: Cannot start voltmeter"

    def performGetValue(self, quant, options={}):
        if quant.name == 'Pressure':
            voltage = self.voltmeter.getValue(VOLTMETER_QUANT)
            pressure = VtoP(voltage)

            return pressure
        else:
            assert False, "Error: unknown quantity"

        return 'none'
