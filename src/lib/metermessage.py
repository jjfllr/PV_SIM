import numpy as np
import json

class MeterMessage():
    origin: str
    time: np.float64
    consumption: np.float64

    def __repr__(self):
        return "{}: {}".format(self.type, self.__dict__)

    def __init__(self, origin: str='default', time: np.float64=0.0, consumption:np.float64=0.0):
        self.origin = origin
        self.time = time
        self.consumption = consumption

    def to_json(self):
        d = {'Type': 'MeterMessage'}
        d.update(self.__dict__)
        return json.dumps(d)

    def __eq__(self, other):
        if isinstance(other, MeterMessage):
            return self.origin == other.origin and np.isclose(self.time, other.time) and np.isclose(self.consumption, other.consumption)
        return False

    @classmethod
    def from_json(cls, data):
        y = json.loads(data)

        if 'Type' not in y:
            raise TypeError('Not a Valid MeterMessage')
        if y['Type'] != 'MeterMessage':
            raise TypeError('Not a Valid MeterMessage')
        if 'origin' not in y:
            raise LookupError('origin not found in JSON')
        if 'time' not in y:
            raise LookupError('time not found in JSON')
        if 'consumption' not in y:
            raise LookupError('consumption not found in JSON')

        return MeterMessage(origin=y['origin'], time=y['time'], consumption=y['consumption'])


def test_message():
    m = MeterMessage(origin="House", time=24, consumption=9001)
    print(m)

    j = m.to_json()
    print('json :', j)
    y = json.loads(j)
    print('dict :', y)
    n = MeterMessage.from_json(j)
    print('Obj  :', n)


if __name__ == '__main__':
    exit(0)
