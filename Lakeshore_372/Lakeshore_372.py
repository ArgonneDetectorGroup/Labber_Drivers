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
        elif qname in inset_quants:
            vals_list = []
            for qix, q in enumerate(inset_quants):

                #Might as well update the rest of them even though they weren't
                #explicitly asked for...
                q_datatype =  self.getQuantity('%s %s'%(q, qchannel)).datatype

                if q == qname:
                    if q_datatype == 2:
                        val = quant.getCmdStringFromValue(value)
                    elif q_datatype == 0:
                        val = '%d'%value
                else:
                    if q_datatype == 2:
                        #COMBOBOX index
                        
                        val = self.getQuantity('%s %s'%(q, qchannel)).getCmdStringFromValue()
                    elif q_datatype == 0:
                        #DOUBLE --> String
                        val = '%d'%self.getValue('%s %s'%(q, qchannel))
                
                vals_list.append(val)

            self.writeAndLog('INSET %s,%s'%(qchannel, ','.join(vals_list)))
        
        elif qname in intype_quants:
            vals_list = []
            for qix, q in enumerate(intype_quants):

                #Might as well update the rest of them even though they weren't
                #explicitly asked for...
                q_datatype =  self.getQuantity('%s %s'%(q, qchannel)).datatype

                if q == qname:
                    if q_datatype == 2:
                        val = quant.getCmdStringFromValue(value)
                    elif q_datatype == 0:
                        val = '%d'%value
                else:
                    if q_datatype == 2:
                        #COMBOBOX index
                        
                        val = self.getQuantity('%s %s'%(q, qchannel)).getCmdStringFromValue()
                    elif q_datatype == 0:
                        #DOUBLE --> String
                        val = '%d'%self.getValue('%s %s'%(q, qchannel))
                
                vals_list.append(val)

            self.writeAndLog('INTYPE %s,%s'%(qchannel, ','.join(vals_list)))

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
        elif qname in intype_quants:
            #Get the string of values back from the Lakeshore
            query = self.askAndLog('INTYPE? %s'%qchannel, bCheckError=False).split(',')

            #Plug them all into the right place
            for qix, quant in enumerate(intype_quants):

                #Might as well update the rest of them even though they weren't
                #explicitly asked for...
                self.setValue('%s %s'%(quant, qchannel), query[qix])

                #Set the "asked for" value here so it gets returned properly
                if quant == qname:
                    value = query[qix]

        elif qname in inset_quants:
            #Get the string of values back from the Lakeshore
            query = self.askAndLog('INSET? %s'%qchannel, bCheckError=False).split(',')
            # assert False, query

            #Plug them all into the right place
            for qix, quant in enumerate(inset_quants):

                #Might as well update the rest of them even though they weren't
                #explicitly asked for...
                self.setValue('%s %s'%(quant, qchannel), query[qix])

                #Set the "asked for" value here so it gets returned properly
                if quant == qname:
                    value = query[qix]
        else:
            value = VISA_Driver.performGetValue(self, quant, options)
        return value