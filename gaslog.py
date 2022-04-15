#!/usr/bin/env python3
# vim: set fileencoding=UTF-8 :

# HMC5888L Magnetometer (Digital Compass) wrapper class
# Based on https://bitbucket.org/thinkbowl/i2clibraries/src/14683feb0f96,
# but uses smbus rather than quick2wire and sets some different init
# params.

import math
import time
import sys
import os
import re

import rrdtool

import hmc5883l as hmc
import argparse

# Trigger level and hysteresis
trigger_level = 600
trigger_hyst = 100
# Amount to increase the counter at each trigger event
trigger_step = 0.01

# Path to RRD with counter values
count_rrd = "%s/count.rrd" % (os.path.dirname(os.path.abspath(__file__)))

# Path to RRD with magnetometer values (for testing and calibration only)
mag_rrd = "%s/mag.rrd" % (os.path.dirname(os.path.abspath(__file__)))


# Create the Round Robin Databases
def create_rrds():
  print ('Creating RRD: ' + mag_rrd)
  # Create RRD to store magnetic induction values bx, by, bz:
  # 1 value per second
  # 86400 rows == 1 day
  try:
    rrdtool.create(mag_rrd, 
      '--no-overwrite',
      '--step', '1',
      'DS:bx:GAUGE:2:-2048:2048',
      'DS:by:GAUGE:2:-2048:2048',
      'DS:bz:GAUGE:2:-2048:2048',
      'RRA:AVERAGE:0.5:1:86400')
  except Exception as e:
    print ('Error ' + str(e))

  print ('Creating RRD: ' + count_rrd)
  # Create RRD to store counter and consumption:
  # 1 trigger cycle matches consumption of 0.01 m**3
  # Counter is GAUGE
  # Consumption is ABSOLUTE
  # 1 value per minute for 3 days
  # 1 value per day for 30 days
  # 1 value per week for 10 years
  # Consolidation LAST for counter
  # Consolidation AVERAGE for consumption
  try:
    rrdtool.create(count_rrd, 
      '--no-overwrite',
      '--step', '60',
      'DS:counter:GAUGE:86400:0:100000',
      'DS:consum:ABSOLUTE:86400:0:1',
      'RRA:LAST:0.5:1:4320',
      'RRA:AVERAGE:0.5:1:4320',
      'RRA:LAST:0.5:1440:30',
      'RRA:AVERAGE:0.5:1440:30',
      'RRA:LAST:0.5:10080:520',
      'RRA:AVERAGE:0.5:10080:520')
  except Exception as e:
    print ('Error ' + str(e))

# Get the last counter value from the rrd database
def last_rrd_count():
  val = 0.0
  handle = os.popen("rrdtool lastupdate " + count_rrd)
  for line in handle:
    m = re.match(r"^[0-9]*: ([0-9.]*) [0-9.]*", line)
    if m:
      val = float(m.group(1))
      break
  handle.close()
  return val

# Write values of magnetic induction into mag rrd
# This is for testing and calibration only!
def write_mag_rrd(bx, by, bz):
  update = "N:%d:%d:%d" % (bx, by, bz)
  #print update
  rrdtool.update(mag_rrd, update)

# Main
def main():
  # Check command args
  parser = argparse.ArgumentParser(description='Program to read the gas counter value by using the digital magnetometer HMC5883.')
  parser.add_argument('-c', '--create', action='store_true', default=False, help='Create rrd databases if necessary')
  parser.add_argument('-m', '--magnetometer', action='store_true', default=False, help='Store values of magnetic induction into mag rrd')
  args = parser.parse_args()

  if args.create:
    create_rrds()

  trigger_state = 0
  timestamp = time.time()
  counter = last_rrd_count()
  print ("restoring counter to %f" % counter)
  compass = hmc.hmc5883l(gauss = 4.7, declination = (-2,5))

  while(1==1):
    # read data from HMC5883
    
    #data = read_data()
  
    # get x,y,z values of magnetic induction
    #bx = convert_sw(data, 3) # x
    #by = convert_sw(data, 7) # y 
    #bz = convert_sw(data, 5) # z


    (bx,by,bz)=compass.axes()
    if args.magnetometer:
      # write values into mag rrd
      write_mag_rrd(bx, by, bz)

    # compute the scalar magnetic induction
    # and check against the trigger level
    old_state = trigger_state
    b = math.sqrt(float(bx*bx) + float(by*by) + float(bz*bz))
    if b > trigger_level + trigger_hyst:
      trigger_state = 1
    elif b < trigger_level - trigger_hyst:
      trigger_state = 0
    if old_state == 0 and trigger_state == 1:
      # trigger active -> update count rrd
      counter += trigger_step
      update = "N:%f:%f" % (counter, trigger_step)
      #print update
      rrdtool.update(count_rrd, update)
      timestamp = time.time()
    elif time.time() - timestamp > 3600:
      # at least on update every hour
      update = "N:%f:%f" % (counter, 0)
      #print update
      rrdtool.update(count_rrd, update)
      timestamp = time.time()

    time.sleep(1)

if __name__ == '__main__':
  main()