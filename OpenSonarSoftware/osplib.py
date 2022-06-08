##############################################################################
############################################################################## 
# Open Sonar Library
##############################################################################
##############################################################################
# Created for the Open Sonar Project by:
# Graham Christie, Isaac Fuller, Kara Sanford
# January 2022
#############################################
# Version 5.0
##############################################################################
##############################################################################

import csv
import os
import io
import numpy as np
import datetime as dt
import serial
import matplotlib.pyplot as plt
import math


from brping import Ping1D
import pynmea2

#########################################
#########################################
# Sensors
#########################################
#########################################

#-----------------------------------------------------------------------------
class GNSS:
# Class to manage all GNSS functions
    def __init__(self, metadata):
        self.gps_com = metadata['GNSS_Com'][1]
        self.gps_baud = metadata['GNSS_Com'][2]
    
    def connect_gnss(self):
        # Function to connect to the GNSS serial port
        try:
            self.gps_ser = serial.Serial(self.gps_com, self.gps_baud, timeout=0.1)
            self.gps_sio = io.TextIOWrapper(io.BufferedRWPair(self.gps_ser, self.gps_ser))
            self.gps_found = True
            print('GNSS Connected')
            return self.gps_found
        except:
            print('No GNSS Found!')
            self.gps_found = False
            return self.gps_found
        
    def disconnect_gnss(self):
        # Function to close serial port to GNSS
        if not self.gps_found:
            return
        self.gps_ser.close()
        self.gps_found = False
            
    def get_nmea(self):
        # Function to get GGA strings with timestamp attached
        if not self.gps_found:
            gps_error = [['No','GNSS Found'],True]
            return gps_error
        while True:
            ping = False
            try:
                self.gps_ser.reset_input_buffer()
                line = self.gps_sio.readline()
                time = dt.datetime.utcnow().time()
                msg = pynmea2.parse(line)
                
            
                if type(msg) == pynmea2.types.talker.GGA:
                    ping = True
                elif type(msg) == pynmea2.types.talker.RMC:
                    ping = True
                elif type(msg) == pynmea2.types.talker.GLL:
                    ping = True
                return time, msg, ping
            except:
                pass
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
class Sonar:
# Class to manage all sonar functions
    def __init__(self, metadata):
        self.sonar_com = metadata['Sonar_Com'][1]
        self.sonar_baud = metadata['Sonar_Com'][2]
        
    def connect_sonar(self):
        # Function to connect to the sonar
        try:
            self.myping = Ping1D()
            self.myping.connect_serial(self.sonar_com, self.sonar_baud)
            self.sonar_found = True
            print('Sonar Connected')
            return self.sonar_found
        except:
            print('No Sonar Found!')
            self.sonar_found = False
            return self.sonar_found
        
    def send_ping(self):
        # Function to take a single ping from sonar
        if not self.sonar_found:
            return
        self.distance = self.myping.get_distance()
        self.distance['distance'] = self.distance['distance']/1000
        self.time = dt.datetime.utcnow().time()
        
        observation = self.time, self.distance
        
        return observation
            
    def ping_to_string(self, ssp):
        #Function to turn the observation dictionary into a string for writing
        if not self.sonar_found:
            return 'No Sonar Found'
        dist = self.distance['distance']
        conf = self.distance['confidence']
        dura = self.distance['transmit_duration']
        star = self.distance['scan_start']
        leng = self.distance['scan_length']
        gain = self.distance['gain_setting']
        
        ping_string = str(self.time)+','+'$DEPTH,'+str(dist)+','+\
            str(conf)+','+str(dura)+','+str(star)+','+str(leng)+','\
            +str(gain)+','+str(ssp) + '\n'
        
        return ping_string
    
    def set_sound_speed(self, soundspeed):
        # Function to set a specified sound speed to the sonar
        sound_speed_ms = soundspeed
        if not self.sonar_found:
            return False
        sound_speed_mms = round(sound_speed_ms * 1000)
        print('--------------------------------------------------------------')
        print(f'Setting sound speed to {sound_speed_ms} m/s on sonar head')
        print('--------------------------------------------------------------')
        self.myping.set_speed_of_sound(sound_speed_mms)
        return True
    
    def get_sound_speed(self):
        # Function to get the sound speed set onthe sonar
        if not self.sonar_found:
            return
        sound_speed_mms = self.myping.get_speed_of_sound()
        sound_speed_ms = sound_speed_mms['speed_of_sound']/1000
        print('--------------------------------------------------------------')
        print(f'Sound speed is to {sound_speed_ms} m/s on sonar head')
        print('--------------------------------------------------------------')
        return sound_speed_ms
        
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
class Speed:
# Class to manage all surface sound speed functions
    def __init__(self, metadata):
        self.svp_com = metadata['SVP_Com'][1]
        self.svp_baud = metadata['SVP_Com'][2]
        
    def connect_speed(self):
        # Function to connect to the surface svp
        try:
            self.svp_ser = serial.Serial(self.svp_com, self.svp_baud, timeout=2.5)
            self.svp_sio = io.TextIOWrapper(io.BufferedRWPair(self.svp_ser, self.svp_ser))
            self.svp_found = True
            print('SVP Connected')
            return self.svp_found
        except:
            print('No SVP Found!')
            self.svp_found = False
            return self.svp_found
        
    def get_surface_sound_speed(self):
        try:
            self.svp_ser.reset_input_buffer()
            line = self.svp_ser.readline()
            message = line.decode()
            soundspeed = float(message)/1000
            return soundspeed
        except:
            print('SVP Error')
            pass

    def disconnect_speed(self):
        # Function to close serial port to surface svp
        if not self.svp_found:
            return
        self.svp_ser.close()
