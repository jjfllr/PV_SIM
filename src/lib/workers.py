import pika
import numpy as np
from src.lib.generators import Meter, Photovoltaic
from src.lib.metermessage import MeterMessage

import threading
import time


class ThreadTimer(object):
    def __init__(self, init_time=0, duration=3600):
        self.mutex = threading.Lock()
        self.duration = duration
        self.init_time = init_time
        self.time = init_time

    def end(self):
        with self.mutex:
            return self.duration + self.init_time <= self.time

    def increment_time(self, interval=1):
        with self.mutex:
            self.time += interval

    def get_time(self):
        self.mutex
        with self.mutex:
            return self.time


class BrokerConfigs(object):
    def __init__(self, queue='default', host='localhost', routing_key='default', exchange='', credentials=pika.PlainCredentials('guest', 'guest')):
        self.credentials = credentials
        self.queue = str(queue)
        self.host = str(host)
        self.routing_key = str(routing_key)
        self.exchange = str(exchange)


class ThreadHousehold(object):
    def __init__(self, start_event, stop_event, timer: ThreadTimer=None, meter=Meter(), brokerconfigs=BrokerConfigs()):
        self.start_event = start_event
        self.stop_event = stop_event
        self.meter = meter

        self.timer = timer

        self.config = brokerconfigs
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.config.host, credentials=self.config.credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config.queue)

        thread = threading.Thread(target=self._run)
        thread.start()

    def _publish(self, message=''):
        self.channel.basic_publish(exchange=self.config.exchange, routing_key=self.config.routing_key, body=message)

    def _run(self):
        while not self.start_event.is_set():
            time.sleep(0.01)

        print('Household thread Started')

        t_last = 0

        while not self.stop_event.is_set():
            if self.timer is not None:
                t = self.timer.get_time()
            else:
                t = int(time.time())
                # Only send message if 2 seconds has passed
            if t_last + 2 <= t:
                m = MeterMessage(origin=self.meter.id, time=t, consumption=self.meter.get_consumption(t))
                self._publish(message=str(m.to_json()))
                t_last = t
            if self.timer is not None:
                self.timer.increment_time(2)

            time.sleep(0.01)

        print('Household thread Finished')

        self.connection.close()


class ThreadPvGenerator(object):

    def __init__(self, start_event, stop_event, photovoltaic=Photovoltaic(), brokerconfigs=BrokerConfigs(), logfile=None):
        self.start_event = start_event
        self.stop_event = stop_event

        if logfile is not None:
            self.logfile = open(logfile, 'w')

            self.logfile.write(f"{'Time':>12} [s] | {'Meter Name':^10}{'Consumption':^17} [W] |{'PV Name':^10}{'Generation':^20} [kW] |{'Netto':^20} [kW]\n")
        else:
            self.logfile = None

        self.photovoltaic = photovoltaic

        self.config = brokerconfigs
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.config.host, credentials=self.config.credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config.queue)

        thread = threading.Thread(target=self._run)
        thread.setDaemon(True)
        thread.start()

    def _run(self):
        while not self.start_event.is_set():
            time.sleep(0.01)

        print("PV Thread Start")

        self.channel.basic_consume(queue=self.config.queue, on_message_callback=self._on_request, auto_ack=True)
        while not self.stop_event.is_set():
            self.connection.process_data_events()
            time.sleep(0.1)
        self.connection.close()
        print("PV thread finished")

    def _on_request(self, ch, method, properties, body):
        # self.queue[properties.correlation_id] = body
        m = MeterMessage.from_json(body)
        self.logger(message=m)

    def logger(self, message: MeterMessage = ''):
        generation = self.photovoltaic.get_power(message.time)
        str = "{:>12} [s] | {:^10} consumed {:<07} [W] | {:^10} generated {:<08} [kW] | Netto: {:<012} [kW]\n"\
            .format(message.time, message.origin, np.round(message.consumption, 2), self.photovoltaic.id,\
                np.round(generation/1000.0, 6), np.round((generation - message.consumption)/1000, 6))
        if self.logfile is not None:
            self.logfile.write(str)
            return
        print(str)

    def __del__(self):
        self.stop_event.set()
        print("closing thread")
        if self.logfile is not None:
            self.logfile.close()


if __name__ == '__main__':
    exit(0)
