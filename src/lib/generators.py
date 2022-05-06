# Methods to simulate household with power consumption between values
import random
import numpy as np
from perlin_noise import PerlinNoise

################################################
# Parameters
STEP = 1
SEED = 39

METER_MIN_CONSUMPTION = 0.0
METER_MAX_CONSUMPTION = 9000.0

PV_DAWN = 5.5
PV_DUSK = 21.0
PV_DAWN_TIME = 2.5
PV_DUSK_TIME = 1.0
PV_HOUR_MAX_VOLT = 14.0

PV_VOLTS_NO_SUN = 0.0
PV_VOLTS_FULL_RISE = 300.0
PV_VOLTS_BEGIN_FALL = 200.0
PV_VOLTS_MAX = 3300.0

################################################
# PV equations
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


class Meter:
    p_noise = PerlinNoise(octaves=0.5, seed=SEED)
    random_seed = random.Random(SEED)

    def __init__(self, seed=SEED, octaves=0.5):
        self.p_noise = PerlinNoise(octaves=octaves, seed=seed)
        self.random_seed = random.Random(seed)

    def get_consumption(self, time):
        noise = STEP*self.random_seed.randrange(-1, 2)
        # Using PerlinNoise in order to create a smooth Curve
        # PerlinNoise is generated between -1 and 1, so we escale it to be between our values
        next = (self.p_noise(time) + 1) * ((METER_MAX_CONSUMPTION - METER_MIN_CONSUMPTION)/2) + noise
        if next <= 0.0:
            return 0.0
        if next >= 9000.0:
            return 9000.0
        return next


class Photovoltaic:
    random_seed = random.Random(SEED)

    def __init__(self, seed=SEED):
        self.random_seed = random.Random(seed)

    def get_power(self, time):
        # This function should be cyclic with a 24 hour period
        t = time % 24.0

        # before dawn and after dusk we have no light
        if t <= PV_DAWN or t >= PV_DUSK:
            return PV_VOLTS_NO_SUN

        noise = STEP*self.random_seed.randrange(-1, 2)
        # after dawn for DAWN_TIME hours after dawn we see a linear component
        if t <= (PV_DAWN + PV_DAWN_TIME):
            #  Y = mX + a
            tmp = PV_DAWN_CONST[0] * t + PV_DAWN_CONST[1] + noise
            return tmp if tmp > 0 else 0.0

        # # before dusk, for DUSK_TIMEhours we see a linear component
        if t >= (PV_DUSK - PV_DUSK_TIME):
            tmp = PV_DUSK_CONST[0] * t + PV_DUSK_CONST[1] + noise
            return tmp if tmp > 0 else 0.0

        # in between we see a cuadratic component
        return PV_DAY_CONST[0] * t**2 + PV_DAY_CONST[1] * t + PV_DAY_CONST[2] + noise


def test():
    from matplotlib import pyplot
    seed = 39
    meter = Meter(seed=seed, octaves=0.1)
    pv = Photovoltaic(seed=seed)

    hours = 24
    tm = np.linspace(0.0, hours - 1/(60*60), num=hours*60*60 - 1)

    c = np.array([meter.get_consumption(t) for t in tm])
    p = np.array([pv.get_power(t) for t in tm])

    pyplot.figure(figsize=(15, 10))
    pyplot.grid(color='k', linestyle='-', linewidth=1, alpha=0.3)
    pyplot.plot(tm, c, color='r', alpha=0.5, label="Consumption")
    pyplot.plot(tm, p, color='g', alpha=1, label="Generation")
    pyplot.plot(tm, p - c, color='orange', alpha=0.7, label="Delta")
    pyplot.xlabel("Hour [HH]")
    pyplot.ylabel("Power [W]")
    pyplot.legend(loc='upper right')


if __name__ == '__main__':
    test()
