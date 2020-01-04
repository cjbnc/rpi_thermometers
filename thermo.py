#!/usr/bin/env python3

import os
import glob
import time
import datetime
import argparse
import csv

parser = argparse.ArgumentParser(
    description='Record readings from DS18B20 thermometer')
parser.add_argument(
    '-l', '--logfile',
    help='specify log file to record readings',
    default=None)
parser.add_argument(
    '-q', '--quiet',
    help='silence reports to stdout (use with -l)',
    action='store_true')
parser.add_argument(
    '-r', '--ramfile',
    help='store latest results in file on ramdrive',
    default=None)
parser.add_argument(
    '-s', '--sleep',
    help='time to sleep between readings',
    type=float,
    default=28)
args = parser.parse_args()
LOGFILE = args.logfile
RAMFILE = args.ramfile
QUIET = args.quiet
SLEEP = args.sleep
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

if LOGFILE != None:
    log_file = open(LOGFILE, mode='a')
    log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

# CHANGE THESE TO YOUR DEVICES AND LABELS
devs = (
    {'dev':'28-011921372d21', 'loc':'hm_office'},
    {'dev':'28-0119213fa93a', 'loc':'hm_outside'},
)
 
base_dir = '/sys/bus/w1/devices/'
dev_count = 0
for device in devs:
    device['path'] = base_dir + device['dev'] + '/w1_slave'
    if os.path.exists(device['path']):
        dev_count += 1
    else:
        device['path'] = None
if dev_count == 0:
    print("No matching devices found")
    exit(-1)

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return '{:0.2f}'.format(temp_c), '{:0.2f}'.format(temp_f)

try:
    while True:
        results = []
        for device in devs:
            device_file = device['path']
            if device_file == None:
                continue;
            temps = read_temp(device_file)
            results.append(device['loc'])
            results.extend(temps)
    
        now = datetime.datetime.now().strftime("%F %T")
        results.insert(0, now)
        if not QUIET: print(results)
        if RAMFILE != None:
            ram_file = open(RAMFILE, mode='w')
            ram_file.write(', '.join(results) + "\n")
            ram_file.close()
        if LOGFILE != None:
            log_writer.writerow(results)
            log_file.flush()
        time.sleep(SLEEP)
except KeyboardInterrupt:
    print("Stopping on Ctrl-C")

if LOGFILE != None:
    log_file.close()
