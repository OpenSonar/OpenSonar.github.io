##############################################################################
############################################################################## 
# Open Sonar Configurator
##############################################################################
##############################################################################
# Created for the Open Sonar Project by:
# Graham Christie, Isaac Fuller, Kara Sanford
# January 2022
#############################################
# Version 1.0
##############################################################################
##############################################################################

# This program should be used to enter all relavent metadata and configuration
# information about the survey and survey vessel prior to field work. The data
# entered here will be used to create a configuration file which will ensure
# the acquisition and processing software are configured correctly.

# Enter in the information as required by the description then run the program
# or run the program and follow the prompts.

#-----------------
# Survey metadata
    # Replace the text with your survey name and location, and filename
    # Replace the numbers with the survey date (YYYY,MM,DD)
survey_name = 'Example_Survey_Name'
survey_location = 'Example_Survey_Location'
survey_filename = 'Output/example_survey_name_config.csv'
survey_date = [2022,1,1]
#-----------------

#-----------------
# Vessel metadata
    # Replace the text with your vessel name
vessel_name = 'Example_Vessel_Name'
#-----------------

#-----------------
# GNSS metadata
    # Replace the text with your GNSS name and type
    # Replace the waterline offset with a positive distance value from the 
    # waterline to the GNSS antenna in meters
gnss_name = 'Example_GNSS_Name'
gnss_type = 'Generic_NMEA'
gnss_waterline_offset = 0.5
#-----------------

#-----------------
# Sonar metadata
    # Replace the text with your sonar name and type
    # Replace the waterline offset with a negative distance value from the 
    # waterline to the sonar transducer face in meters
sonar_name = 'Example_Sonar_Name'
sonar_type = 'BR_Ping'
sonar_waterline_offset = -0.5
#-----------------

#-----------------
# SVP metadata
    # Replace the text with the SVP name and type
    # Replace the number with the desired default sound speed
svp_name = 'Example_SVP_Name'
svp_type = 'Valeport_SVS'
default_sndspd = 1480
#-----------------

#-----------------
# GNSS coms
    # Replace the text with the name of the com port
    # Replace the number with the baud rate used by the sensor
gnss_port = 'COM7'
gnss_baud = 460800
#-----------------

#-----------------
# Sonar coms
    # Replace the text with the name of the com port
    # Replace the number with the baud rate used by the sensor
sonar_port = 'COM3'
sonar_baud = 115200
#-----------------

#-----------------
# SVP coms
    # Replace the text with the name of the com port
    # Replace the number with the baud rate used by the sensor
svp_port = 'COM9'
svp_baud = 9600
#-----------------

# End of information to be entered, code to follow

##############################################################################
##############################################################################

# The following code allows the user to select how they want to enter the 
# necessary metadata information, either by using the information entered
# above, or by following the prompts to enter them into the command line.

# It then uses osplib to write a configuration file in the specified location.

import datetime as dt
import time
import osplib

# Introductory text displayed
osplib.osp_logo()
print('Welcome to the Open Sonar Project Survey Configurator!')
print('------------------------------------------------------')
time.sleep(2)
print('Please type your responses to the following questions in the terminal.')
print('Do not use spaces in any response.')
time.sleep(3)

# User given the opportunity to either use the information entered above
# or to configure a new survey.
print('Would you like to configure a new survey?')
print('    Selecting "yes" will prompt you to enter the neccessary information.')
print('    Selecting "no" will use the information entered in the code above.')
print('    - yes')
print('    - no')
new_survey = input('Type your response here then press enter: ')    

# If the user selects yes to configure a new survey, they are prompted to enter
# the relevant information. Various checks are made on the information as entered
# to ensure it is the correct format.

