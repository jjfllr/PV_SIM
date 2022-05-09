import unittest
import json
import numpy as np


import src.lib.generators as generators
import src.lib.metermessage as metermessage
import src.lib.configurations as configs

def test_graph_generator():
    from matplotlib import pyplot
    meter = generators.Meter(seed=configs.SEED, octaves=0.00005)
    pv = generators.Photovoltaic(seed=configs.SEED)

    seconds = 72*60*60 # 24 hours in seconds
    tm = np.linspace(0, seconds - 1, num=seconds - 1)

    c = np.array([meter.get_consumption(t) for t in tm])
    p = np.array([pv.get_power(t) for t in tm])

    pyplot.figure(figsize=(15, 10))
    pyplot.grid(color='k', linestyle='-', linewidth=1, alpha=0.3)
    pyplot.plot(tm, c, color='r', alpha=0.5, label="Consumption")
    pyplot.plot(tm, p, color='g', alpha=1, label="Generation")
    pyplot.plot(tm, p - c, color='orange', alpha=0.7, label="Delta")
    pyplot.xlabel("secods [s]")
    pyplot.ylabel("Power [W]")
    pyplot.legend(loc='upper right')


class TestMeter(unittest.TestCase):

    def test_message_encoding(self):

        o = 'house'
        t = 23.5 * 60 * 60
        c = 8769.12
        m = metermessage.MeterMessage(origin=o, time=t, consumption=c)
        j = m.to_json()
        self.assertEqual(j, json.dumps({'Type': 'MeterMessage', 'origin': o, 'time': t, 'consumption': c}))

    def test_message_decoding(self):
        o = 'house'
        t = 23.5 * 60 * 60
        c = 8769.12
        m = metermessage.MeterMessage(origin=o, time=t, consumption=c)
        j = m.to_json()
        j = metermessage.MeterMessage.from_json(j)

        self.assertEqual(m, j)



if __name__ == '__main__':
    unittest.main()
    # test_graph_generator()
