# ---------------------------------------------------------------------------
# Copyright 2017-2018  OMRON Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------------------------
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import p2def
from serial_connector import SerialConnector
from hvc_p2_wrapper import HVCP2Wrapper
from hvc_tracking_result import HVCTrackingResult
from hvc_tracking_result_c import C_FACE_RES35, C_BODY_RES35
from hvc_result import HVCResult
from hvc_result_c import C_FRAME_RESULT
from stb import STB
from grayscale_image import GrayscaleImage

WINDOWS_STB_LIB_NAME = 'libSTB.dll'
LINUX_STB_LIB_NAME = './libSTB.so'

class HVCP2Api(object):
    """ This class provide python full API for HVC-P2(B5T-007001) with STB library.
    """
    __slots__ = ['use_stb', '_stb', '_hvc_p2_wrapper', '_exec_func']
    def __init__(self, connector, exec_func, use_stabilizer):
        """Constructor

        Args:
            connector (SerialConnector): serial connector
            exec_func (int): functions flag to be executed
                              (e.g. p2def.EX_FACE | p2def.EX_AGE )
            use_stb (bool): use STB library

        Returns:
            void

        """
        self._hvc_p2_wrapper = HVCP2Wrapper(connector)

        # Disable to use STB if using Hand detection only.
        if use_stabilizer == p2def.USE_STB_ON and exec_func == p2def.EX_HAND:
            _use_stb = p2def.USE_STB_OFF
        else:
            _use_stb = use_stabilizer
        self.use_stb = _use_stb

        # Adds face flag if using facial estimation function
        if exec_func & (p2def.EX_DIRECTION\
                      | p2def.EX_AGE\
                      | p2def.EX_GENDER\
                      | p2def.EX_GAZE\
                      | p2def.EX_BLINK\
                      | p2def.EX_RECOGNITION\
                      | p2def.EX_EXPRESSION):
            exec_func |= p2def.EX_FACE + p2def.EX_DIRECTION

        self._exec_func = exec_func

        os = sys.platform
        if os == 'win32':
            stb_lib_name = WINDOWS_STB_LIB_NAME
        elif 'linux':
            stb_lib_name = LINUX_STB_LIB_NAME
        else:
            raise 'Error: Unsupported OS.'

        if self.use_stb:
            self._stb = STB(stb_lib_name, exec_func)

    def connect(self, com_port, baudrate, timeout):
        """Connects to HVC-P2 by COM port via USB or UART interface.

        Args:
            com_port (str): COM port ('COM3', '/dev/ttyACM0' etc. )
            baudrate (int): baudrate (9600/38400/115200/230400/460800/921600)
            timeout  (int): timeout period(sec) for serial communication

        Returns:
            bool: status

        """
        return self._hvc_p2_wrapper.connect(com_port, baudrate, timeout)

    def disconnect(self):
        """Disconnects to HVC-P2.

        Args:
            void

        Returns:
            void

        """
        return self._hvc_p2_wrapper.disconnect()

    def get_version(self):
        """Gets the device's model name, version and revision.

        Args:
            void

        Returns:
            tuple of (response_code, hvc_type, major, minor, release, revision)
                response_code (int): response code from B5T-007001.
                hvc_type (str): model name(12 characters) "B5T-007001  "
                major    (int): major version number.
                minor    (int): minor version number.
                release  (int): release number.
                revision (int): revision number.

        """
        return self._hvc_p2_wrapper.get_version()

    def set_camera_angle(self, camera_angle):
        """Sets camera angle.

        Args:
            camera_angle (int): the angle used when facing the camera
                    HVC_CAM_ANGLE_0   (00h):   0 degree
                    HVC_CAM_ANGLE_90  (01h):  90 degree
                    HVC_CAM_ANGEL_180 (02h): 180 degree
                    HVC_CAM_ANGEL_270 (03h): 270 degree

        Returns:
            int: response_code form B5T-007001.

        """
        return self._hvc_p2_wrapper.set_camera_angle(camera_angle)

    def get_camera_angle(self):
        """Gets camera angle.

        Args:
            void

        Returns:
            tuple of (response_code, camera_angle)
                response_code (int): response code form B5T-007001
                camera_angle (int): the angle used when facing the camera

        """
        return self._hvc_p2_wrapper.get_camera_angle()

    def execute(self, out_img_type, tracking_result, out_img):
        """Executes functions specified in the constructor.
         e.g. Face detection, Age estimation etc.

        Args:
            out_img_type (int): output image type
                OUT_IMG_TYPE_NONE  (00h): no image output
                OUT_IMG_TYPE_QVGA  (01h): 320x240 pixel resolution(QVGA)
                OUT_IMG_TYPE_QQVGA (02h): 160x120 pixel resolution(QQVGA)
            tracking_result (HVCTrackingResult): the tracking result is stored
            out_img (GrayscaleImage): output image

        Returns:
            tuple of (response_code, stb_return)
                response_code (int): response code form B5T-007001
                stb_return (bool): return status of STB library

        """
        frame_result = HVCResult()
        response_code = self._hvc_p2_wrapper.execute(self._exec_func,\
                                           out_img_type, frame_result, out_img)

        tracking_result.clear()
        if self.use_stb and (self._exec_func != p2def.EX_NONE):
            stb_in = C_FRAME_RESULT()
            frame_result.export_to_C_FRAME_RESULT(stb_in)
            stb_out_f = C_FACE_RES35()
            stb_out_b = C_BODY_RES35()
            (stb_return, face_count, body_count) = self._stb.execute(stb_in,\
                                                                     stb_out_f,\
                                                                     stb_out_b)
            if stb_return < 0: # STB error
                return (response_code, stb_return)

            tracking_result.faces.append_C_FACE_RES35(self._exec_func,\
                                                      face_count, stb_out_f)

            if self._exec_func & p2def.EX_DIRECTION:
                tracking_result.faces.append_direction_list(frame_result.faces)

            if self._exec_func & p2def.EX_GAZE:
                tracking_result.faces.append_gaze_list(frame_result.faces)

            if self._exec_func & p2def.EX_BLINK:
                tracking_result.faces.append_blink_list(frame_result.faces)

            if self._exec_func & p2def.EX_EXPRESSION:
                tracking_result.faces.append_expression_list(frame_result.faces)

            tracking_result.bodies.append_BODY_RES35(self._exec_func,\
                                                     body_count, stb_out_b)
            tracking_result.hands.append_hand_list(frame_result.hands)
        else:
            tracking_result.appned_FRAME_RESULT(frame_result)
            stb_return = 0
        return (response_code, stb_return)

    def reset_tracking(self):
        """Resets tracking.
        Note:
            The tracking status will be cleared(i.e. TrackingID will be cleared),
            but other settings will not cleared.

        Args:
            void

        Returns:
            bool: return status

       """
        return self._stb.clear_stb_frame_results()


    def set_threshold(self, body_thresh, hand_thresh, face_thresh,\
                                                      recognition_thresh):
       """Sets the thresholds value for Human body detection, Hand detection,
           Face detection and/or Recongnition.

        Args:
            body_thresh (int):Threshold value for Human body detection[1-1000]
            hand_thresh (int):Threshold value for Hand detection[1-1000]
            face_thresh (int):Threshold value for Face detection[1-1000]
            recognition_thresh (int):Threshold value for Recognition[0-1000]

        Returns:
            int: response_code form B5T-007001.

       """
       return self._hvc_p2_wrapper.set_threshold(body_thresh, hand_thresh,\
                                                face_thresh, recognition_thresh)

    def get_threshold(self):
        """Gets the thresholds value for Human body detection, Hand detection,
           Face detection and/or Recongnition.

        Args:
            void

        Returns:
            tuple of (response_code,
                      body_thresh, hand_thresh, face_thresh, recognition_thresh)

        """
        return self._hvc_p2_wrapper.get_threshold()

    def set_detection_size(self, min_body, max_body, min_hand, max_hand,\
                           min_face, max_face):
        """Sets the detection size for Human body detection, Hand detection
           and/or Face detection

        Args:
            min_body (int): Minimum detection size for Human body detection
            max_body (int): Maximum detection size for Human body detection
            min_hand (int): Minimum detection size for Hand detection
            max_hand (int): Maximum detection size for Hand detection
            min_face (int): Minimum detection size for Face detection
            max_face (int): Maximum detection size for Face detection

        Returns:
            int: response_code form B5T-007001.
        """
        return self._hvc_p2_wrapper.set_detection_size(min_body, max_body,\
                                        min_hand, max_hand, min_face, max_face)

    def get_detection_size(self):
        """Gets the detection size for Human body detection, Hand detection
           and/or Face detection

        Args:
            void

        Returns:
            tuple of (response_code,
                     min_body, max_body, min_hand, max_hand, min_face, max_face)

        """
        return self._hvc_p2_wrapper.get_detection_size()

    def set_face_angle(self, yaw_angle, roll_angle):
        """Sets the face angle, i.e. the yaw angle range and the roll angle
           range for Face detection.

        Args:
            yaw_angle (int): face direction yaw angle range.
                    HVC_FACE_ANGLE_YAW_30 (00h): +/-30 degree (frontal face)
                    HVC_FACE_ANGLE_YAW_60 (01h): +/-60 degree (half-profile face)
                    HVC_FACE_ANGLE_YAW_90 (02h): +/-90 degree (profile face)
            roll_angle (int): face inclination roll angle range.
                    HVC_FACE_ANGLE_ROLL_15 (00h): +/-15 degree
                    HVC_FACE_ANGLE_ROLL_45 (01h): +/-45 degree

        Returns:
            int: response_code form B5T-007001.
      """
        return self._hvc_p2_wrapper.set_face_angle(yaw_angle, roll_angle)

    def get_face_angle(self):
        """Gets the face angle set for Face detection.

        Args:
            void

        Returns:
            tuple of (response_code, yaw_angle, roll_angle)
                response_code (int): response code form B5T-007001
                yaw_angle (int): face direction yaw angle range
                roll_angle (int): face inclination roll angle range

        """
        return self._hvc_p2_wrapper.get_face_angle()

    def set_uart_baudrate(self, baudrate):
        """Sets the UART baudrate.

        Note:
            The setting can be done when the USB is connected and will have
            no influence on the transmission speed as this is a command for UART
            connection.

        Args:
            baudrate (int): UART baudrate in bps.
                    (9600/38400/115200/230400/460800/921600)

        Returns:
            int: response_code form B5T-007001.

      """
        return self._hvc_p2_wrapper.set_uart_baudrate(baudrate)

   #==========================================================================
   # APIs for Album operation of Face recognition
   #==========================================================================
    def register_data(self, user_id, data_id, out_register_image):
        """Registers data for Recognition and gets a normalized image.

        Args:
            user_id (int): User ID [0-9]
            data_id (int): Data ID [0-99]
            out_register_image (GrayscaleImage): normalized face image

        Returns:
            int: response_code form B5T-007001.

      """
        return self._hvc_p2_wrapper.register_data(user_id, data_id,\
                                                  out_register_image)

    def delete_data(self, user_id, data_id):
        """Deletes a specified registered data. (Recognition)

        Args:
            user_id (int): User ID [0-9]
            data_id (int): Data ID [0-99]

        Returns:
            int: response_code form B5T-007001.

        """
        return self._hvc_p2_wrapper.delete_data(user_id, data_id)

    def delete_user(self, user_id):
        """Deletes a specified registerd user. (Recognition)

        Args:
            user_id (int): User ID [0-9]

        Returns:
            int: response_code form B5T-007001.

       """
        return self._hvc_p2_wrapper.delete_user(user_id)

    def delete_all_data(self):
        """Deletes all the registerd data. (Recognition)

        Args:
            void

        Returns:
            int: response_code form B5T-007001.

       """
        return self._hvc_p2_wrapper.delete_all_data()

    def get_user_data(self, user_id):
        """Gets the registration info of a specified user. (Recognition)
        i.e. the presence or absence of registered data, for the specified user.

        Args:
            user_id (int): User ID [0-9]

        Returns:
            tuple of (response_code, data_list)
                response_code (int): response_code form B5T-007001.
                data_list (list): data presence of registered data.

        """
        return self._hvc_p2_wrapper.get_user_data(user_id)

    def save_album(self):
        """Saves the album on the host side. (Recognition)

        Args:
            void

        Returns:
            tuple of (response_code, album)
                response_data (int): response_code form B5T-007001.
                album (str): album

        """
        return self._hvc_p2_wrapper.save_album()

    def load_album(self, album):
        """Loads the album on the host side. (Recognition)

        Args:
            album (str): album

        Returns:
            int: response_code form B5T-007001.

        """
        return self._hvc_p2_wrapper.load_album(album)

    def save_album_to_flash(self):
       """Saves the album on the flash ROM.  (Recognition)

        Note:
            The processing time will be longer if there is a lot of data.
            Album data already present on the flash ROM of the device will be
            overwritten.

        Args:
            void

        Returns:
            int: response_code form B5T-007001.

       """
       return self._hvc_p2_wrapper.save_album_to_flash()

    def reformat_flash(self):
        """Reformats the album save area on the flash ROM. (Recognition)

        Args:
            void

        Returns:
            int: response_code form B5T-007001.

        """
        return self._hvc_p2_wrapper.reformat_flash()

   #==========================================================================
   # APIs for STB library
   #==========================================================================
    def get_stb_version(self):
        """Gets the version number of STB library.

        Args:
             void

        Returns:
            tuple of (stb_return, major, minor)
                stb_return (int): return value of STB library
                major (int): major version number of STB library.
                minor (int): minor version number of STB library.

        """
        if self._stb is None:
            return

        return self._stb.get_stb_version()

    def set_stb_tr_retry_count(self, max_retry_count):
        """Sets maximum tracking retry count.

        Set the number of maximum retry when not finding a face/human body while
        tracking. Terminates tracking as lost object when keeps failing for this
        maximum retry count.

        Args:
            max_retry_count (int): maximum tracking retry count. [0-300]

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_tr_retry_count(max_retry_count)

    def get_stb_tr_retry_count(self):
        """Gets maximum retry count.

        Args:
            void

        Returns:
            tuple of (stb_return, max_retry)
                stb_return (int): return value of STB library
                max_retry_count (int): maximum tracking retry count.

       """
        return self._stb.get_stb_tr_retry_count()

    def set_stb_tr_steadiness_param(self, pos_steadiness_param,\
                                          size_steadiness_param):
        """Sets steadiness parameter of position and size.

        -- pos_steadiness_param
        For example, outputs the previous position coordinate data if the
        shifting measure is within 30%, existing position coordinate data if it
         has shift more than 30% when the rectangle position steadiness
         parameter has set as initial value of 30.

        -- size_steadiness_param
        For example, outputs the previous detecting size data if the changing
        measure is within 30%, existing size data if it has changed more than
        30% when the rectangle size steadiness parameter has set as initial
        value of 30.

        Args:
            pos_steadiness_param (int): rectangle position steadiness parameter
                                        [0-100]
            size_steadiness_param (int): rectangle size steadiness parameter
                                        [0-100]

        Returns:
            stb_return (int): return value of STB library

        """
        return self._stb.set_stb_tr_steadiness_param(pos_steadiness_param, \
                                                     size_steadiness_param)

    def get_stb_tr_steadiness_param(self):
        """Gets steadiness parameter of position and size.

        Args:
            void:

        Returns:
            tuple of (stb_return, pos_steadiness_param, size_steadiness_param)
                stb_return (int): return value of STB library
                pos_steadiness_param (int): rectangle position steadiness parameter
                size_steadiness_param (int): rectangle size steadiness parameter

       """
        return self._stb.get_stb_tr_steadiness_param()

    def set_stb_pe_threshold_use(self, threshold):
        """Sets estimation result stabilizing threshold value.

        Sets the stabilizing threshold value of Face direction confidence.
        Eliminates face data with lower confidence than the value set at this
        function for accuracy improvement of result stabilizing.
        For example, the previous data confidence with below 500 will not be
        applied for stabilizing when the face direction confidence threshold
        value has set as 500.

        * This is for the three functions of age, gender and face direction
          estimation functions.

        Args:
            threshold (int): face direction confidence threshold value.[0-1000]

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_pe_threshold_use(threshold)

    def get_stb_pe_threshold_use(self):
        """Gets estimation result stabilizing threshold value.

        Args:
            void

        Returns:
            tuple of (stb_return, threshold)
                stb_return (int): return value of STB library
                threshold (int): face direction confidence threshold value

       """
        return self._stb.get_stb_pe_threshold_use()

    def set_stb_pe_angle_use(self, min_UD_angle, max_UD_angle,
                                   min_LR_angle, max_LR_angle):
        """Sets estimation result stabilizing angle

        Sets angle threshold value of Face direction.

        Eliminates face data with out of the set angle at this function for
        accuracy improvement of result stabilizing.
        For example, the previous data with up-down angle of below -16 degree
        and over 21 degree will not be applied for stabilizing when the up-down

        * This is for the three functions of age, gender and face direction
          estimation functions.

        Args:
            min_UD_angle (int): minimum up-down angle of the face [-90 to 90]
            max_UD_angle (int): maximum up-down angle of the face [-90 to 90]
            min_LR_angle (int): minimum left-right angle of the face [-90 to 90]
            max_LR_angle (int): maximum left-right angle of the face [-90 to 90]

            min_UD_angle ≦ max_UD_angle
            min_LR_angle ≦ max_LR_angle

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_pe_angle_use(min_UD_angle, max_UD_angle,\
                                              min_LR_angle, max_LR_angle)

    def get_stb_pe_angle_use(self):
        """Gets estimation result stabilizing angle

        Args:
            void

        Returns:
            tuple of (stb_return, min_UD_angle, max_UD_angle,
                                  min_LR_angle, max_LR_angle)
                stb_return (int): return value of STB library
                min_UD_angle (int): minimum up-down angle of the face
                max_UD_angle (int): maximum up-down angle of the face
                min_LR_angle (int): minimum left-right angle of the face
                max_LR_angle (int): maximum left-right angle of the face

       """
        return self._stb.get_stb_pe_angle_use()

    def set_stb_pe_complete_frame_count(self, frame_count):
        """Sets age/gender estimation complete frame count

        Sets the number of previous frames applying to fix stabilization.
        The data used for stabilizing process (=averaging) is only the one
        fulfilled the set_stb_pe_threshold_use() and set_stb_pe_angle_use()
        condition.
        Stabilizing process will be completed with data more than the number of
        frames set at this function and it won't be done with less data.

        * This is for the two functions of age and gender estimation.

        Args:
            frame_count (int): the number of previous frames applying to fix
                               the result [1-20]

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_pe_complete_frame_count(frame_count)

    def get_stb_pe_complete_frame_count(self):
        """Gets age/gender estimation complete frame count.

        Args:
            void

        Returns:
            tuple of (stb_return, frame_count)
                stb_return (int): return value of STB library
                frame_count (int): the number of previous frames applying to fix
                                   the result

        """
        return self._stb.get_stb_pe_complete_frame_count()

    def set_stb_fr_threshold_use(self, threshold):
        """Sets recognition stabilizing threshold value

        Sets stabilizing threshold value of Face direction confidence to improve
        recognition stabilization.
        Eliminates face data with lower confidence than the value set at this
        function.
        For example, the previous data confidence with below 500 will not be
        applied for stabilizing when the face direction confidence threshold
        value has set as 500.

        Args:
            threshold (int): face direction confidence threshold value [0-1000]

        Returns:
            stb_return (int): return value of STB library

        """
        return self._stb.set_stb_fr_threshold_use(threshold)

    def get_stb_fr_threshold_use(self):
        """Gets recognition stabilizing threshold value

        Args:
            void

        Returns:
            tuple of (stb_return, threshold)
                stb_return (int): return value of STB library
                threshold (int): face direction confidence threshold value

        """
        return self._stb.get_stb_fr_threshold_use()

    def set_stb_fr_angle_use(self, min_UD_angle, max_UD_angle,\
                                   min_LR_angle, max_LR_angle):
        """Sets recognition stabilizing angle

        Sets angle threshold value of Face direction for accuracy improvement of
        recognition stabilizing.
        Eliminates face data with out of the set angle at this function.
        For example, the previous data with up-down angle of below -16degree and
        over 21 degree will not be applied for stabilizing when the up-down
        angle threshold value of Face direction has set as 15 for minimum and
        21 for maximum.

        Args:
            min_UD_angle (int): minimum up-down angle of the face [-90 to 90]
            max_UD_angle (int): maximum up-down angle of the face [-90 to 90]
            min_LR_angle (int): minimum left-right angle of the face [-90 to 90]
            max_LR_angle (int): maximum left-right angle of the face [-90 to 90]

            min_UD_angle ≦ max_UD_angle
            min_LR_angle ≦ max_LR_angle

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_fr_angle_use(min_UD_angle, max_UD_angle,\
                                              min_LR_angle, max_LR_angle)

    def get_stb_fr_angle_use(self):
        """Gets recognition stabilizing angle

        Args:
            void

        Returns:
            tuple of (stb_return, min_UD_angle, max_UD_angle,
                                  min_LR_angle, max_LR_angle)
                stb_return (int): return value of STB library
                min_UD_angle (int): minimum up-down angle of the face
                max_UD_angle (int): maximum up-down angle of the face
                min_LR_angle (int): minimum left-right angle of the face
                max_LR_angle (int): maximum left-right angle of the face

        """
        return self._stb.get_stb_fr_angle_use()

    def set_stb_fr_complete_frame_count(self, frame_count):
        """Sets recognition stabilizing complete frame count

        Sets the number of previous frames applying to fix the recognition
        stabilizing.
        The data used for stabilizing process (=averaging) is only the one
        fulfilled the STB_SetFrThresholdUse and STB_SetFrAngleUse condition.
        Stabilizing process will be completed with a recognition ID fulfilled
        seizing ratio in result fixing frames and will not be done without one.

        * Refer set_stb_fr_min_ratio function for account ratio function

        Args:
            frame_count (int): the number of previous frames applying to fix
                               the result. [0-20]

        Returns:
            stb_return (int): return value of STB library

        """
        return self._stb.set_stb_fr_complete_frame_count(frame_count)

    def get_stb_fr_complete_frame_count(self):
        """Gets recognition stabilizing complete frame count

        Args:
            void

        Returns:
            tuple of (stb_return, frame_count)
                stb_return (int): return value of STB library
                frame_count (int): the number of previous frames applying to fix
                                   the result. [0-20]

        """
        return self._stb.get_stb_fr_complete_frame_count()

    def set_stb_fr_min_ratio(self, min_ratio):
        """Sets recognition minimum account ratio

        Sets minimum account ratio in complete frame count for accuracy
        improvement of recognition stabilizing.
        For example, when there are 7 frames of extracted usable data in
        referred previous 20 frames, STB_SetFrCompleteFrameCount function has
        set "10"for the complete frame count and "60" for the recognition
        minimum account ratio.
        Creates frequency distribution of recognition result in the set 10 frames.
            Recognized as "Mr. A"(1 frame)
            Recognized as "Mr. B"(4 frames)
            Recognized as "Mr. C"(4 frames)
        In this case, the most account ratio “Mr. B” will be output as
        stabilized result.
        However, this recognition status will be output as "STB_STAUS_CALCULATING"
        since the account ratio is about57%(= 4 frames/10 frames) ,
        (Mr. B seizing ratio=) 57% < recognition account ratio (=60%).

        Args:
            min_ratio (int): recognition minimum account ratio [0-100]

        Returns:
            stb_return (int): return value of STB library

       """
        return self._stb.set_stb_fr_min_ratio(min_ratio)

    def get_stb_fr_min_ratio(self):
        """Gets recognition minimum account ratio

        Args:
            void

        Returns:
            tuple of (stb_return, min_ratio)
                stb_return (int): return value of STB library
                min_ratio (int): recognition minimum account ratio

        """
        return self._stb.get_stb_fr_min_ratio()


if __name__ == '__main__':
    pass

