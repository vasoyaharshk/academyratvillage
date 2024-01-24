import serial
import datetime
import os
import csv
import time
from user import settings
from multiprocessing import Process


class FakeEcohab:
    def __init__(self):
        self.name = "ECOHAB NOT FOUND"

    def play(self):
        pass
    def terminate(self):
        pass


class Ecohab(Process):
    def __init__(self):
        Process.__init__(self)

        self.name = "eco"
        start = time.time()
        port = "/dev/ttyUSB-Ecohab"
        ecohab = serial.Serial(port=port, baudrate=115200, timeout=0.1)


    def read_ecohab(self):
        start = time.time()
        port = "/dev/ttyUSB-Ecohab"
        ecohab = serial.Serial(port=port, baudrate=115200, timeout=0.1)
        datetimestr = str(datetime.datetime.now()).replace(' ', '_')
        ecohab_path = os.path.join(settings.ECOHAB_DIRECTORY, 'ecohab_' + datetimestr + '_raw.csv')

        with open(ecohab_path, 'w') as result:
            filewriter = csv.writer(result, delimiter='\t')
            header = ['Date', 'Time', 'Antena_number', 'RFID_detected', 'RFID_label']
            filewriter.writerow(header)
            result.flush()

            if not ecohab.isOpen():
                ecohab.open()

            while True:
                tag = ecohab.readline()

                try:
                    tag = tag.decode('utf-8')
                    if tag != '':
                        # print(tag)
                        datetimestr = str(datetime.datetime.now())
                        date = str(datetimestr[0:4] + '.' + datetimestr[5:7] + '.' + datetimestr[8:10])
                        timing = datetimestr[11:]
                        antenna = tag[11:12]
                        rfid = tag[0:10]
                        print(date, timing, antenna, rfid)
                        filewriter.writerow([date, timing, antenna, rfid])
                        result.flush()
                        # print(time.time() - start)
                        if time.time() - start > 86400:
                            # print('starting new record')
                            return()
                        # print('reading')


                except UnicodeDecodeError:
                    tag = None

    def play(self):
        self.start()

    def run(self):
        while True:

            try:
                print('STARTING ECOHAB')
                self.read_ecohab()

            except:
                time.sleep(600)


try:
    eco = Ecohab()
except:
    eco = FakeEcohab()


eco.play()