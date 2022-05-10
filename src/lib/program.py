import time
import threading
from datetime import datetime

import pika

import src.lib.configurations as configs
import src.lib.workers as workers
from src.lib.generators import Meter, Photovoltaic


class Program():
    mode = None
    duration = None
    init_time = None
    house_name = None
    pv_name = None
    log_file = None

    def __init__(self):
        while True:
            if self.mode is None:
                tmp = input("Please select Mode\n\t[S]imulation | [R]eal Time: ")
                self.mode = tmp[0].upper() if tmp[0] in ['S', 's', 'R', 'r'] else None
            if self.mode == 'R':
                self.init_time = int(time.time())
            if self.init_time is None:
                tmp = str(input("Please select initial Time of simulation (HH:MM:SS): "))
                try:
                    tmp = datetime.strptime(tmp, "%H:%M:%S")
                    self.init_time = int((tmp - datetime(1900,1,1)).total_seconds())
                except Exception:
                    print(f"Invalid time Format")
                    break
                    continue
            if self.duration is None:
                tmp = input("Please especify duration in seconds: ")
                try:
                    self.duration = int(tmp)
                except Exception:
                    print("Not a Number")

            if self.house_name is None:
                tmp = input("Select House Name (default: House): ")
                self.house_name = "House" if tmp == '' else tmp

            if self.pv_name is None:
                tmp = input("Select photovoltaic generator Name (default: PV): ")
                self.pv_name = "PV" if tmp == '' else tmp

            if self.log_file is None:
                tmp = input("Select photovoltaic generator Name (default: console output): ")
                self.log_file = None if tmp == '' else tmp

            if self.mode is not None and self.duration is not None\
                    and self.init_time is not None and self.house_name is not None\
                    and self.pv_name is not None:
                break

        print(f"set up to recording data equivalent for {self.duration} [s]")

    def run(self):
        print("Setting up program")
        meter = Meter(id=self.house_name, seed=configs.SEED, octaves=0.5)
        photovoltaic = Photovoltaic(id=self.pv_name, seed=configs.SEED)
        # Events Controling threads
        start_event = threading.Event()
        household_event = threading.Event()
        photovoltaic_event = threading.Event()
        broker_config = workers.BrokerConfigs(queue=configs.QUEUE, host=configs.HOST,\
            routing_key=configs.ROUTING_KEY, exchange=configs.EXCHANGE,\
            credentials=pika.PlainCredentials(configs.PLAINTEXT_USER, configs.PLAINTEXT_PASS))

        if self.mode == 'S':
            timer = workers.ThreadTimer(init_time=self.init_time, duration=self.duration)
        else:
            timer = None

        workers.ThreadHousehold(start_event=start_event, stop_event=household_event,\
                            meter=meter, brokerconfigs=broker_config, timer=timer)
        workers.ThreadPvGenerator(start_event=start_event, stop_event=photovoltaic_event, photovoltaic=photovoltaic, brokerconfigs=broker_config, logfile=self.log_file)

        # little pause to let the threads prepare
        time.sleep(0.5)
        start_event.set()

        if self.mode == 'S':
            print("Simulation Started\n")
            while not timer.end():
                time.sleep(1)
                continue
        else:
            print("Starting to record Data")
            t = int(time.time())
            while int(time.time()) < t + self.duration:
                time.sleep(1)
                continue

        # terminate household thread
        household_event.set()
        # let the PV thread get some more messages
        time.sleep(2)
        photovoltaic_event.set()

        print("Program Finished", end='')
        if self.log_file is not None:
            print(", please look logfile.log for output")
