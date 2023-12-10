# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 16:30:26 2023

@author: edgar
"""

# <codecell> Libraries
import pandas as pd 
import time
from scipy.spatial import distance
import numpy as np
import math
import random
import sys
from hcndp import menu
from hcndp import network_data
from hcndp.network_data import _I,_J,_K,_archivo 


# <codecell> Execution

network=network_data.Network(_I,_J,_K,_archivo)

menu.show_menu_main(network)
    