if new_survey == 'yes':
    print('Configuring new survey!')
    time.sleep(2)
    
    print('-----------------')
    print('Survey metadata')
    proceed = False
    while not proceed:
        print('    Enter text with the survey name')
        survey_name = input('Survey name: ')
        length = len(survey_name.split(' '))
        if length == 1:                
            proceed = True
        else:
            print('    ### Please do not use spaces in your entry ###')
    print('    Enter text with the survey location')
    survey_location = input('Survey location: ')
    proceed = False
    while not proceed:
        print('    Enter text with the survey configuration filename')
        survey_filename = input('Survey filename (ends with .csv): ')
        length = len(survey_filename.split(' '))
        if length == 1:
            if survey_filename.endswith('.csv'):                
                proceed = True
            else:
                print('    ### Please ensure your filename ends with ".csv" ###')
        else:
            print('    ### Please do not use spaces in your entry ###')
    print('Enter numbers for the survey year, month, and day')
    proceed = False
    while not proceed:
        survey_year = input('Survey year: ')
        survey_month = input('Survey month: ')
        survey_day = input('Survey day: ')
        try:
            survey_year = int(survey_year)
            survey_month = int(survey_month)
            survey_day = int(survey_day)
            if (survey_year > 2000 and survey_year < 2100):
                if (survey_month <= 12 and survey_month > 0):
                    if (survey_day <= 31 and survey_month > 0):
                        proceed = True
                    else:
                        print('    ### Please enter a valid day ###')
                else:
                    print('    ### Please enter a valid month ###')
            else:
                print('    ### Please enter a valid year ###')
        except:
            print('    ### Please enter integer numbers')
    survey_date = [survey_year,survey_month,survey_day]
    print('-----------------')
    
    #-----------------
    print('Vessel metadata')
    print('    Enter text with your vessel name')
    vessel_name = input('Vessel name: ')
    print('-----------------')

    print('GNSS metadata')
    print('    Enter text with the GNSS name')
    gnss_name = input('GNSS name: ')
    print('    Enter text with the GNSS type')
    gnss_type = input('GNSS type: ')
    proceed = False
    while not proceed:        
        print('    Enter a waterline offset with a positive distance value from the ')
        print('    waterline to the GNSS antenna in meters')
        gnss_waterline_offset = input('GNSS waterline offset (m): ')
        try:
            gnss_waterline_offset = float(gnss_waterline_offset)
            if gnss_waterline_offset >= 0:
                proceed = True
            else:
                print('    ### Please enter a positive value ###')
        except:
            print('    ### Please enter a valid number ###')
    print('-----------------')
    
    print('Sonar metadata')
    print('    Enter text with the sonar name')    
    sonar_name = input('Sonar name:')
    print('    Enter text with the sonar type')
    sonar_type = input('Sonar type: ')
    proceed = False
    while not proceed:        
        print('    Enter a waterline offset with a negative distance value from the ')
        print('    waterline to the sonar transducer face in meters')
        sonar_waterline_offset = input('Sonar waterline offset (m): ')
        try:
            sonar_waterline_offset = float(sonar_waterline_offset)
            if sonar_waterline_offset <= 0:
                proceed = True
            else:
                print('    ### Please enter a negative value ###')
        except:
            print('    ### Please enter a valid number ###')

    print('-----------------')
    
    print('SVP metadata')
    print('    Enter text with the SVP name')    
    svp_name = input('SVP name: ')
    print('    Enter text with the SVP type')
    svp_type = input('SVP type: ')
    print('    Enter a number with the desired default sound speed')
    default_sndspd = input('Default sound speed (m/s): ')
    print('-----------------')
    
    print('GNSS coms')
    print('    Enter text with the name of the com port')    
    gnss_port = input('GNSS port: ')
    print('    Enter a number with the baud rate used by the sensor')
    gnss_baud = input('GNSS baud rate: ')
    print('-----------------')
    
    print('Sonar coms')
    print('    Enter text with the name of the com port')    
    sonar_port = input('Sonar port: ')
    print('    Enter a number with the baud rate used by the sensor')
    sonar_baud = input('Sonar baud rate: ')
    print('-----------------')
    
    print('SVP coms')
    print('    Enter text with the name of the com port')    
    svp_port = input('SVP port: ')
    print('    Enter a number with the baud rate used by the sensor')
    svp_baud = input('SVP baud rate:')
    print('-----------------')
    time.sleep(2)
# If the user selects not to configure a new survey, the above entered
# information is used.
else:
    print('Using existing information entered')
    time.sleep(2)

# The metadata information is then written to a dictionary
survey_metadata = {}
survey_metadata['filetype'] = ['OSPLIB_CONFIG']
survey_metadata['Survey'] = [survey_name, survey_location, dt.datetime(
    survey_date[0],survey_date[1],survey_date[2])]
survey_metadata['Geodetics'] = [6378137, 298.257223563]
survey_metadata['Vessel'] = [vessel_name]
survey_metadata['GNSS'] = [gnss_name, gnss_type, gnss_waterline_offset, 0, 0, 0]
survey_metadata['Sonar'] = [sonar_name, sonar_type, sonar_waterline_offset, 0, 0, 0]
survey_metadata['SVP'] = [svp_name, svp_type, default_sndspd]
survey_metadata['GNSS_Com'] = [gnss_name, gnss_port, gnss_baud]
survey_metadata['Sonar_Com'] = [sonar_name, sonar_port, sonar_baud]
survey_metadata['SVP_Com'] = [svp_name, svp_port, svp_baud]

# This dictionary is then written to a configuration file by an osplib function
osplib.write_meta_header(survey_filename, survey_metadata)

# The information used is then displayed for confirmation of entered information
print('------------------------------------------------------')
print('Configuration file written using the following information:')
print(survey_metadata)

