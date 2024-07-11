from pylsl import StreamInfo, StreamOutlet, local_clock
import asyncio
import aioconsole 
import os
import signal
import sys
import getopt

from bleak import BleakClient
from bleak.uuids import uuid16_dict
import time
import numpy as np
import math
import datetime
import pandas as pd
import csv

""" Predefined UUID (Universal Unique Identifier) mapping are based on Heart Rate GATT service Protocol that most
Fitness/Heart Rate device manufacturer follow (Polar H10 in this case) to obtain a specific response input from 
the device acting as an API """

uuid16_dict = {v: k for k, v in uuid16_dict.items()}

## UUID for model number ##
MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Model Number String")
)


## UUID for manufacturer name ##
MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Manufacturer Name String")
)

## UUID for battery level ##
BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)

## UUID for connection establishment with device ##
PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of stream settings ##
PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of start stream ##
PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of ECG Stream ##
ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
ACC_WRITE = bytearray([0x02, 0x02, 0x00, 0x01, 0xC8, 0x00, 0x01, 0x01, 0x10, 0x00, 0x02, 0x01, 0x08, 0x00])
HR_DISABLE = bytearray([0x00, 0x00])
## For Polar H10  sampling frequency ##
ECG_SAMPLING_FREQ = 130
#ECG_SAMPLING_FREQ = 256
ACC_SAMPLING_FREQ = 200
ibi_SAMPLING_FREQ = 1000
PMD_CHAR1_UUID = "fb005c81-02e7-f387-1cad-8acd2d8df0c8" #read, write, indicate – Request stream settings?
PMD_CHAR2_UUID = "fb005c82-02e7-f387-1cad-8acd2d8df0c8"

U1_CHAR2_UUID = "6217ff4d-91bb-91d0-7e2a-7cd3bda8a1f3"      # write-without-response, indicate

HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb" 

#äOUTLET_ECG = []
#OUTLET_ACC = []
#OUTLET_ibi = []
acc_stream_values = []
acc_stream_times = []
ibi_stream_values = []
ibi_stream_times = []

def StartStream(STREAMNAME):
#-----------ECG--------------------------
    info_ECG = StreamInfo(STREAMNAME, 'ECG', 1,ECG_SAMPLING_FREQ, 'float32', 'myuid2424')

    info_ECG.desc().append_child_value("manufacturer", "Polar")
    channels = info_ECG.desc().append_child("channels")
    for c in ["ECG"]:
        channels.append_child("channel")\
            .append_child_value("name", c)\
            .append_child_value("unit", "microvolts")\
            .append_child_value("type", "ECG")

#-----------ACCELEROMETRO--------------------------
# possibile altro nome 'Mocap'            

    info_ACC = StreamInfo(STREAMNAME, 'ACC', 3, ACC_SAMPLING_FREQ, 'float32', 'myuid2424')
    
    info_ACC.desc().append_child_value("manufacturer", "Polar")
    channels = info_ECG.desc().append_child("channels")
    for c in ['X','Y','Z']:
            channels.append_child("channel")\
                .append_child_value("label", c)\
                .append_child_value("unit", "microvolts")\
                .append_child_value("type", "ACC")
                
    #outlet = StreamOutlet(info_ACC)
        
#------------R-R----------------   
#possibile altro nome 'Misc'

    info_ibi = StreamInfo(STREAMNAME, 'HR', 1, ibi_SAMPLING_FREQ, 'float32', 'myuid2424')
    info_ibi.desc().append_child_value("manufacturer", "Polar")
    channels = info_ibi.desc().append_child("channels")
    for c in ["ibi"]:
                channels.append_child("channel")\
                    .append_child_value("name", c)\
                    .append_child_value("unit", "microvolts")\
                    .append_child_value("type", "HR")
        # next make an outlet; we set the transmission chunk size to 74 samples and
        # the outgoing buffer size to 360 seconds (max.)
        #return StreamOutlet(info, 74, 360)
        
#---------------outlets------------        
    outlet_ECG = StreamOutlet(info_ECG)
    outlet_ACC = StreamOutlet(info_ACC)
    outlet_ibi = StreamOutlet(info_ibi)
    return outlet_ECG, outlet_ACC, outlet_ibi
    
    # next make an outlet; we set the transmission chunk size to 74 samples and
    # the outgoing buffer size to 360 seconds (max.)
    #return StreamOutlet(info, 74, 360)
 #   return StreamOutlet(info_ACC, 0, 360)
 #   return StreamOutlet(info_ibi, 0, 360)


