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
# -*- coding: utf-8 -*-
#!/usr/bin/env python

from hvc_result_c import *
from hvc_tracking_result_c import *

STB_EX_BODY       =   0x01
STB_EX_FACE       =   0x04
STB_EX_DIRECTION  =   0x08
STB_EX_AGE        =   0x10
STB_EX_GENDER     =   0x20
#STB_EX_GAZE       =   0x40  # Not use now.
#STB_EX_BLINK      =   0x80  # Not use now.
#STB_EX_EXPRESSION =  0x100  # Not use now.
STB_EX_RECOGNITION =  0x200
STB_EX_FUNC_ALL = STB_EX_BODY | STB_EX_FACE | STB_EX_DIRECTION | STB_EX_AGE\
                | STB_EX_GENDER | STB_EX_RECOGNITION

# STB error code definition
STB_RET_NORMAL           =  0x00  # Normal end
STB_RET_ERR_INITIALIZE   = -0x02  # Initializing error
STB_RET_ERR_INVALIDPARAM = -0x03  # Parameter error
STB_RET_ERR_NOHANDLE     = -0x07  # Handle error
STB_RET_ERR_PROCESSCONDITION = -0x08 # Processing condition error


class STB(object):
    """Python wrapper class for STB library(dll) in C language."""
    hSTB = c_void_p()

    def __init__(self, library_name, exec_func):
        # Load shared library
        self.stbDLL = cdll.LoadLibrary(library_name)
        self.hSTB = self.stbDLL.STB_CreateHandle(exec_func)

    def execute(self, frame_res, faces_res, bodies_res):
        """Executes stabilization process.

        In:
            - each frame result by frame_res(C_FRAME_RESULT) input argument
        Out:
            - face count (return)
            - body count (return)
            - stabilized face result by faces_res(C_FACE_RESULTS) output argument
            - stabilized body result by bodies_res(C_BODY_RESULTS) output argument

        Args:
            frame_res (C_FRAME_RESULT): input one frame result for STBLib.
                    Set the information of face central coordinate, size and
                    direction to stabilize age, gender and face recognition.
            faces_res (C_FACE_RES35): output result stabilized face data.
            bodies_res (C_BODY_RES35): output result stabilized body data.

        Returns:
            tuple of (stb_return, face_count, body_count)
                stb_return (int): return value of STB library
                face_count (int): face count
                body_count (int): body count

        """
        _face_count = c_uint(0)
        _body_count = c_uint(0)

        ret = self.stbDLL.STB_SetFrameResult(self.hSTB, byref(frame_res))
        if ret != STB_RET_NORMAL:
            return (ret, 0, 0)

        ret = self.stbDLL.STB_Execute(self.hSTB)
        if ret != STB_RET_NORMAL:
            return (ret, 0, 0)

        ret = self.stbDLL.STB_GetFaces(self.hSTB, byref(_face_count),\
                                                  byref(faces_res))
        if ret != STB_RET_NORMAL:
            return (ret, 0, 0)

        ret = self.stbDLL.STB_GetBodies(self.hSTB, byref(_body_count),\
                                                   byref(bodies_res))
        if ret != STB_RET_NORMAL:
            return (ret, 0, 0)

        return (STB_RET_NORMAL, _face_count.value, _body_count.value)

    def get_stb_version(self):
        _major_version = c_byte(0)
        _minor_version = c_byte(0)
        ret = self.stbDLL.STB_GetVersion(byref(_major_version),\
                                         byref(_minor_version))
        return (ret, _major_version.value, _minor_version.value)

    def clear_stb_frame_results(self):
        ret = self.stbDLL.STB_ClearFrameResults(self.hSTB)
        return ret

    def set_stb_tr_retry_count(self, max_retry_count):
        ret = self.stbDLL.STB_SetTrRetryCount(self.hSTB, max_retry_count)
        return ret

    def get_stb_tr_retry_count(self):
        _max_retry_count = c_int(0)
        ret = self.stbDLL.STB_GetTrRetryCount(self.hSTB, byref(_max_retry_count))
        return (ret, _max_retry_count.value)

    def set_stb_tr_steadiness_param(self, pos_steadiness_param,\
                                          size_steadiness_param):
        ret = self.stbDLL.STB_SetTrSteadinessParam(self.hSTB,\
                                                   pos_steadiness_param,\
                                                   size_steadiness_param)
        return ret

    def get_stb_tr_steadiness_param(self):
        _pos_steadiness_param = c_int(0)
        _size_steadiness_param = c_int(0)
        ret = self.stbDLL.STB_GetTrSteadinessParam(self.hSTB,\
                    byref(_pos_steadiness_param), byref(_size_steadiness_param))
        return (ret, _pos_steadiness_param.value, _size_steadiness_param.value)

    def set_stb_pe_threshold_use(self, threshold):
        ret = self.stbDLL.STB_SetPeThresholdUse(self.hSTB, threshold)
        return ret

    def get_stb_pe_threshold_use(self):
        _threshold = c_int(0)
        ret = self.stbDLL.STB_GetPeThresholdUse(self.hSTB, byref(_threshold))
        return (ret, _threshold.value)

    def set_stb_pe_angle_use(self, min_UD_angle, max_UD_angle,\
                                   min_LR_angle, max_LR_angle):
        ret = self.stbDLL.STB_SetPeAngleUse(self.hSTB,
                                             min_UD_angle, max_UD_angle,\
                                             min_LR_angle, max_LR_angle)
        return ret

    def get_stb_pe_angle_use(self):
        _min_UD_angle = c_int(0)
        _max_UD_angle = c_int(0)
        _min_LR_angle = c_int(0)
        _max_LR_angle = c_int(0)
        ret = self.stbDLL.STB_GetPeAngleUse(self.hSTB,\
                                 byref(_min_UD_angle), byref(_max_UD_angle),\
                                 byref(_min_LR_angle), byref(_max_LR_angle))
        return (ret, _min_UD_angle.value, _max_UD_angle.value,\
                     _min_LR_angle.value, _max_LR_angle.value)

    def set_stb_pe_complete_frame_count(self, frame_count):
        ret = self.stbDLL.STB_SetPeCompleteFrameCount(self.hSTB, frame_count)
        return ret

    def get_stb_pe_complete_frame_count(self):
        _frame_count = c_int(0)
        ret = self.stbDLL.STB_GetPeCompleteFrameCount(self.hSTB, byref(_frame_count))
        return (ret, _frame_count.value)

    def set_stb_fr_threshold_use(self, threshold):
        ret = self.stbDLL.STB_SetFrThresholdUse(self.hSTB, threshold)
        return ret

    def get_stb_fr_threshold_use(self):
        _threshold = c_int(0)
        ret = self.stbDLL.STB_GetFrThresholdUse(self.hSTB, byref(_threshold))
        return (ret, _threshold.value)

    def set_stb_fr_angle_use(self, min_UD_angle, max_UD_angle, min_LR_angle,\
                                                                max_LR_angle):
        ret = self.stbDLL.STB_SetFrAngleUse(self.hSTB,\
                                            min_UD_angle, max_UD_angle,\
                                            min_LR_angle, max_LR_angle)

        return ret

    def get_stb_fr_angle_use(self):
        _min_UD_angle = c_int(0)
        _max_UD_angle = c_int(0)
        _min_LR_angle = c_int(0)
        _max_LR_angle = c_int(0)
        ret = self.stbDLL.STB_GetFrAngleUse(self.hSTB, byref(_min_UD_angle),\
                                            byref(_max_UD_angle),\
                                            byref(_min_LR_angle),\
                                            byref(_max_LR_angle))

        return (ret, _min_UD_angle.value, _max_UD_angle.value,\
                _min_LR_angle.value, _max_LR_angle.value)

    def set_stb_fr_complete_frame_count(self, frame_count):
        ret = self.stbDLL.STB_SetFrCompleteFrameCount(self.hSTB, frame_count)
        return ret

    def get_stb_fr_complete_frame_count(self):
        _frame_count = c_int(0)
        ret = self.stbDLL.STB_GetFrCompleteFrameCount(self.hSTB, byref(_frame_count))
        return (ret, _frame_count.value)

    def set_stb_fr_min_ratio(self, min_ratio):
        ret = self.stbDLL.STB_SetFrMinRatio(self.hSTB, min_ratio)
        return ret

    def get_stb_fr_min_ratio(self):
        _min_ratio = c_int(0)
        ret = self.stbDLL.STB_GetFrMinRatio(self.hSTB, byref(_min_ratio))
        return (ret, _min_ratio.value)

if __name__ == '__main__':
    pass

