from VISA_Driver import VISA_Driver

#Some necessary globals
#The order of these lists is super important!!! Don't change it!

SPECIAL_QUANTS = {
    'INSET':['Status', 'Dwell Time', 'Pause Time', 'Calibration Curve', 'Temperature Coefficient'],
    'INTYPE':['Excitation Mode', 'Excitation Value', 'Autorange', 'Range', 'Excitation Status', 'Units'],
    'FILTER':['Filter Status', 'Filter Settle Time', 'Filter Window']
}

def parse_qname(fullname):
    '''Discover and return the name and channel of the desired quantity'''
    foundName = False
    for _cmd, _quants in SPECIAL_QUANTS.items():
        for name in _quants:
            if fullname.startswith(name):
               qname = name
               qchannel = fullname.split(name+' ')[-1]
               foundName = True
               break
            else:
                qname = fullname
                qchannel = None
        if foundName == True:
            break

    return qname, qchannel

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

        #Try and parse the quantity name to get the quant type and channel number
        qname, qchannel = parse_qname(quant.name)

        if qname == 'Active Channel':
            ch_num = quant.getCmdStringFromValue(value)

            self.writeAndLog('SCAN %s, 0'%ch_num, bCheckError=False)

            #Wait three seconds for instrument to settle
            for x in range(100):
                    self.wait(0.03)
                    self.reportProgress(x/100)
        
        elif qchannel is not None:

            #Grab the right command and index for the quantity
            for _cmd, _quants in SPECIAL_QUANTS.items():
                if qname in _quants:
                    cmd = _cmd
                    qix = _quants.index(qname)
                    break

            vals_list = self.askAndLog('%s? %s'%(cmd, qchannel), bCheckError=False).split(',')

            #Datatype 2 is COMBO
            if quant.datatype == 2:
                new_val = quant.getCmdStringFromValue(value)
            #Datatype 0 is DOUBLE, but for these commands it's really an INT
            elif quant.datatype == 0:
                new_val = '%d'%value
            #None of the inset/intype commands should be any other datatype, so raise error
            else:
                raise ValueError("Unknown data type")

            vals_list[qix] = new_val

            #If the user tries to set the resistance range of any channel
            #or the range/value of the control channel, turn off Autorange
            if (qname == 'Range') or (quant.name == 'Excitation Value A'):
                vals_list[2] = '0'

            self.writeAndLog('%s %s,%s'%(cmd, qchannel, ','.join(vals_list)))

            #Give the box a little time to do its thing
            self.wait(0.1)

            #Double check that anything actually changed. Not all options are always available
            #depending on setting. Like, if Autorange is on, then you can't set excitations.
            value = self.performGetValue(quant, options={})

        else:
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)

        return value

    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""

        active_channel_quants = ['Temperature', 'Quadrature', 'Resistance', 'Power']

        #Try and parse the quantity name to get the quant type and channel number
        qname, qchannel = parse_qname(quant.name)

        if qname in active_channel_quants:
        #These are really just a convenience for remote operation
        #In any real measurements one would use the appropriate channel X quants
            current_channel = self.readValueFromOther('Active Channel')

            cmd = quant.get_cmd.replace('<*>', current_channel)
            value = self.askAndLog(cmd, bCheckError=False)
        
        elif qname == 'Active Channel':
            value = self.askAndLog('SCAN?', bCheckError=False).split(',')[0]
        
        elif qchannel is not None:

            for _cmd, _quants in SPECIAL_QUANTS.items():
                if qname in _quants:
                    cmd = _cmd
                    break

            vals_list = self.askAndLog('%s? %s'%(cmd, qchannel), bCheckError=False).split(',')

            #There is really no reason not to set all of the other ones here, too.
            for val, q in zip(vals_list, SPECIAL_QUANTS[cmd]):
                _qname = '%s %s'%(q, qchannel)
                
                #Have to do a check here because not all the quants exist for channel A
                if _qname in self.dQuantities.keys():
                    self.setValue(_qname, val)

                #Make sure the function still resturns the right thing
                if _qname == quant.name:
                    value = val

        else:
            value = VISA_Driver.performGetValue(self, quant, options)
        return value