## Bit conversion of the Hexadecimal stream
def create_data_conv(outlet_ECG, outlet_ACC, outlet_ibi):
  
  
    def data_conv(sender, data: bytearray):
    #global OUTLET
      with open(filename, 'a', newline="") as f:
        #if data[0] == 0x00:
           # print(".", end = '', flush=True)
         #   step = 3
         #   samples = data[10:]
         #   offset = 0
         #   while offset < len(samples):
          #      ecg = convert_array_to_signed_int(samples, offset, step)
          #      offset += step
          #      outlet_ECG.push_sample([ecg])
    #            print("ecco l'ecg':")
     #           print(ecg)
    
    #    if data[0] == 0x02:
     #       if not bool(acc_stream_values):
      #          acc_stream_start_time = time.time_ns()/1.0e9
        
      #      timestamp = convert_to_unsigned_long(data, 1, 8)/1.0e9 # timestamp of the last sample
      #      frame_type = data[9]
      #      resolution = (frame_type + 1) * 8 # 16 bit
      #      time_step = 0.005 # 200 Hz sample rate
      #      step = math.ceil(resolution / 8.0)
      #      samples = data[10:] 
      #      n_samples = math.floor(len(samples)/(step*3))
      #      sample_timestamp = timestamp - (n_samples-1)*time_step
      #      offset = 0
      #      while offset < len(samples):
      #          x = convert_array_to_signed_int(samples, offset, step)
      #          offset += step
      #          y = convert_array_to_signed_int(samples, offset, step) 
      #          offset += step
      #          z = convert_array_to_signed_int(samples, offset, step) 
      #          offset += step
            # mag = np.linalg.norm([x, y, z])
            #acc_stream_values.extend([[x, y, z]])
            #acc_stream_times.extend([sample_timestamp])
            #sample_timestamp += time_step
                #outlet_ACC.push_sample([x])
      #          outlet_ACC.push_sample([x, y, z])
            #num_channels = OUTLET_ACC.info().channel_count()
 #ä               print("ecco la z")
  #              print(x)
    
        byte0 = data[0] # heart rate format
    #print(byte0)
        uint8_format = (byte0 & 1) == 0
        energy_expenditure = ((byte0 >> 3) & 1) == 1
        rr_interval = ((byte0 >> 4) & 1) == 1
        
        if not rr_interval:
            return

        first_rr_byte = 2
        if uint8_format:
            hr = data[1]
            pass
        else:
            hr = (data[2] << 8) | data[1] # uint16
            first_rr_byte += 1
    
        if energy_expenditure:
            ee = (data[first_rr_byte + 1] << 8) | data[first_rr_byte]
            first_rr_byte += 2

        for i in range(first_rr_byte, len(data), 2):
            ibi = (data[i + 1] << 8) | data[i]
        # Polar H7, H9, and H10 record IBIs in 1/1024 seconds format.
        # Convert 1/1024 sec format to milliseconds.
        # TODO: move conversion to model and only convert if sensor doesn't
        # transmit data in milliseconds.
            ibi = np.ceil(ibi / 1024 * 1000)
            ibi_stream_values.extend([ibi])
            ibi_stream_times.extend([time.time_ns()/1.0e9])
            ibi_stream_values_string = ' '.join(map(str, ibi_stream_values))
            outlet_ibi.push_sample([ibi])
            timestamp_local = local_clock() * 1000
            
            current_datetime = datetime.datetime.now()
            year = current_datetime.year
            month = current_datetime.month        
            day = current_datetime.day
            hour = current_datetime.hour
            minute = current_datetime.minute
            second = current_datetime.second
            millisecond = current_datetime.microsecond // 1000
            timestamp_true = datetime.datetime.now().timestamp()
            #ecg_sample, ecg_timestamp = outlet_ECG.push_sample([ecg])
            #ibi_df = pd.DataFrame([[ibi, timestamp_local, year, month, day, hour, minute, second, millisecond, timestamp_true]], columns=['ibi', 'timestamp local', "year", "month", "day", "hour", "minute", "second", "millisecond", "timestamp",])
   #         filename = f"dati_IBI_{date_str}_subject{subject_number}_task{task_number}.csv"
           # with open(filename, 'a', newline="") as f:
                #ibi_df.to_csv(f, header=False, index=False)
            writer = csv.writer(f)
            writer.writerow(['ibi', 'timestamp local', "year", "month", "day", "hour", "minute", "second", "millisecond", "timestamp"])
            writer.writerow([ibi, timestamp_local, year, month, day, hour, minute, second, millisecond, timestamp_true])
          #      if os.stat(filename).st_size == 0:
           #         ibi_df.to_csv(f, header=True, index=False)
            #    else:
             #       ibi_df.to_csv(f, header=False, index=False)
              #  os.fsync(f.fileno())
            print("ecco gli ibi:")
            print(ibi)
      #  OUTLET_ibi.push_sample([ibi_stream_values])
    return data_conv

