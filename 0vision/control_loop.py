#!/usr/bin/env python
# Copyright (c) 2016, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
sys.path.append('..')
import logging

import keyboard

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config


#logging.basicConfig(level=logging.INFO)

ROBOT_HOST = '192.168.3.3'
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'

keep_running = True

logging.getLogger().setLevel(logging.INFO)

conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')
setp_names, setp_types = conf.get_recipe('setp')
watchdog_names, watchdog_types = conf.get_recipe('watchdog')

con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()

# get controller version
con.get_controller_version()

####################################################

# setup recipes
con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

print("RTDE Running...")

# control loop
while keep_running:

    # Setpoints to move the robot to

    mylines = []                             # Declare an empty list named mylines.
    with open ('coordinates.txt', 'rt') as myfile: # Open lorem.txt for reading text data.
        for myline in myfile:                # For each line, stored as myline,
            mylines.append(myline)           # add its contents to mylines.
    myfile.close()

    xc=0.0
    yc=0.0
    zc=-0.100
    roll=-0.5
    if len(mylines)!=0 and (float(mylines[1])!=0 or float(mylines[0])!=0 or float(mylines[2])!=0):
        xc = -float(mylines[0])/1000
        yc = -float(mylines[1])/1000+0.01
        zc = float(mylines[2])/1000-0.02
        roll = 0
        if yc > 0.200 :
            yc=0.200
        if yc < -0.190:
            yc=-0.190
        xb=0.320
        nxb=-0.32
        if xc > xb :
            xc = xb
        if xc < nxb:
            xc = nxb
        if zc > 1.001 :
            xc=0.0
            yc=0.0
            zc=-0.100

##    print(xc)
##    print(yc)
##    print(zc)
    #print(setp1)
    setp1 = [xc, yc, zc, 0.0, roll, 0.0]
    
    #setp1 = [0.6, -0.5, 0.6, 0.0, 3.1415926, 0.0]
    #setp2 = [0.0, -0.9, 0.6, 0.0, 3.1415926, 0.0]
    #setp2 = setp1

    setp.input_double_register_0 = 0
    setp.input_double_register_1 = 0
    setp.input_double_register_2 = 0
    setp.input_double_register_3 = 0
    setp.input_double_register_4 = 0
    setp.input_double_register_5 = 0
      
    # The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
    watchdog.input_int_register_0 = 0

    def setp_to_list(setp):
        list = []
        for i in range(0,6):
            list.append(setp.__dict__["input_double_register_%i" % i])
        return list

    def list_to_setp(setp, list):
        for i in range (0,6):
            setp.__dict__["input_double_register_%i" % i] = list[i]
        return setp

    #start data synchronization
    if not con.send_start():
        sys.exit()

##############################################

# control loop
#while keep_running:

    # receive the current state
    state = con.receive()
    
    if state is None:
        break;
    
    # do something...
    if state.output_int_register_0 != 0:
        new_setp = setp1
        list_to_setp(setp, new_setp)
        # send new setpoint        
        con.send(setp)

    # kick watchdog
    con.send(watchdog)

    if keyboard.is_pressed('Q'):  # if key 'q' is pressed 
            print('You Pressed Quit!')
            break  # finishing the loop

con.send_pause()

con.disconnect()
