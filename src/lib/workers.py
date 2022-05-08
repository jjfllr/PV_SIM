import pika
from src.lib.generators import Meter, Photovoltaic
from src.lib.metermessage import MeterMessage

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
                t = 23.00
                m = MeterMessage(origin=self.meter.id, time=t, consumption=self.meter.get_consumption(t))
                self._publish(message=str(m.to_json()))
            time.sleep(1)
        print('H Finished')
        self.connection.close()


class ThreadPvGenerator(object):

    def __init__(self, stop_event, photovoltaic=Photovoltaic(), brokerconfigs=BrokerConfigs(), logfile=None):
        if logfile is not None:
            self.logfile = open(logfile, 'w')
        else:
            self.logfile = None

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
        m = MeterMessage.from_json(body)
        self.logger(message=m)

    def logger(self, message: MeterMessage = ''):
        generation = self.photovoltaic.get_power(message.time)
        str = "{:10} - Meter {:10} consumed {:10} [W] | PV {:10} generated {:10} [W] | Consumption Netto: {}\n"\
            .format(message.time, message.origin, message.consumption, self.photovoltaic.id,\
            generation, generation - message.consumption)
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
