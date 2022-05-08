# Methods to simulate household with power consumption between values
import random
from perlin_noise import PerlinNoise
import src.lib.configurations as configs


class Meter:
    p_noise = PerlinNoise(octaves=0.0001, seed=configs.SEED)
    random_seed = random.Random(configs.SEED)

    def __init__(self, id='', seed=configs.SEED, octaves=0.5):
        self.id = str(id)
        self.p_noise = PerlinNoise(octaves=octaves, seed=seed)
        self.random_seed = random.Random(seed)

    def get_consumption(self, time):
        noise = configs.STEP*self.random_seed.randrange(-1, 2)
        # Using PerlinNoise in order to create a smooth Curve
        # PerlinNoise is generated between -1 and 1, so we escale it to be between our values
        next = (self.p_noise(time) + 1) * ((configs.METER_MAX_CONSUMPTION - configs.METER_MIN_CONSUMPTION)/2) + noise
        if next <= 0.0:
            return 0.0
        if next >= 9000.0:
            return 9000.0
        return next


class Photovoltaic:
    random_seed = random.Random(configs.SEED)

    def __init__(self, id='', seed=configs.SEED):
        self.id = str(id)
        self.random_seed = random.Random(seed)

    def get_power(self, time):
        # This function should be cyclic with a 24 hour period
        t = time % (24.0*60.0*60.0)

        # before dawn and after dusk we have no light
        if t <= configs.PV_DAWN or t >= configs.PV_DUSK:
            return configs.PV_VOLTS_NO_SUN

        noise = configs.STEP*self.random_seed.randrange(-1, 2)
        # after dawn for DAWN_TIME hours after dawn we see a linear component
        if t <= (configs.PV_DAWN + configs.PV_DAWN_TIME):
            #  Y = mX + a
            tmp = configs.PV_DAWN_CONST[0] * t + configs.PV_DAWN_CONST[1] + noise
            return tmp if tmp > 0 else 0.0

        # # before dusk, for DUSK_TIMEhours we see a linear component
        if t >= (configs.PV_DUSK - configs.PV_DUSK_TIME):
            tmp = configs.PV_DUSK_CONST[0] * t + configs.PV_DUSK_CONST[1] + noise
            return tmp if tmp > 0 else 0.0

        # in between we see a cuadratic component
        return configs.PV_DAY_CONST[0] * t**2 + configs.PV_DAY_CONST[1] * t + configs.PV_DAY_CONST[2] + noise


if __name__ == '__main__':
    exit(0)
