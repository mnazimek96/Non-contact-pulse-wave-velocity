# This is part of Master degree theses
# which take Video file to process it later

import cv2
import datetime

# cam init
hands_cam0 = cv2.VideoCapture(0)
legs_cam1 = cv2.VideoCapture(1)

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

        # add time stamp
        hands_frame = cv2.putText(hands_frame, current_time, (10, 50), font, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # ROI to later processing
        right_hand_ROI = hands_frame[200:330, 70:200]
        left_hand_ROI = hands_frame[200:330, 440:570]

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
