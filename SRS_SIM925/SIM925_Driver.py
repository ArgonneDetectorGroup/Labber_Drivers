#Add the parent directory to the path to expose common_lib
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import sys
sys.path.append(parent_dir)

from common_lib.SIM9XX_Driver import SIM9XX_Driver

class Driver(SIM9XX_Driver):
    """ This class re-implements the SIM9XX driver"""

    pass