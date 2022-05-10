# File containing different configuration parameters for models.

import numpy as np


################################################
# Randomizer Parameters
NOISE_AMPLITUDE = 1
SEED = 39

# Parameters for modeling
# values in Watt
METER_MIN_CONSUMPTION = 0.0
METER_MAX_CONSUMPTION = 9000.0
PV_VOLTS_NO_SUN = 0.0
PV_VOLTS_FULL_RISE = 300.0
PV_VOLTS_BEGIN_FALL = 200.0
PV_VOLTS_MAX = 3300.0
# Times in secods
PV_DAWN = 5.5 * 60 * 60
PV_DUSK = 21.0 * 60 * 60
PV_DAWN_TIME = 2.5 * 60 * 60
PV_DUSK_TIME = 1.0 * 60 * 60
PV_HOUR_MAX_VOLT = 14.0 * 60 * 60

################################################
# Modeling Equations
# Dawn curve calculation
PV_DAWN_CONST = np.polyfit(
        x=[PV_DAWN, PV_DAWN+PV_DAWN_TIME],
        y=[PV_VOLTS_NO_SUN, PV_VOLTS_FULL_RISE],
        deg=1)
# Dusk Curve calculator
PV_DUSK_CONST = np.polyfit(
        x=[PV_DUSK - PV_DUSK_TIME, PV_DUSK],
        y=[PV_VOLTS_BEGIN_FALL, PV_VOLTS_NO_SUN],
        deg=1)
# Rest of the day curve
PV_DAY_CONST = np.polyfit(
        x=[PV_HOUR_MAX_VOLT, PV_DAWN+PV_DAWN_TIME, PV_DUSK-PV_DUSK_TIME],
        y=[PV_VOLTS_MAX, PV_VOLTS_FULL_RISE, PV_VOLTS_BEGIN_FALL],
        deg=2)

################################################
# Connection Data
HOST = 'localhost'
QUEUE = 'Household_1'
ROUTING_KEY = 'Household_1'
EXCHANGE = ''
PLAINTEXT_USER = 'guest'
PLAINTEXT_PASS = 'guest'
