from VISA_Driver import VISA_Driver

class SIM900_Driver(VISA_Driver):
    """ This class re-implements the VISA driver"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)
        # do additional initialization code here...

        #Hacky way to make sure the input buffer is flushed out
        try:
            _ = self.read(1024)
        except:
            pass

        #Flush everything (hopefully)
        self.writeAndLog('*CLS')
        self.writeAndLog('FLOQ')

        #Step through each channel and query ID
        for ix in range(8):
            channel = ix+1
            self.writeAndLog('FLSH %d' % channel)
            self.writeAndLog('SNDT %d, "*IDN?"' % channel, bCheckError=False)
        
        #Really need to wait here to make sure the above commands have time to process
        self.wait(0.1)
        
        #Vectors for holding returned ID queries
        idns = []
        for ix in range(8):

            channel = ix+1

            #The idea here is that the SIM modules are way slower than the computer, so we
            #keep checking the number of bytes waiting at the port until it stabalizes,
            #then we read exactly the correct number of bytes from the port.

            #If we get an ID, append it to the list, otherwise append an empty string
            nbytes_waiting = int(self.askAndLog('NINP? %d' % channel, bCheckError=False))
            if nbytes_waiting > 0:
                nbytes_waiting_old = 0
                while nbytes_waiting_old != nbytes_waiting:
                    nbytes_waiting_old = nbytes_waiting
                    nbytes_waiting = int(self.askAndLog('NINP? %d' % channel, bCheckError=False))
                    self.wait(0.01)
                
                self.writeAndLog('RAWN? %d, %d' % (channel, nbytes_waiting), bCheckError=False)
                idns.append(self.read(nbytes_waiting).decode().strip('\r\n'))
            else:
                idns.append('')

        #Step through the IDs, extract the instrument name, and compare it to the selected mdoel
        #If found, now we know which channel that module lives at
        self.ports_dict = {}
        for ix, idn in enumerate(idns):
            channel = ix+1
            if idn != '':
                module_code = idn.split(',')[1]
                self.ports_dict[module_code] = channel
            else:
                module_code = 'Empty'
            
            self.setValue('Slot %d' % channel, module_code)
                   
    def performClose(self, bError=False, options={}):
        """Perform the close instrument connection operation"""
        # calling the generic VISA class to close communication
        VISA_Driver.performClose(self, bError, options=options)
        # do additional cleaning up code here...
        pass

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""

        port = self.ports_dict[options['module_code']]

        self.writeAndLog('FLSH %d' % port)
        self.writeAndLog('SNDT %d, "%s"' % (port, quant.set_cmd), bCheckError=False)

        return value

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""

        port = self.ports_dict[options['module_code']]

        self.writeAndLog('FLSH %d' % port)
        self.writeAndLog('SNDT %d, "%s"' % (port, quant.get_cmd), bCheckError=False)
        
        
        self.wait(0.1)

        #Again, the idea is to keep checking the port until it has finished publishing data.
        #There is probably a way better way to do this....
        nbytes_waiting = int(self.askAndLog('NINP? %d' % port, bCheckError=False))
        nbytes_waiting_old = 0

        while (nbytes_waiting_old != nbytes_waiting) or (nbytes_waiting == 0):
            nbytes_waiting_old = nbytes_waiting
            nbytes_waiting = int(self.askAndLog('NINP? %d' % port, bCheckError=False))
            self.wait(0.1)
        
        self.writeAndLog('RAWN? %d, %d' % (port, nbytes_waiting), bCheckError=False)
        value = float(self.read(nbytes_waiting).decode().strip('\r\n'))
        
        return value