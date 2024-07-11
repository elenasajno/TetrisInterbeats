# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 12:57:59 2023

@author: amary
"""

################################
#
#   Record video from webcam
#
#             by
#
#      Code Monkey King
#
################################

# packages
import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc
import time
import datetime
import pylsl



# ctypes required for using GetTickCount64()
import ctypes
 
# getting the library in which GetTickCount64() resides
lib = ctypes.windll.kernel32
 

date_str = input("Enter the date (YYYY-MM-DD): ")
subject_number = input("Enter the subject number: ")
task_number = input("Enter the task number: ")

# open the webcam video stream
webcam = cv2.VideoCapture(0)

# open output video file stream
filename = f"video_recrding_{date_str}_subject{subject_number}_task{task_number}.mp4"
video = VideoWriter(filename, VideoWriter_fourcc(*'MP42'), 25.0, (640, 480))

# main loop
while True:
    # get the frame from the webcam
    stream_ok, frame = webcam.read()
    
    # if webcam stream is ok
    if stream_ok:
        # display current frame
        cv2.imshow('Webcam', frame)
        
        # write frame to the video file
 #       video.write(frame)
 #       screenshot = cv2.cvtColor(np.array(pg.screenshot()), cv2.COLOR_RGB2BGR)

        # Add timestamp overlay
        timestamp = time.time()
       # timestamp2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        


        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        milliseconds = current_time.microsecond // 1000  # Retrieve milliseconds and convert to integer
        # calling the function and storing the return value
        tick = lib.GetTickCount64()
        local_time = pylsl.local_clock() 
        # since the time is in milliseconds i.e. 1000 * seconds
        # therefore truncating the value
        tick = int(str(tick))

        formatted_time_with_ms = f"{formatted_time}.{milliseconds:03d}"
        
        
        # Convert tick to string and concatenate with the other strings
        tick_str = str(tick)
        local_time_str = str(local_time)

        #print(formatted_time_with_ms)
        
        
        timestamp_str = "{:.7f}".format(timestamp)
        
        cv2.putText(frame, timestamp_str+" "+tick_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, formatted_time_with_ms+" "+local_time_str, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
      #  cv2.putText(frame, formatted_time_with_ms, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Write video frame
        video.write(frame)

    # escape condition
    if cv2.waitKey(1) & 0xFF == 27: break

# clean ups
cv2.destroyAllWindows()

# release web camera stream
webcam.release()

# release video output file stream
video.release()