#-----------------------------------------------------------------------------

#########################################
#########################################
# Online Actions
#########################################
#########################################

#-----------------------------------------------------------------------------
def take_observation(metadata, gnss_device, sonar_device, svp_device, 
                     current_speed, update_speed, obs_numb, simple_log, raw_log):
    if update_speed:
        if obs_numb == 100:
            print('Updating sound speed from sound velocity probe')
            current_speed = svp_device.get_surface_sound_speed()
            sonar_device.set_sound_speed(current_speed)
            
            obs_numb = 0
        else:
            obs_numb += 1
     
    time, nmea, ping = gnss_device.get_nmea()
        
    nmea_message = str(time) + ',' + str(nmea) + '\n'
    raw_log.write(nmea_message)
    if ping:
            
        time, sonar = sonar_device.send_ping()
            
        sonar_message = sonar_device.ping_to_string(current_speed)
            
        raw_log.write(sonar_message)
        nmea_message = nmea_message.split(',')
        if nmea_message[1] == '$GNGGA':
            waterline = metadata['Sonar'][2]
            depth = sonar['distance']+waterline
            depth = round(depth,3)
            height = float(nmea_message[10])+float(nmea_message[12])-depth-metadata['GNSS'][2]
            height = round(height,3)
            simple_message = str(time)+','+str(nmea.latitude)+','+\
                str(nmea.longitude)+','+str(depth)+','+\
                str(height)+','+str(current_speed)+'\n'
            print(simple_message)
            simple_log.write(simple_message)
    return obs_numb, current_speed
#-----------------------------------------------------------------------------

#########################################
#########################################
# Readers
#########################################
#########################################

