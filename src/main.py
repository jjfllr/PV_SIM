import pika
import json
import numpy as np
from src.lib.generators import Meter, Photovoltaic

import threading
import time

mutex = threading.Lock()

class BrokerConfigs(object):
    def __init__(self, queue='default', host='localhost', routing_key='default', exchange='', credentials=pika.PlainCredentials('guest', 'guest')):
        self.credentials = credentials
        self.queue = str(queue)
        self.host = str(host)
        self.routing_key = str(routing_key)
        self.exchange = str(exchange)


class ThreadHousehold(object):

    def __init__(self, stop_event, meter=Meter(), brokerconfigs=BrokerConfigs()):
        self.stop_event = stop_event
        self.meter = meter

        self.config = brokerconfigs
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.config.host, credentials=self.config.credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config.queue)

        thread = threading.Thread(target=self._run)
        thread.start()

    def _publish(self, message=''):
        self.channel.basic_publish(exchange=self.config.exchange, routing_key=self.config.routing_key, body=message)
        print('message published')

    def _run(self):
        global mutex
        print('H Started')
        while not self.stop_event.is_set():
            with mutex:
                print("thread_household: ",  self.meter.get_consumption(15))
                self._publish(message=">>Hello from Household<<" )
            time.sleep(1)
        print('H Finished')
        self.connection.close()


class ThreadPvGenerator(object):
    # queue = {}

    def __init__(self, stop_event, photovoltaic=Photovoltaic(), brokerconfigs=BrokerConfigs()):
        self.photovoltaic = photovoltaic
        self.stop_event = stop_event

        self.config = brokerconfigs
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.config.host, credentials=self.config.credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config.queue)

        thread = threading.Thread(target=self._run)
        thread.setDaemon(True)
        thread.start()

    def _run(self):
        global mutex
        print("PV Start")
        self.channel.basic_consume(queue=self.config.queue, on_message_callback=self._on_request, auto_ack=True)
        while not self.stop_event.is_set():
            with mutex:
                self.connection.process_data_events()
                # print(self.queue)
            time.sleep(0.1)
        self.connection.close()
        print("PV finished")

    def _on_request(self, ch, method, properties, body):
        # self.queue[properties.correlation_id] = body
        print(body)


class MeterMessage():
    type = 'MeterMessage'
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


    # x = json.dumps({'Type': 'MeterMssage', 'Origin': '1', 'Time': '2', 'Watt': '3'})
    # x = MeterMessage.from_json(x)
    #
    # print(x)


def main():

    print("Main thread created")
    seed=39
    meter = Meter(seed=seed, octaves=0.5)
    photovoltaic = Photovoltaic(seed=seed)
    household_event = threading.Event()
    photovoltaic_event = threading.Event()

    broker_config = BrokerConfigs(queue='household_1', host='localhost', routing_key='household_1', exchange='')

    ThreadHousehold(stop_event=household_event, meter=meter, brokerconfigs=broker_config)
    ThreadPvGenerator(stop_event=photovoltaic_event, photovoltaic=photovoltaic, brokerconfigs=broker_config)

    # create 2 threads
    # Household -> Meter, send regular messages
    # PV -> Photovoltaic, receives regular messagesn

    while True:
        cont = input("Continue (y)/(n)")
        if cont[0] == 'n':
            household_event.set()
            photovoltaic_event.set()
            break
        time.sleep(5)

    print("Main Finished")


if __name__ == '__main__':
    main()
