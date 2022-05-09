import time
import datetime

from src.lib.program import Program

def main():
    print("--- PV Simulator ---")
    p = Program()
    print("Start time: ", datetime.datetime.fromtimestamp(time.time()))
    p.run()
    print("End time: ", datetime.datetime.fromtimestamp(time.time()))


if __name__ == '__main__':
    main()
