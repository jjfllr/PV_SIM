import pika
import threading
import time
from src.lib.generators import Meter, Photovoltaic
# from src.lib.metermessage import MeterMessage
import src.lib.configurations as configs
import src.lib.workers as workers

def main():

    duration = 15

    print("Main thread created")
    meter = Meter(id='House_1',seed=configs.SEED, octaves=0.5)
    photovoltaic = Photovoltaic(id='PV_1',seed=configs.SEED)
    start_event = threading.Event()
    household_event = threading.Event()
    photovoltaic_event = threading.Event()
    broker_config = workers.BrokerConfigs(queue=configs.QUEUE, host=configs.HOST,\
                routing_key=configs.ROUTING_KEY, exchange=configs.EXCHANGE,\
                credentials=pika.PlainCredentials(configs.PLAINTEXT_USER, configs.PLAINTEXT_PASS))

    timer = workers.ThreadTimer(init_time=0*60*60, duration=duration)
    timer = None
    workers.ThreadHousehold(start_event=start_event, stop_event=household_event, meter=meter, brokerconfigs=broker_config, timer=timer)
    workers.ThreadPvGenerator(start_event=start_event, stop_event=photovoltaic_event, photovoltaic=photovoltaic, brokerconfigs=broker_config, logfile='./logfile.log')

    # little pause to let the threads begin
    time.sleep(1)
    start_event.set()

    if timer is not None:
        while not timer.end():
            time.sleep(0.1)
            continue

    else:
        t = int(time.time())
        while int(time.time()) < t + duration:
            time.sleep(0.1)
            continue

    # terminate household thread
    household_event.set()
    # let the PV thread get some more messages
    time.sleep(3)
    photovoltaic_event.set()


    print("Main Finished")


if __name__ == '__main__':
    main()
