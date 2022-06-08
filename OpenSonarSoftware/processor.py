##############################################################################
############################################################################## 
# Open Sonar Processor
##############################################################################
##############################################################################
# Created for the Open Sonar Project by:
# Graham Christie, Isaac Fuller, Kara Sanford
# January 2022
#############################################
# Version 1.0
##############################################################################
##############################################################################

# This program should be used to process raw log files from Open Sonar Online.
# Capabilities include:
#     - Reading raw files to extract soundings with all available data
#     - Reading raw files to extract dilution of precision data
#     - Reading sound speed profiles to calculate harmonic mean sound speeds
#     - Correcting sounding depths to harmonic mean sound speed from profiles
#     - Vertically referencing sounding depths to water level and ellipsoid
#     - Viewing processed data
#     - Cleaning suspect soundings from processed data

##############################################################################
##############################################################################

import time

import osplib

# Introductory text displayed
osplib.osp_logo()
print('Welcome to Open Sonar Processor!')
print('-----------------------------')
time.sleep(2)
print('Please type your responses to the following questions in the terminal.')
print('Do not use spaces in any response.')
time.sleep(3)

proceed = False
while not proceed:
    raw_file = input('Enter raw log file name: ')
    if raw_file == 'smile':
        osplib.smile()
    proceed = osplib.file_check(raw_file, '.csv')

print('Reading raw log file. This may take a moment.....')

raw_log = osplib.Raw_Log(raw_file)    
metadata, read_log = raw_log.read_raw_log()

print('-----------------------------------------')
print('Raw log file read and metadata extracted.')

raw_soundings = False
profile = False
raw_soundings_exists = False
profile_exists = False
correct = False
dops = False

proceed = False
while not proceed:
    print('Please select one of the following options:')
    if not profile:
        print('    - profile       (Calculate harmonic mean sound speed profile)')
    
    if not raw_soundings:
        print('    - soundings     (Extract soundings from raw data)')
        
    if profile_exists and raw_soundings_exists:
        if not correct:
            print('    - correct       (Correct soundings with harmonic mean sound speed)')
            correct = True
        
    if raw_soundings_exists:
        if not dops:
            print('    - dops          (Extract dilution of precision values over time)')
        print('    - clean         (Clean data by removing bad points)')
        
    selection = input('Type your selection here: ')
    
    if selection == 'profile':
        print('-----------------------------------------')
        print('Please enter the name of the profile you wish to process below')
        profile_name = input('Enter profile name: ')
        raw_profile = osplib.Profile(profile_name)
        raw_profile.read_simple_svp()
        profile = raw_profile.calculate_harmonic_mean()
        profile_exists = True
        profile_for_save = map(lambda x: [x], profile)
        raw_profile.plot_hmss()
        osplib.save_data(profile_for_save)
        
        
    elif selection == 'soundings':
        raw_soundings = raw_log.extract_soundings(metadata)
        raw_soundings_exists = True
        osplib.save_data(raw_soundings)
    
    elif selection == 'correct':
        soundings = raw_profile.correct_soundings(raw_soundings)
        osplib.save_data(soundings)
        
    elif selection == 'dops':
        dops = raw_log.extract_dop()
        osplib.save_data(dops)
    
    elif selection == 'clean':
        proceed = True
        print('-----------------------------------------')
        print('Proceeding to vizualization and cleaning')
    else:
        pass
    
osplib.Clean_Soundings(soundings)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

