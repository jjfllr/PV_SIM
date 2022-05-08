import pika
import threading
import time
from src.lib.generators import Meter, Photovoltaic
# from src.lib.metermessage import MeterMessage
import src.lib.configurations as configs
import src.lib.workers as workers

def main():

    print("Main thread created")
    meter = Meter(seed=configs.SEED, octaves=0.5)
    photovoltaic = Photovoltaic(seed=configs.SEED)
    household_event = threading.Event()
    photovoltaic_event = threading.Event()
    broker_config = workers.BrokerConfigs(queue=configs.QUEUE, host=configs.HOST,\
                routing_key=configs.ROUTING_KEY, exchange=configs.EXCHANGE,\
                credentials=pika.PlainCredentials(configs.PLAINTEXT_USER, configs.PLAINTEXT_PASS))

    workers.ThreadHousehold(stop_event=household_event, meter=meter, brokerconfigs=broker_config)
    workers.ThreadPvGenerator(stop_event=photovoltaic_event, photovoltaic=photovoltaic, brokerconfigs=broker_config)

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
