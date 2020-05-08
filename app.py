# This is part of Master degree theses
# which take Video file to process it later

import cv2
import datetime


import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import butter, freqz, lfilter
from scipy.fft import fft, fftfreq, fftshift
import scipy.fftpack


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def split_rgb(roi):
    # image[:, :, 0] is R channel, replace the rest by 0.
    imgLeftHand_R = roi.copy()
    imgLeftHand_R[:, :, 1:3] = 0
    # image[:, :, 1] is G channel, replace the rest by 0.
    imgLeftHand_G = roi.copy()
    imgLeftHand_G[:, :, [0, 2]] = 0
    # image[:, :, 2] is B channel, replace the rest by 0.
    imgLeftHand_B = roi.copy()
    imgLeftHand_B[:, :, 0:2] = 0
    return imgLeftHand_R, imgLeftHand_G, imgLeftHand_B


# cam init
hands_cam0 = cv2.VideoCapture(0)

legs_cam1 = cv2.VideoCapture(1)
legs_cam1.set(15, -2.0)

# font for time stamp
font = cv2.FONT_HERSHEY_SIMPLEX

# recording init
file_name_hands = 'Recordings/Hands_0.avi'
file_name_legs = 'Recordings/Legs_0.avi'
frame_width = int(hands_cam0.get(3))
frame_height = int(hands_cam0.get(4))
out_hands = cv2.VideoWriter(file_name_hands, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                            15, (frame_width, frame_height))
out_legs = cv2.VideoWriter(file_name_legs, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                           15, (frame_width, frame_height))

# flag for info about starting recording
start_flag_hands = False
start_flag_legs = False

# ExG samples table
Exg_samples = []


# slider to adjust image parameters
def empty(a):
    pass


track_bar_name = "Skin color setup"
cv2.namedWindow("Skin color setup")
cv2.resizeWindow(track_bar_name, 640, 240)
cv2.createTrackbar("Hue Min", track_bar_name, 0, 179, empty)
cv2.createTrackbar("Hue Max", track_bar_name, 77, 179, empty)
cv2.createTrackbar("Sat Min", track_bar_name, 88, 255, empty)
cv2.createTrackbar("Sat Max", track_bar_name, 193, 255, empty)
cv2.createTrackbar("Val Min", track_bar_name, 71, 255, empty)
cv2.createTrackbar("Val Max", track_bar_name, 255, 255, empty)

while True:
    cam0_is_connected, hands_frame = hands_cam0.read()
    cam1_is_connected, legs_frame = legs_cam1.read()

    if cam0_is_connected:
        # Checking if recording is ON
        if not start_flag_hands:
            print('Cam 0 -> ON AIR')
            start_flag_hands = True

        # time for synchronise recordings
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")

        # making mask due to sliders position
        frame0HSV = cv2.cvtColor(hands_frame, cv2.COLOR_BGR2HSV)

        h_min = cv2.getTrackbarPos("Hue Min", track_bar_name)
        h_max = cv2.getTrackbarPos("Hue Max", track_bar_name)
        s_min = cv2.getTrackbarPos("Sat Min", track_bar_name)
        s_max = cv2.getTrackbarPos("Sat Max", track_bar_name)
        v_min = cv2.getTrackbarPos("Val Min", track_bar_name)
        v_max = cv2.getTrackbarPos("Val Max", track_bar_name)
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(frame0HSV, lower, upper)

        # Adding mask to image
        hands_frame = cv2.bitwise_and(hands_frame, hands_frame, mask=mask)

        # add time stamp
        hands_frame = cv2.putText(hands_frame, current_time, (10, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # ROI to later processing
        right_hand_ROI = hands_frame[200:330, 70:200]
        left_hand_ROI = hands_frame[200:330, 440:570]

        # Taking VPG signal (ExG method)
        imgLeftHand_R, imgLeftHand_G, imgLeftHand_B = split_rgb(left_hand_ROI)

        sum_G = 0
        sum_R = 0
        sum_B = 0
        div = 0
        width = 130
        height = 130
        for row in range(width):
            for col in range(height):
                if imgLeftHand_G[row, col, 1] != 0 and imgLeftHand_R[row, col, 0] != 0 and imgLeftHand_B[row, col, 2] != 0:
                    sum_G += imgLeftHand_G[row, col, 1]
                    sum_R += imgLeftHand_R[row, col, 0]
                    sum_B += imgLeftHand_B[row, col, 2]
                    div += 1
        percentage = int((div * 100) / (130 * 130))
        print(f'{percentage} %')

        if percentage < 60:
            hands_frame = cv2.putText(hands_frame, "STOP", (200, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            hands_frame = cv2.putText(hands_frame, "START", (200, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
            if sum_B + sum_G + sum_R != 0:
                r = sum_R/(sum_G + sum_R + sum_B)
                g = sum_G/(sum_G + sum_R + sum_B)
                b = sum_B/(sum_G + sum_R + sum_B)

                ExG = 2 * g - r - b
                Exg_samples.append(ExG)

        hands_frame = cv2.rectangle(hands_frame, (70, 200), (200, 330), (255, 0, 0), 2)
        hands_frame = cv2.rectangle(hands_frame, (440, 200), (570, 330), (255, 0, 0), 2)

        out_hands.write(hands_frame)

        cv2.imshow(file_name_hands, hands_frame)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # same for cam1
    if cam1_is_connected:
        if not start_flag_legs:
            print('Cam 1 -> ON AIR')
            start_flag_legs = True
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        legs_frame = cv2.bitwise_and(legs_frame, legs_frame, mask=mask)
        legs_frame = cv2.putText(legs_frame, current_time, (10, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
        right_leg_ROI = legs_frame[200:330, 70:200]
        left_leg_ROI = legs_frame[200:330, 440:570]
        legs_frame = cv2.rectangle(legs_frame, (70, 200), (200, 330), (255, 0, 0), 2)
        legs_frame = cv2.rectangle(legs_frame, (440, 200), (570, 330), (255, 0, 0), 2)
        out_legs.write(legs_frame)
        cv2.imshow(file_name_legs, legs_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the video capture and video write objects
hands_cam0.release()
out_hands.release()

# Closes all the frames
cv2.destroyAllWindows()

# VPG signal processing
signal = Exg_samples
N = len(signal)
Fs = 15.0
T = 1.0 / Fs
N_fft = 512
t = np.linspace(0, N*T, N)
y = signal

plt.figure(1)
plt.plot(t, signal)
y = butter_bandpass_filter(signal, 0.583, 3, 15, order=2)
plt.plot(t, y)
plt.xlabel('Time(s)')
plt.title('VPG signal')
plt.show()

mean_removed = np.ones_like(y)*np.mean(y)
y = y - mean_removed

# Calculate fft
yf = fft(y, n=N_fft)
xf = np.arange(0, Fs, Fs/N_fft)


# Plot the fft #
plt.figure(2)
ax = plt.subplot(111)
pt, = ax.plot(xf, np.abs(yf), lw=2.0, c='b')
p = plt.Rectangle((Fs/2, 0), Fs/2, ax.get_ylim()[1], facecolor="grey", fill=True, alpha=0.75, hatch="/", zorder=3)
ax.add_patch(p)
ax.set_xlim((ax.get_xlim()[0], Fs))
ax.set_title('FFT', fontsize=16, fontweight="bold")
ax.set_ylabel('FFT magnitude (power)')
ax.set_xlabel('Frequency (Hz)')
plt.legend((p,), ('mirrored',))
ax.grid()
plt.show()






