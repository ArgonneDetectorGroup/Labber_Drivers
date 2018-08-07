import serial
import InstrumentDriver

import pt415_interface as pti


port = 'COM1'
baudrate = 115200


class Driver(InstrumentDriver.InstrumentWorker):
    
    def performOpen(self, options={}):
        
        self.connection = serial.Serial(port, baudrate, timeout = 2)
        assert self.connection.isOpen(), "Serial port connection error"
        self.connection.flushInput()
        self.connection.flushOutput()
        self.connection.close()

    def performGetValue(self, quant, options={}):
        assert quant.get_cmd in pti.pt415_dict.keys(), "Error: Unknown quantity"

        with self.connection as conn:
            key = quant.get_cmd
            request = pti.pt415_dict[key].getReadRequest()
            conn.open()
            conn.flushInput()
            conn.write(request)
            response = pti.read_until(conn, '\r', 2)
            value = pti.pt415_dict[key].parseOutput(response)
        
        return value


    def performSetValue(self, quant, value, sweep_rate=0.0, options={}):
        assert quant.set_cmd in pti.pt415_dict.keys(), "Error: Unknown quantity"

        with self.connection as conn:
            key = quant.set_cmd
            request = pti.pt415_dict[key].getWriteRequest()
            conn.open()
            conn.flushInput()
            conn.write(request)

            #Make sure to do a read so it flushes out the buffer for the next cmd
            response = pti.read_until(conn, '\r', 2)
            
        return value