#-----------------------------------------------------------------------------
def generic_reader(filename, delimit, start, end):
    # Generic reader used to read all files
    return_list = []        
    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=delimit)
        start_found = False
        for row in csv_reader:
            if row[0] != start and start_found == False:
                pass
            elif row[0] == start:
                start_found = True                    
            elif row[0] == end:                    
                return return_list
            else:
                return_list.append(row) 
    return return_list    
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def read_config_file(filename):
    # Controller for generic reader to extract metadata from config file
    if not file_check(filename, '.csv'):
        return
        
    read_result = generic_reader(filename,',','Header_Start','Header_End')
        
    meta = {}
    meta['Survey'] = [read_result[0][0],read_result[0][1],read_result[0][2]]
    meta['Geodetics'] = [float(read_result[1][0]),float(read_result[1][1])]
    meta['Vessel'] = [read_result[2][0]]
    meta['GNSS'] = [read_result[3][0],read_result[3][1],float(read_result[3][2]),
                        float(read_result[3][3]),float(read_result[3][4]),
                        float(read_result[3][5])]        
    meta['Sonar'] = [read_result[4][0],read_result[4][1],float(read_result[4][2]),
                         float(read_result[4][3]),float(read_result[4][4]),
                         float(read_result[4][5])] 
    meta['SVP'] = [read_result[5][0],read_result[5][1],float(read_result[5][2])]
    meta['GNSS_Com'] = [read_result[6][0],read_result[6][1], int(read_result[6][2])]
    meta['Sonar_Com'] = [read_result[7][0],read_result[7][1], int(read_result[7][2])]
    meta['SVP_Com'] = [read_result[8][0],read_result[8][1],int(read_result[8][2])]
                
    return meta
#-----------------------------------------------------------------------------

#########################################
#########################################
# Writers
#########################################
#########################################

#-----------------------------------------------------------------------------
def write_meta_header(filename, metadata):
    # Function to write new files with survey metadata as the header
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([metadata['filetype']])
        writer.writerow(['Header_Start'])
        writer.writerow(metadata['Survey'])
        writer.writerow(metadata['Geodetics'])
        writer.writerow(metadata['Vessel'])
        writer.writerow(metadata['GNSS'])
        writer.writerow(metadata['Sonar'])
        writer.writerow(metadata['SVP'])
        writer.writerow(metadata['GNSS_Com'])
        writer.writerow(metadata['Sonar_Com'])
        writer.writerow(metadata['SVP_Com'])
        if metadata['filetype'][0] == 'OSP_SIMPLE_LOG':
            writer.writerow(['Time, Latitude, Longitude, Depth_Below_Water, Height_Ellipsoidal, Soundspeed'])
        writer.writerow(['Header_End'])
    print(metadata['filetype'][0]+' file created')    
        
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def save_data(data):
    
    print('--------------------------------------------------')
    print('Would you like to save this data?')
    print('    - yes')
    print('    - no')
    selection = input('Type your selection here: ')
    if selection == 'no':
        print('You have elected not to save your data')
        return
    elif selection == 'yes':
        filename = input('Enter a file name: ')
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerows(data)
        print('Data saved to file.')
    return
#-----------------------------------------------------------------------------

#########################################
#########################################
# Post processing applications
#########################################
#########################################

