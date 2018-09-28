LABBER_PATH = '/Program Files (x86)/Labber/Script/'
LABBER_SERVER = 'localhost'

VOLTAGE_SOURCE = 'Stanford Research SIM 960 PID Controller'
V_QUANT = 'Manual Output'
V_GAIN = 2

HEAT_SWITCH = 'HPD Heat Switch'

MAG_CYCLE_RELAY = 'Mag Cycle Relay'

SAFE_RAMP_RATE = 5.6e-3 #Amps/second

# LABBER_PATH should be added to PYTHON_PATH already. If not, uncomment the next two lines
# import sys
# sys.path.append(LABBER_PATH)

import threading
import time
import datetime
import Labber as lab
import InstrumentDriver

def get_safe_ramp_rate_V(magtime, target, resistance):
    """magtime in seconds, target is delta in amps"""
    
    
    safe_rate = SAFE_RAMP_RATE*resistance #A/second * R = V/s
    target_V = target*resistance
    ask_rate = target_V/magtime

    if safe_rate > ask_rate:
        safe_rate = ask_rate
    
    #This is in volts/seconds
    return safe_rate/V_GAIN




class Driver(InstrumentDriver.InstrumentWorker):

    def check_if_sweeping(self):
        val1 = self.source.getValue(V_QUANT)
        self.wait(0.5)
        val2 = self.source.getValue(V_QUANT)

        val1 = int(val1*1000)
        val2 = int(val2*1000)

        if val1 == val2:
            isSweeping = False
        else:
            isSweeping = True

        return isSweeping


    def startMag(self):
        
        if self.resistance is None:
            self.resistance = float(self.getCmdStringFromValue('Resistor'))
        target_I = self.getValue('Mag Current')
        target_V = target_I*self.resistance / V_GAIN

        #Set this for easy access later
        self.ramp_target = target_I
        
        magTime = self.getValue('Mag Time')*60
        ramprate = get_safe_ramp_rate_V(magTime, target_I, self.resistance)
        
        waitTime = max(target_V/ramprate, magTime)

        self.setValue('Status', 'Magging up!')

        return (target_V, ramprate, waitTime)

    def startDemag(self):
        
        if self.resistance is None:
            self.resistance = float(self.getCmdStringFromValue('Resistor'))
        
        current_V = self.source.getValue(V_QUANT)
        current_I = current_V*V_GAIN/self.resistance
        target_V = 0

        self.ramp_target = 0

        magTime = self.getValue('Demag Time')*60
        ramprate = get_safe_ramp_rate_V(magTime, current_I, self.resistance)

        waitTime = max(current_V/ramprate, magTime)
        
        self.setValue('Status', 'Magging down!')
        
        return (target_V, ramprate, waitTime)

    def finishMessage(self):
        self.resistance = None
        self.ramp_target = None
        self.setValue('Status', 'Mag Cycle finished at %s'%str(datetime.datetime.now()))


    def rampMag(self, waitTime=0, isFirstCall=True, precallback=None, postcallback=None):
        if isFirstCall:
            #Figure out the ramp rate and start going
            
            assert precallback is not None, "Must pass precallback for first call!"         
            target_V, ramprate, waitTime = precallback()

            self.source.setValue(V_QUANT, target_V, rate=ramprate, wait_for_sweep=False)
        
        if waitTime - 10 > 0:
            check_start = time.time()
            current_value = self.source.getValue(V_QUANT)*V_GAIN/self.resistance
            message = 'Ramping mag to %f A. Now at: %f A. Time left: %f minutes.'%(self.ramp_target, current_value, waitTime/60)
            self.setValue('Status', message)
            
            waitTime-=10
            delay = time.time()-check_start
            
            self.timer = threading.Timer(10-delay, self.rampMag, args = [waitTime, False, None, postcallback])
            self.timer.start()
            
        else:
            self.wait(abs(waitTime))
            while self.check_if_sweeping():
                self.setValue('Status', 'Almost done ramping. < 1 minute.')

            if postcallback is not None:
                postcallback()

    def startSoak(self, waitTime=0, isFirstCall=True):
        check_start = time.time()
        if isFirstCall:
            waitTime = self.getValue('Soak Time')*60*60
            if self.getValue('Heat Switch Start Position') == 'Closed':
                hs_cycle_start = time.time()
                self.setValue('Status', 'Cycling heat switch before soak')
                self.heatSwitch.setValue('Heat Switch', 'Open')
                self.heatSwitch.setValue('Heat Switch', 'Closed')
                waitTime -= (time.time() - hs_cycle_start)

        if waitTime - 10 >= 0:
            self.setValue('Status', 'Soaking: %f hours remaining'%(waitTime/3600))
            waitTime -= 10
            delay = time.time()-check_start
            self.timer = threading.Timer(10-delay, self.startSoak, args = [waitTime, False])
            self.timer.start()
        else:
            self.setValue('Status', 'Opening heat switch')
            self.heatSwitch.setValue('Heat Switch', 'Open')
            self.rampMag(precallback=self.startDemag, postcallback=self.finishMessage)


    def performOpen(self, options={}):
        """Try to connect to the instruments. Start it up if necessary."""

        self.client = lab.connectToServer(LABBER_SERVER)
        instruments = self.client.getListOfInstruments()

        for hardware, config in instruments:
            if hardware == VOLTAGE_SOURCE:
                self.source = self.client.connectToInstrument(VOLTAGE_SOURCE, dict(name=config['name']))
            elif hardware == HEAT_SWITCH:
                self.heatSwitch = self.client.connectToInstrument(HEAT_SWITCH, dict(name=config['name']))
            elif hardware == MAG_CYCLE_RELAY:
                self.relay = self.client.connectToInstrument(MAG_CYCLE_RELAY, dict(name=config['name']))
        
        instruments = [self.source, self.heatSwitch, self.relay]

        for inst in instruments:
            assert inst is not None, "ERROR: Could not find instrument!"
            
            if not inst.isRunning():
                inst.startInstrument()
            
            assert inst.isRunning() == True, "ERROR: Cannot start instrument"

        self.timer = None
        self.ramp_target = None
        self.resistance = None

        self.setValue('Status', 'Ready to Cycle')

    def performClose(self, options = {}):
        self.setValue('Status', 'Shutting down driver and killing ramps')
        #Kill off the timer
        if self.timer is not None:
            self.timer.cancel()

        #Stop any sweeps that are currently happening
        self.source.abortCurrentOperation()

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        if quant.name == 'Run Cycle':
            #Do nothing if a mag cycle is already running
            if (self.timer is None) or (self.timer.is_alive() == False):
                #Start fresh from zero every time
                assert self.source.getValue(V_QUANT) == 0.0, "Must start mag cycle at zero current"

                #Check to make sure the relay switch is in the desired position
                relay_position = self.relay.getValue('Relay Position')
                resistor = self.getValue('Resistor')
                if resistor == 'Mag Cycle (0.99)':
                    assert (relay_position == 'Mag Cycle'), "Set relay properly before running"
                else:
                    assert( relay_position == 'Regulate'), "Set relay properly before running"
                    message = 'Verify manual switches are set to: %s! Enter 1 to Abort: ' % resistor
                    abort = self.getValueFromUserDialog(value=0, text=message, title='Warning!')

                    if abort:
                        return value

                #Set this now for the duration of the cycle
                self.resistance = float(self.getCmdStringFromValue('Resistor'))

                self.setValue('Status', 'Setting heat switch')
                self.heatSwitch.setValue('Heat Switch', self.getValue('Heat Switch Start Position'))

                start_delay_secs = self.getValue('Start Delay Time')*60*60
                self.timer = threading.Timer(start_delay_secs, self.rampMag, 
                                                kwargs = dict(precallback=self.startMag, postcallback=self.startSoak))
                self.timer.start()
                self.setValue('Status', 'Mag Cycle scheduled for %f seconds from now'%start_delay_secs)
        
        elif quant.name == 'Abort Cycle':
            self.setValue('Status', 'Aborting Cycle')
            if self.timer is not None:
                if self.timer.is_alive():
                    self.timer.cancel()
                    self.timer = None
                    self.setValue('Status', 'Cycle Aborted, mag sweep stopped at %s'%str(datetime.datetime.now()))
            
            if self.check_if_sweeping():
                self.source.abortCurrentOperation()

            self.resistance = None
            self.ramp_target = None

        return value

            
            
