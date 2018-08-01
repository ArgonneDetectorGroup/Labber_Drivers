from VISA_Driver import VISA_Driver

class Driver(VISA_Driver):
    """ This class re-implements the VISA driver"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)
        # do additional initialization code here...
        pass

    def performClose(self, bError=False, options={}):
        """Perform the close instrument connection operation"""
        # calling the generic VISA class to close communication
        VISA_Driver.performClose(self, bError, options=options)
        # do additional cleaning up code here...
        pass

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""

        if quant.name == 'Channel':
            self.writeAndLog('SCAN %s, 0'%value, bCheckError=False)

            #Wait three seconds for instrument to settle
            for x in range(100):
                    self.wait(0.03)
                    self.reportProgress(x/100)
        
        elif quant.name == 'Frequency':
            self.writeAndLog('FREQ %s, %s'%(self.getValue('Channel'), value))
        else:
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)

        return value

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""

        cmd_dict = {'Temperature' : 'KRDG?',
                    'Quadrature': 'QRDG?',
                    'Resistance' : 'SRDG?',
                    'Power' : 'RDGPWR?',
                    'Frequency' : 'FREQ?'}

        if quant.name in cmd_dict.keys():

            desired_channel = self.getValue('Channel')
            current_channel = self.readValueFromOther('Channel')
            
            if int(current_channel) != int(desired_channel):
                for x in range(100):
                    self.wait(0.03)
                    self.reportProgress(x/100)
                    
            cmd = '%s %s'%(cmd_dict[quant.name], self.readValueFromOther('Channel'))
            value = self.askAndLog(cmd, bCheckError=False)
        elif quant.name == 'Channel':
            value = self.askAndLog('SCAN?', bCheckError=False).split(',')[0]
        else:
            value = VISA_Driver.performGetValue(self, quant, options)
        return value