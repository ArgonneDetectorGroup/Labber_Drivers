from VISA_Driver import VISA_Driver

class Driver(VISA_Driver):
    """ This class re-implements the VISA driver"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)

    def performClose(self, bError=False, options={}):
        """Perform the close instrument connection operation"""
        # calling the generic VISA class to close communication
        VISA_Driver.performClose(self, bError, options=options)
        # do additional cleaning up code here...
        

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""

        #The order of these two lists is super important!!! Don't change it!
        inset_quants = ['Status', 'Dwell Time', 'Pause Time', 'Calibration Curve', 'Temperature Coefficient']
        intype_quants = ['Excitation Mode', 'Excitation Value', 'Autorange', 'Range', 'Excitation Status', 'Units']

        #Try and parse the quantity name to get the quant type and channel number
        for name in inset_quants+intype_quants:
            if quant.name.startswith(name):
               qname = name
               qchannel = quant.name.split(name+' ')[-1]
               break
            else:
                qname = quant.name

        if qname == 'Active Channel':
            self.writeAndLog('SCAN %s, 0'%value, bCheckError=False)

            #Wait three seconds for instrument to settle
            for x in range(100):
                    self.wait(0.03)
                    self.reportProgress(x/100)
        
        elif qname in inset_quants+intype_quants:
            if qname in inset_quants:
                cmd = 'INSET'
                qix = inset_quants.index(qname)
            elif qname in intype_quants:
                cmd = 'INTYPE'
                qix = intype_quants.index(qname)

            vals_list = self.askAndLog('%s? %s'%(cmd, qchannel), bCheckError=False).split(',')

            #Datatype 2 is COMBO
            if quant.datatype == 2:
                new_val = quant.getCmdStringFromValue(value)
            #Datatype 0 is DOUBLE, but for these two commands it's really an INT
            elif quant.datatype == 0:
                new_val = '%d'%value
            #None of the inset/intype commands should be any other datatype, so raise error
            else:
                raise ValueError("Unknown data type")

            vals_list[qix] = new_val

            self.writeAndLog('%s %s,%s'%(cmd, qchannel, ','.join(vals_list)))

        else:
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)

        return value

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""

        active_channel_quants = ['Temperature', 'Quadrature', 'Resistance', 'Power']
        
        #The order of these two lists is super important!!! Don't change it!
        inset_quants = ['Status', 'Dwell Time', 'Pause Time', 'Calibration Curve', 'Temperature Coefficient']
        intype_quants = ['Excitation Mode', 'Excitation Value', 'Autorange', 'Range', 'Excitation Status', 'Units']

        #Try and parse the quantity name to get the quant type and channel number
        for name in inset_quants+intype_quants:
            if quant.name.startswith(name):
               qname = name
               qchannel = quant.name.split(name+' ')[-1]
               break
            else:
                qname = quant.name

        if qname in active_channel_quants:

            current_channel = self.readValueFromOther('Active Channel')

            cmd = quant.get_cmd.replace('<*>', current_channel)
            value = self.askAndLog(cmd, bCheckError=False)
        
        elif qname == 'Active Channel':
            value = self.askAndLog('SCAN?', bCheckError=False).split(',')[0]
        
        elif qname in inset_quants+intype_quants:
            if qname in inset_quants:
                cmd = 'INSET'
                qix = inset_quants.index(qname)
            elif qname in intype_quants:
                cmd = 'INTYPE'
                qix = intype_quants.index(qname)


            vals_list = self.askAndLog('%s? %s'%(cmd, qchannel), bCheckError=False).split(',')

            #There is really no reason not to set all of the other ones here, too, but it isn't
            #strictly necessary, as logger or anything else will just ask for them again anyhow
            value = vals_list[qix]

        else:
            value = VISA_Driver.performGetValue(self, quant, options)
        return value