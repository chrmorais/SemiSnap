'''
Created on July 27, 2014

[Copyright (c) 2014 Josh Willhite]
Repository: https://github.com/Josh-Willhite/SemiSnap Email: jwillhite@gmail.com

This program is released under the MIT license. See the COPYING file for terms.
'''

import numpy as np
from scipy import stats
import cv2
import subprocess
import time
from time import strftime
from Queue import Queue
from collections import deque
import threading
from tweet_image import post_vehicle_image


thresh_q = deque(maxlen=500)
trigger_level = .25
min_img_cap_time = 1.5

img_write_q = Queue()


def get_threshold():
    mean_list = [val for val in thresh_q]
    return stats.mode(mean_list)[0][0]


def diff(c, b, a):
    d1 = cv2.absdiff(a, b)
    d2 = cv2.absdiff(b, c)
    background_removed = cv2.bitwise_and(d1, d2)
    return background_removed, cv2.mean(background_removed)


def getROI(frame, diff_frame):
    #TODO just grab area of movement for analysis

    ret,thresh2 = cv2.threshold(frame,20,255,cv2.THRESH_BINARY_INV)
    moments = cv2.moments(frame)
    print moments['m00']

    width = np.size(frame, 1)
    height = np.size(frame, 0)

    #select upper portion of frame
    x0 = 0
    y0 = 0
    x1 = width
    y1 = height/2

    #return frame[y0:y1, x0:x1]

def set_camera(cap):
    cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, 97/255.0)
    cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 112/255.0)
    cap.set(cv2.cv.CV_CAP_PROP_SATURATION, 255/255.0)

def snap():
    cap = cv2.VideoCapture(0)
    set_camera(cap)

    raw = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
    a = raw
    b = raw
    last_time = time.time()

    while True:
        curr_time = time.time()
        raw = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)
        c = b
        b = a
        a = raw

        d = diff(c,b,a)

        try:
            curr_mode = get_threshold()
        except:
            curr_mode = .5

        curr_threshold = curr_mode + trigger_level * curr_mode

        cv2.imshow('basic', raw)

        if d[1][0] > curr_threshold and len(thresh_q) > 100 and (curr_time - last_time) > min_img_cap_time:
            last_time = curr_time
            text_color = (0, 0, 0)
            cv2.putText(raw, strftime("%a, %d %b %Y %H:%M:%S"), (0, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, text_color)
            cv2.imshow('movement', d[0])
            #img_write_q.put(raw)
        else:
            thresh_q.append(round(d[1][0], 2))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def write_img():
    while True:
        if not img_write_q.empty():
            frame = img_write_q.get()
            cv2.imwrite('./images/%s.png' % time.time(), frame)


if __name__ == '__main__':
    cv_thread = threading.Thread(target=snap).start()
    #write_thread = threading.Thread(target=write_img).start()

'''
    tweet_thread = threading.Thread(target=post_vehicle_image())
    write_thread.start()
'''