#-----------------------------------------------------------------------------
class Profile:
# Class to manage soundspeed profiles and their application
    def __init__(self, svp_filename):
        self.svp_filename = svp_filename
        
    def read_simple_svp(self):
        # Function to read a simple svp into the class
        lines = []        
        with open(self.svp_filename) as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                lines.append(row)
        self.depths_list = []
        self.speeds_list = []
        for item in lines:
            depth = item[0]
            speed = item[1]
            try:
                depth = float(depth)
                speed = float(speed)
                self.depths_list.append(depth)
                self.speeds_list.append(speed)
            except:
                pass
        return self.depths_list, self.speeds_list
    
    def calculate_harmonic_mean(self):
        # Function to calculate hmss using layers of constant gradient
        surface_soundspeed = round(self.speeds_list[0],1)
        
        last_depth = 0
        last_speed = surface_soundspeed
        time_sum = 0
        delta_depth_sum = 0
        
        self.harmonic_mean_list = []
        
        count = 0
        
        while count <= (len(self.depths_list)-1):
            delta_speed = self.speeds_list[count] - last_speed
            delta_depth = self.depths_list[count] - last_depth
            
            g = delta_speed/delta_depth
            time = (1/g) * (np.log(self.speeds_list[count]/last_speed))
            
            time_sum = time_sum + time
            delta_depth_sum = delta_depth_sum + delta_depth
            harmonic_mean = delta_depth_sum/time_sum
            self.harmonic_mean_list.append(harmonic_mean)
            
            last_depth = self.depths_list[count]
            last_speed = self.speeds_list[count]
            count += 1
        
        return self.harmonic_mean_list
    
    def correct_soundings(self, soundings):
        old_depths = []
        new_depths = []

        old_speeds = []
        new_speeds = []

        number = []

        #diff = []
        for row in soundings:
            o_depth = row[-3]
            o_speed = row[-1]
    
            n_depth, n_speed = self.correct_soundspeed(o_depth, o_speed)
            
            diff = n_depth-o_depth
            
            row.append(round(n_depth,3))
            row.append(round(row[-3]+diff,3))
            row.append(round(n_speed,3))

            old_depths.append(o_depth)
            new_depths.append(n_depth)
    
            old_speeds.append(o_speed)
            new_speeds.append(n_speed)
    
            #diff.append(o_depth-n_depth)
    
            number.append(row[1])
        corrected_soundings = soundings
    
        return corrected_soundings
    
    def correct_soundspeed(self, original_depth, original_soundspeed):
        # Function to take a depth ping and soundspeed and change to new soundspeed
        travel_time = original_depth/original_soundspeed
        
        for item in self.depths_list:
            if original_depth < item:
                interpolate = True
                next_depth_index = self.depths_list.index(item)
                prev_depth_index = self.depths_list.index(item)-1
                break
            else:
                interpolate = False
                
        if interpolate:
            x = [self.depths_list[prev_depth_index],self.depths_list[next_depth_index]]
            y = [self.harmonic_mean_list[prev_depth_index],self.harmonic_mean_list[next_depth_index]]
        
            depth_of_interest = original_depth
            new_soundspeed = np.interp(depth_of_interest, x, y)
        else:
            new_soundspeed = self.harmonic_mean_list[-1]
            
        new_depth = new_soundspeed * travel_time
        
        return new_depth, new_soundspeed
    
    def plot_hmss(self):
        # Function to plot profile and harmonic mean sound speed
        plt.plot(self.speeds_list, self.depths_list, color='turquoise', 
                 linewidth=3, linestyle='solid', label="Observed")
        plt.plot(self.harmonic_mean_list, self.depths_list, color='red', 
                 linewidth=3, linestyle='solid', label="Harmonic Mean")
        plt.axis([min(self.speeds_list)-0.05, max(self.speeds_list)+0.05, 
                  max(self.depths_list)+0.5, min(self.depths_list)-0.5])
        plt.title("Harmonic Mean Sound Speed vs Depth")
        plt.xlabel("Sound Speed [m/s]")
        plt.ylabel("Depth [m]")
        plt.legend()
        plt.gcf().set_dpi(300)
        plt.grid()
        plt.show()
        
        return
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
class Raw_Log:
# Class to manage raw log processing
    def __init__(self, raw_log_filename):
        self.raw_log_filename = raw_log_filename
        
    def read_raw_log(self):
        # Function to read a raw log file
        self.metadata = read_config_file(self.raw_log_filename)
        raw_log = generic_reader(self.raw_log_filename, ',', 'Header_End', None)
        self.raw_log_read = []
        
        for row in raw_log:
            try:
                row[0] = dt.datetime.strptime(row[0], '%H:%M:%S.%f').time()            
                for i in range(len(row)):
                    try:
                        if row[i] == '':
                            row[i] = None
                        row[i] = float(row[i])

                    except:
                        pass
                self.raw_log_read.append(row)
            except:
                pass
        
        return self.metadata, self.raw_log_read
    
    def get_time_lat_long(self, message, t, la, lo):
        time, lat, long = None, None, None
        try:
            message[t] = str(message[t])
            time = dt.datetime.strptime(message[t], '%H%M%S.%f').time()
            if message[la+1] == 'N':
                lat_raw = message[la]
                neg_la = False
            elif message[la+1] == 'S':
                lat_raw = message[la]
                neg_la = True
            if message[lo+1] == 'E':
                long_raw = message[lo]
                neg_lo = False
            elif message[lo+1] == 'W':
                long_raw = message[lo]
                neg_lo = True
        
            lat_d = math.floor(lat_raw/100)
            lat_m = (lat_raw/100 - lat_d) * 100
            lat = lat_d+(lat_m/60)
        
            long_d = math.floor(long_raw/100)
            long_m = (long_raw/100 - long_d) * 100
            long = long_d+(long_m/60)
            
            if neg_la:
                lat = -lat
            if neg_lo:
                long = -long
            
            return time, lat, long
        except:
            return time, lat, long
    
    def extract_dop(self):
        #Function to extract dop values from GNGSA messages
        dop_log = []
        prev_row = None
        for row in self.raw_log_read:
            if row[1] == '$GNGSA':
                if not prev_row[1] == '$GNGSA':
                    time = row[0]
                    ping = row[1]
                    pdop = row[-2]
                    hdop = row[-3]
                    vdop = row[-4]
                    dop_log.append([time,ping,pdop,hdop,vdop])
            prev_row = row
        return dop_log
        
    def extract_soundings(self, metadata):
        # Function to extract soundings from GLL, RMC, GGA, DEPTH messages
        sounding_log = []
        print(metadata)
        
        ant_off = metadata['GNSS'][2]
        sonar_off = metadata['Sonar'][2]
        
        prev_row, time, lat, long, ant_elip_height, hdg, speed, hdop, water_depth, bottom_elip_height, soundspeed\
            = None, None, None, None, None, None, None, None, None, None, None
        sounding_number = 0
        for row in self.raw_log_read:
            try:
                if row[1] == '$GNRMC':
                    time, lat, long = self.get_time_lat_long(row, 2, 4, 6)
                    speed = row[8]
                    hdg = row[9]
                elif row[1] == '$GNGGA':
                    time, lat, long = self.get_time_lat_long(row, 2, 3, 5)
                    hdop = row [9]
                    ant_height = row[10]
                    sep = row[12]
                    ant_elip_height = round((ant_height + sep), 3)
                elif row[1] == '$DEPTH':
                    if prev_row[1] == '$GNGLL':
                        pass
                    elif prev_row[1] == '$GNGGA':
                        water_depth = -row[2]/1000+sonar_off
                        bottom_elip_height = ant_elip_height-ant_off+water_depth
                        soundspeed = row[-1]
                        sounding_log.append([time, sounding_number, lat, long, ant_elip_height, hdg, speed, 
                                             hdop, water_depth, bottom_elip_height, soundspeed])
                        sounding_number += 1
                prev_row = row
                
            except:
                pass
        return sounding_log
    
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
class Clean_Soundings:
# Class to manage 
    def __init__(self, soundings):
        self.soundings = soundings
        self.clean_soundings()
        
    def pull_items(self):
        self.ping = []
        self.old_depth = []
        self.new_depth = []
        self.old_speed = []
        self.new_speed = []
        for row in self.soundings:
            self.ping.append(row[1])
            self.old_depth.append(row[-4])
            self.new_depth.append(row[-2])
            self.old_speed.append(row[-3])
            self.new_speed.append(row[-1])
    
    def plot_data(self):
        if self.right-self.left <= 100:
            plt.scatter(self.ping, self.new_depth, label="Ping")
        plt.plot(self.ping, self.new_depth, color='red', 
                 linewidth=1, linestyle='solid', label="Corrected Depth")
        #plt.plot(self.ping, self.old_depth, color='red', 
                 #linewidth=1, linestyle='solid', label="Original")
        plt.axis([self.left, self.right, self.y_min-0.05, self.y_max+0.05])
        plt.title("Corrected Depth")
        plt.xlabel("Ping Number")
        plt.legend()
        plt.ylabel("Depth [m]")
        plt.gcf().set_dpi(300)
        plt.grid()
        plt.show()
    
    def clean_soundings(self):
    # Function to allow plotting and cleaning of data
        self.pull_items()
        self.y_min = min(self.new_depth)
        self.y_max = max(self.new_depth)
        self.left = min(self.ping)
        self.right = max(self.ping)
        self.plot_data()
        
        new_soundings = self.soundings
        while True:
            print('-------------------------------------------------')
            print('Please enter ping numbers for the desired left and right extents to zoom')
            self.left = input('Enter left extent: ')
            self.right = input('Enter right extent: ')
            
            try:
                self.left = int(self.left)
            except:
                pass
            try:
                self.right = int(self.right)
            except:
                pass
            
            if self.left == 'min':
                self.left = int(min(self.ping))
            if self.right == 'max':
                self.right = int(max(self.ping))
            
            self.y_min = min(self.new_depth[self.left:self.right])
            self.y_max = max(self.new_depth[self.left:self.right])
            
            self.plot_data()
            
            print('Do you want to remove any soundings?')
            print('    - yes           (You will be asked to select a range of soundings)')
            print('    - no            (You will be able to change zoom again)')
            print('    - save          (Save the data as is)')
            print('    - exit          (Exit without saving)')
            selection = input('Enter your selection here: ')
            
            if selection == 'exit':
                return
            elif selection == 'no':
                pass
            elif selection == 'save':
                save_data(new_soundings)
            elif selection == 'yes':
                print('---------------------------------------------')
                print('Please enter the left and right pings to delete')
                left_delete = int(input('Leftmost ping to delete: '))
                right_delete = int(input('Rightmost ping to delete: '))+2
                
                delete_range = list(range(left_delete, right_delete, 1))
                
                mod_soundings = new_soundings
                
                ping = 0
                bad_pings = []
                
                for row in mod_soundings:
                    x = row[1]
                    count = 0
                    while count <= len(delete_range)-1:
                        if x == delete_range[count]:
                            bad_pings.append(ping)
                        count += 1
                    ping += 1
                
                new_soundings = []
                for row in mod_soundings[0:bad_pings[0]]:
                    new_soundings.append(row)
                for row in mod_soundings[bad_pings[-1]:-1]:
                    new_soundings.append(row)
                
                self.soundings = new_soundings
                self.pull_items()

                self.plot_data()
                    
