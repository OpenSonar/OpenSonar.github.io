##############################################################################
############################################################################## 
# Open Sonar Online
##############################################################################
##############################################################################
# Created for the Open Sonar Project by:
# Graham Christie, Isaac Fuller, Kara Sanford
# January 2022
#############################################
# Version 1.0
##############################################################################
##############################################################################

# This program should be used to collect raw sonar and GNSS data. Prior to
# running this program, use the configurator to set up a configuration file.
# The configuration file will allow Open Sonar Online to properly configure
# its settings to allow data collection to occur as desired.

# Enter in the information as required by the description then run the program

#-----------------
# Configuration File Name
    # Replace the configuration file name with your configuration file
configuration_filename = 'Output/example_survey_name_config.csv'
#-----------------

# End of information to be entered, code to follow

##############################################################################
##############################################################################

# The following code allows online data collection from the GNSS, sonar, and
# sound velocity probes mounted on the vessel. Monitor the console for 
# messages about system status, and for live data.

import sys
import time
import datetime as dt

import osplib

# Introductory text displayed
osplib.osp_logo()
print('Welcome to Open Sonar Online!')
print('-----------------------------')
time.sleep(2)
print('Please type your responses to the following questions in the terminal.')
print('Do not use spaces in any response.')
time.sleep(3)

configuration_filename = input('Enter configuration file name: ')

# Use the configuration file reader from osplib to read the metadata
metadata = osplib.read_config_file(configuration_filename)

# Create an instance of each osplib sensor object by passing it the metadata
gpsdevice = osplib.GNSS(metadata)
sonardevice = osplib.Sonar(metadata)
svpdevice = osplib.Speed(metadata)



# Connect to each osplib sensor object using their connect functions
gps_connection = gpsdevice.connect_gnss()
sonar_connection = sonardevice.connect_sonar()
svp_connection = svpdevice.connect_speed()


# Check if the sensors are connected properly. If GNSS or sonar not connected
# then exit after closing any connections that are open
if not gps_connection or not sonar_connection:
    print('-------------------------------------------')
    print('No GNSS or Sonar Detected - Exiting Program')
    print('-------------------------------------------')
    try:
        gpsdevice.disconnect_gnss()
    except:
        pass
    try:
        svpdevice.disconnect_speed()
    except:
        pass
    sys.exit()

# If everything is connected correctly, create simple and raw log files and 
# write the metadata header to them, then open them for writing data.
start_time = dt.datetime.now()
metadata['filetype'] = ['OSP_SIMPLE_LOG']
simple_log = 'Output/'+metadata['Survey'][0]+'_simple_'+\
    dt.datetime.strftime(start_time,'%H%M%S')+'.csv'
osplib.write_meta_header(simple_log, metadata)
simple_log_writer = open(simple_log, 'a', 1)
metadata['filetype'] = ['OSP_RAW_LOG']
raw_log = 'Output/'+metadata['Survey'][0]+'_raw_'+\
    dt.datetime.strftime(start_time,'%H%M%S')+'.csv'
osplib.write_meta_header(raw_log, metadata)
raw_log_writer = open(raw_log, 'a', 1)

# Set the sound speed source for the system.

# Give the user the choice of where they want the sound speed set on the sonar
# to come from. Choices are the sound velocity probe, the default sound speed
# in the configuration file, or a manually entered sound speed. Based on their
# selection, get that sound speed and set it to the sonar head, then retrieve
# the sound speed set on the sonar head to confirm.
proceed = False
update_speed = False
while proceed == False:
    print('-----------------------------------------------------------------------')
    print('Please select the option you would like for setting the sound speed')
    print('for the sonar to use:')
    print('    svp     - Use the sound speed directly from the surface sound speed')
    print('              sensor if it is present. Will update every minute online')
    print('    default - Use the default sound speed from the configuration file')
    print('    manual  - Give the option to enter a manual sound speed to be used')
    print('    exit    - close all connections and exit the program')
    soundspeed_option = input('Type your selection here: ')
    if soundspeed_option == 'svp':
        print('Sound velocity probe selected as sound speed source.')
        if svp_connection:
            soundspeed_reading = svpdevice.get_surface_sound_speed()
            sonardevice.set_sound_speed(soundspeed_reading)
            time.sleep(2)
            proceed = True
            update_speed = True
        else:
            print('Sound velocity probe not found. Select another option')
            time.sleep(3)
    elif soundspeed_option == 'default':
        print('Default sound speed selected as sound speed source.')
        soundspeed_reading = metadata['SVP'][2]
        sonardevice.set_sound_speed(soundspeed_reading)
        time.sleep(2)
        proceed = True
    elif soundspeed_option == 'manual':
        print('Manual sound speed entry selected. Enter the desired sound speed.')
        manual_soundspeed = input('Manual sound speed: ')
        try:
            soundspeed_reading = float(manual_soundspeed)
            if soundspeed_reading < 1500 and soundspeed_reading > 1400:
                print('Manual sound speed entered.')
                sonardevice.set_sound_speed(soundspeed_reading)
                time.sleep(2)
                proceed = True
            else:
                print('Please enter a valid sound speed')
                time.sleep(3)
        except:
            print('Invalid entry - Not a number.')
            time.sleep(3)
    elif soundspeed_option == 'exit':
        print('---------------')
        print('Exiting Program')
        print('---------------')
        simple_log_writer.close()
        raw_log_writer.close()
        try:
            gpsdevice.disconnect_gnss()
        except:
            pass
        try:
            svpdevice.disconnect_speed()
        except:
            pass
        sys.exit()
    else:
        print('Invalid entry - Please select from the list.')
        time.sleep(3)
current_speed = sonardevice.get_sound_speed()
time.sleep(2)

# Give the user the choice to go online and begin recording or exit
proceed = False
while proceed == False:
    print('--------------------------------------------------------------')
    print('Select one of the options below:')
    print('    online    - Go online with the system and begin recording')
    print('    exit      - Exit the program and close all conections')
    online_setting = input('Type your selection here: ')
    if online_setting == 'online':
        print('Going online in...')
        print('3')
        time.sleep(1)
        print('2')
        time.sleep(1)
        print('1')
        time.sleep(1)
        print('Online!')
        proceed = True
    elif online_setting == 'exit':
        print('---------------')
        print('Exiting Program')
        print('---------------')
        simple_log_writer.close()
        raw_log_writer.close()
        try:
            gpsdevice.disconnect_gnss()
        except:
            pass
        try:
            svpdevice.disconnect_speed()
        except:
            pass
        sys.exit()
    else:
        print('Invalid entry - Please select an option from the list.')
        time.sleep(3)


# Take a test observation
obs_numb = 0

while True:
    obs, speed = osplib.take_observation(metadata, gpsdevice, sonardevice, svpdevice, 
                                          current_speed, update_speed, obs_numb,
                                          simple_log_writer, raw_log_writer)
    obs_numb = obs
    current_speed = speed







# Close log files and connections to sensors after data collection is finished
gpsdevice.disconnect_gnss()
svpdevice.disconnect_speed()
simple_log_writer.close()
raw_log_writer.close()