def convert_array_to_signed_int(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset : offset + length]), byteorder="little", signed=True,
    )


def convert_to_unsigned_long(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset : offset + length]), byteorder="little", signed=False,
    )


## ASynchronous task to start the data stream for ECG ##
async def run(client, debug=False):
    data_conv = create_data_conv(OUTLET_ECG, OUTLET_ACC, OUTLET_ibi)

    print("---------Looking for Device------------ ", flush=True)

    await client.is_connected()
    print("---------Device connected--------------", flush=True)

    model_number = await client.read_gatt_char(MODEL_NBR_UUID)
    print("Model Number: {0}".format("".join(map(chr, model_number))), flush=True)

    manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
    print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))), flush=True)

    battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
    print("Battery Level: {0}%".format(int(battery_level[0])), flush=True)

    
    await client.read_gatt_char(PMD_CONTROL)
    print("Collecting GATT data...", flush=True)

    await client.write_gatt_char(PMD_CONTROL, ECG_WRITE)
    print("Writing GATT data...", flush=True)

    

    ## ECG stream started
    await client.start_notify(PMD_DATA, data_conv)
    
    await client.write_gatt_char(PMD_CHAR1_UUID, ACC_WRITE, response=True)
    await client.start_notify(PMD_CHAR2_UUID, data_conv)
    print("Collecting ACC data...", flush=True)

    await client.start_notify(HEART_RATE_MEASUREMENT_UUID, data_conv)
    print("Collecting HR data...", flush=True)



    print("Collecting ECG data...", flush=True)

    await aioconsole.ainput('Running: Press a key to quit')
    await client.stop_notify(PMD_DATA)
    await client.stop_notify(U1_CHAR2_UUID)
    print("Stopping ECG and ACC data...", flush=True)
    await client.stop_notify(HEART_RATE_MEASUREMENT_UUID)
    print("Stopping HR data...", flush=True)
    print("[CLOSED] application closed.", flush=True)
    sys.exit(0)


async def main(ADDRESS, OUTLET):
    try:
        async with BleakClient(ADDRESS) as client:
            tasks = [
                asyncio.ensure_future(run(client, True)),
            ]

            await asyncio.gather(*tasks)
    except:
        pass


if __name__ == "__main__":
    date_str = input("Enter the date (YYYY-MM-DD): ")
    subject_number = input("Enter the subject number: ")
    task_number = input("Enter the task number: ")
    filename = f"dati_IBI_{date_str}_subject{subject_number}_task{task_number}.csv"
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:s:",["ADDRESS=","STREAMNAME="])
    except getopt.GetoptError:
        print ('Polar2LSL.py -a <MACADDRESS> -s <STREAMNAME>', flush=True)
        sys.exit(2)
    # Defaults:
    STREAMNAME = 'PolarBand'
    ADDRESS = "e7:14:d8:97:23:3f"
    #"f4:da:91:fe:5c:15"
    #"fe:f6:99:da:85:08"
    #ADDRESS = "C7:4C:DA:51:37:51"
    #ADDRESS = "C9:09:F1:4C:AA:4D"
    
    for opt, arg in opts:
        if opt == '-h':
            print ('Polar2LSL.py -a <MACADDRESS> -s <STREAMNAME>', flush=True)
            sys.exit()
        elif opt in ("-a", "--ADDRESS"):
            ADDRESS = arg
        elif opt in ("-s", "--STREAMNAME"):
            STREAMNAME = arg
            
    print ('MACADDRESS is ', ADDRESS, flush=True)
    print ('STREAMNAME is ', STREAMNAME, flush=True)

    OUTLET_ECG, OUTLET_ACC, OUTLET_ibi = StartStream(STREAMNAME)
   # OUTLET_ACC = StartStream(STREAMNAME)
   # OUTLET_ibi = StartStream(STREAMNAME)
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(ADDRESS, OUTLET_ECG))