#-----------------------------------------------------------------------------

#########################################
#########################################
# Miscelaneous applications
#########################################
#########################################

#-----------------------------------------------------------------------------
def file_check(filename, ending):
    # Checks if the filename exist and if they end in .csv
    if filename.endswith(ending):
        return True
    else:
        print('File does not end in ".csv"')
        return False
    filexists = os.path.isfile(filename)
    if not filexists:
        print('File not found!')
        return False
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
def osp_logo():
    # This function just prints the OSP logo out
    print('')
    print('  /$$$$$$   /$$$$$$  /$$$$$$$ ')
    print(' /$$__  $$ /$$__  $$| $$__  $$')
    print('| $$  \ $$| $$  \__/| $$  \ $$')
    print('| $$  | $$|  $$$$$$ | $$$$$$$/')
    print('| $$  | $$ \____  $$| $$____/ ')
    print('| $$  | $$ /$$  \ $$| $$      ')
    print('|  $$$$$$/|  $$$$$$/| $$      ')
    print(' \______/  \______/ |__/  ')
    print('')

#-----------------------------------------------------------------------------

def smile():
    print('')
    print("  , ; ,   .-'''''-.    , ; ,")
    print("  \\|/  .'         '.  \|//")
    print("   \-;-/   ()   ()   \-;-/")
    print("   // ;               ; \\")
    print("  //__; :.         .; ;__\\")
    print(" `-----\'.'-.....-'.'/-----'")
    print("        '.'.-.-,_.'.'")
    print("          '(  (..-'")
    print("            '-'")
    print('')
                              
                              
