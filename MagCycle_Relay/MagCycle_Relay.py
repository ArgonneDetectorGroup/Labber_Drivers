import numpy as np
import PyDAQmx as mx
import InstrumentDriver

class Driver(InstrumentDriver.InstrumentWorker):

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Create task, set value, close task."""

        if quant.name == 'Relay Position':
            if value == 'Mag Cycle':
                channel = 'ADR_DIO/port2/line6'
            elif value == 'Regulate':
                channel = 'ADR_DIO/port2/line7'
            else:
                assert False, "Error, bad value"
            
            #Create a new task
            writeChan = mx.Task()
            writeChan.CreateDOChan(channel, '', mx.DAQmx_Val_ChanPerLine)

            setVal0 = np.array([0], dtype=np.uint8)
            setVal1 = np.array([1], dtype=np.uint8)
            sampsPer = mx.int32()

            #Send a 100 ms pulse to the appropriate channel (0 is on)
            writeChan.WriteDigitalLines(1, mx.bool32(True), 0, mx.DAQmx_Val_GroupByScanNumber, setVal0, mx.byref(sampsPer), None)
            self.wait(0.1)

            #Set it back to low (1 is off)
            writeChan.WriteDigitalLines(1, mx.bool32(True), 0, mx.DAQmx_Val_GroupByScanNumber, setVal1, mx.byref(sampsPer), None)

            #Memory Management!
            writeChan.ClearTask()
        else:
            assert False, "Requesting unknown quantity"

        return value


    def performGetValue(self, quant, options={}):
        """Create task, get value, close task."""

        if quant.name == 'Relay Position':
            #Create some values to put things in
            retVal = np.zeros(2, dtype=np.uint8)
            sampsPer = mx.int32()
            numBytesPer = mx.int32()

            #Create a new task
            readChan = mx.Task()
            readChan.CreateDIChan('ADR_DIO/port2/line4:5', '', mx.DAQmx_Val_ChanPerLine)

            #This does the measurement and updates the values created above
            readChan.ReadDigitalLines(1, 0, mx.DAQmx_Val_GroupByScanNumber, retVal, 2, mx.byref(sampsPer), mx.byref(numBytesPer), None)
            
            #Memory management!
            readChan.ClearTask()

            assert not all(retVal) and any(retVal), "Both channels should not be the same!"

            if all(retVal == [0,1]):
                value = "Mag Cycle"
            elif all(retVal == [1,0]):
                value = "Regulate"
            else:
                assert False, "Error: unexpected value returned "+repr(retVal)
        else:
            assert False, "Error: Unknown quantity"

        return value


