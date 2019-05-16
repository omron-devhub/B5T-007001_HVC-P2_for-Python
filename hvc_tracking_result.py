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

from hvc_result import *
from okao_result import *
from hvc_tracking_result_c import *


status_dic = {STB_STATUS_CALCULATING:"CALCULATING",\
              STB_STATUS_COMPLETE   :"COMPLETE",\
              STB_STATUS_FIXED      :"FIXED",\
              STB_STATUS_NO_DATA    :"NO_DATA"}


class TrackingAgeResult(AgeResult):

    def __init__(self, tracking_status=STB_STATUS_NO_DATA, age=None, conf=None):
        AgeResult.__init__(self, age, conf)
        self.tracking_status = tracking_status

    def __str__(self):
        if self.tracking_status == STB_STATUS_NO_DATA:
            str = 'Age           Age:-    Conf:-'
        else:
            str = AgeResult.__str__(self)
        return str + ' Status:{0}'.format(status_dic[self.tracking_status])


class TrackingGenderResult(GenderResult):

    def __init__(self, tracking_status=STB_STATUS_NO_DATA, gender=None, conf=None):
        GenderResult.__init__(self, gender, conf)
        self.tracking_status = tracking_status

    def __str__(self):
        if self.tracking_status == STB_STATUS_NO_DATA:
            str = 'Gender        Gender:- Conf:-'
        else:
            str = GenderResult.__str__(self)
        return str + ' Status:{0}'.format(status_dic[self.tracking_status])


class TrackingRecognitionResult(RecognitionResult):

    def __init__(self, tracking_status=STB_STATUS_NO_DATA, uid=None, score=None):
        RecognitionResult.__init__(self, uid, score)
        self.tracking_status = tracking_status

    def __str__(self):
        if self.uid == RECOG_NO_DATA_IN_ALBUM:
            str = 'Recognition   No data is registered in the album.'
        elif self.uid == RECOG_NOT_POSSIBLE: # Recognition was not possible.
            str = 'Recognition   Uid:- Score:{0} Status:{1}'.format(self.score,status_dic[self.tracking_status])
        elif self.tracking_status == STB_STATUS_NO_DATA:
            str = 'Recognition   Uid:- Score:- Status:{0}'.format(status_dic[self.tracking_status])
        elif self.uid == -1: # Unknown user.
            str = 'Recognition   Uid:Unknown Score:{0} Status:{1}'.format(self.score,status_dic[self.tracking_status])
        else:
            str = 'Recognition   Uid:{0} Score:{1} Status:{2}'.format(self.uid,self.score,status_dic[self.tracking_status])
        return str

class FaceList(list):

    def append_C_FACE_RES35(self, exec_func, face_count, face_res35):
        """Appends the result of STB output to this face list."""
        for i in range(face_count):
            f = face_res35[i]
            tr_f = TrackingFaceResult(f.center.x, f.center.y, f.nSize,\
                                      f.conf, f.nDetectID, f.nTrackingID);

            if exec_func & EX_AGE:
                age = f.age
                tr_f.age = TrackingAgeResult(age.status, age.value, age.conf)

            if exec_func & EX_GENDER:
                g = f.gender
                tr_f.gender = TrackingGenderResult(g.status, g.value, g.conf)

            if exec_func & EX_RECOGNITION:
                r = f.recognition
                tr_f.recognition = TrackingRecognitionResult(r.status, r.value, r.conf)
            """
            Note:
                We do not use the functions(Face direction, Gaze, Blink and
                Expression estimation) for STBLib.
                So the part of that functions is not implemented here.

            """
            self.append(tr_f)

    def append_direction_list(self, faces):
        for i in range(len(faces)):
            self[i].direction = faces[i].direction

    def append_gaze_list(self, faces):
        for i in range(len(faces)):
            self[i].gaze = faces[i].gaze

    def append_blink_list(self, faces):
        for i in range(len(faces)):
            self[i].blink = faces[i].blink

    def append_expression_list(self, faces):
        for i in range(len(faces)):
            self[i].expression = faces[i].expression


class BodyList(list):

    def append_BODY_RES35(self,exec_func, body_count, body_res35):
        for i in range(body_count):
            b = body_res35[i]
            tr_b = TrackingResult(b.center.x, b.center.y, b.nSize,\
                                      b.conf, b.nDetectID, b.nTrackingID);
            self.append(tr_b)


class HandList(list):

    def append_hand_list(self, hands):
        # Hand detection result
        for i in range(len(hands)):
            h = hands[i]
            hand_res = TrackingResult(h.pos_x, h.pos_y, h.size, h.conf, i, -1)
            self.append(hand_res)


class TrackingResult(object):
    __slots__ = ['pos_x','pos_y', 'size', 'conf', 'detection_id','tracking_id']
    def __init__(self, pos_x=None, pos_y=None, size=None, conf=None, detection_id=None,\
                       tracking_id=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = size
        self.conf = conf
        self.detection_id = detection_id
        self.tracking_id = tracking_id

    def __str__(self):
        x = self.pos_x
        y = self.pos_y
        size = self.size
        conf = self.conf
        d_id = self.detection_id
        t_id = self.tracking_id

        if self.tracking_id != -1:
            s = 'TrackingID:%s\n' % self.tracking_id
        else:
            s = '\n'
        return s + '      Detection     X:%s Y:%s, Size:%s Conf:%s'% (x, y, size, conf)


class TrackingFaceResult(TrackingResult):
    __slots__ = ['direction','age','gender','gaze','blink','expression','recognition']
    def __init__(self, pos_x=None, pos_y=None, size=None, conf=None,\
                                   detection_id=None, tracking_id=None):
        TrackingResult.__init__(self, pos_x, pos_y, size, conf,\
                                             detection_id, tracking_id)
        self.direction = None
        self.age = None
        self.gender = None
        self.gaze = None
        self.blink = None
        self.expression = None
        self.recognition = None

    def __str__(self):
        s = TrackingResult.__str__(self) + '\n'
        if self.direction is not None:
            s += '      ' + self.direction.__str__() +'\n'
        if self.age is not None:
            s += '      ' + self.age.__str__() +'\n'
        if self.gender is not None:
            s += '      ' + self.gender.__str__() +'\n'
        if self.gaze is not None:
            s += '      ' + self.gaze.__str__() +'\n'
        if self.blink is not None:
            s += '      ' + self.blink.__str__() +'\n'
        if self.expression is not None:
            s += '      ' + self.expression.__str__() +'\n'
        if self.recognition is not None:
            s += '      ' + self.recognition.__str__()
        return s


class HVCTrackingResult(object):
    """Class storing tracking result"""

    __slots__ = ['faces', 'bodies', 'hands']
    def __init__(self):
        self.faces = FaceList()
        self.bodies = BodyList()
        self.hands = HandList()

    def __str__(self):
        s = 'Face Count = %s\n' % len(self.faces)
        for i in range(len(self.faces)):
            s += '  [%s] ' % i + self.faces[i].__str__() +'\n'

        s += 'Body Count = %s\n' % len(self.bodies)
        for i in range(len(self.bodies)):
            s += '  [%s] ' % i + self.bodies[i].__str__() +'\n'

        s += 'Hand Count = %s\n' % len(self.hands)
        for i in range(len(self.hands)):
            s += '  [%s] ' % i + self.hands[i].__str__() +'\n'

        return s

    def clear(self):
        del(self.faces[:])
        del(self.bodies[:])
        del(self.hands[:])

    def appned_FRAME_RESULT(self, frame_result):

        # Body detection result
        for i in range(len(frame_result.bodies)):
            b = frame_result.bodies[i]
            body_res = TrackingResult(b.pos_x, b.pos_y, b.size,b.conf,i,\
                                    STB_TRID_NOT_TRACKED)
            self.bodies.append(body_res)

        # Hand detection result
        for i in range(len(frame_result.hands)):
            h = frame_result.hands[i]
            hand_res = TrackingResult(h.pos_x, h.pos_y, h.size,h.conf,i,\
                                    STB_TRID_NOT_TRACKED)
            self.hands.append(hand_res)

        # Face detection result
        for i in range(len(frame_result.faces)):
            f = frame_result.faces[i]
            face_res = TrackingFaceResult(f.pos_x, f.pos_y, f.size,f.conf,i,\
                                    STB_TRID_NOT_TRACKED)
            # Face direction result
            if f.direction is not None:
                face_res.direction = DirectionResult(f.direction.LR,\
                                                     f.direction.UD,\
                                                     f.direction.roll,\
                                                     f.direction.conf)
            # Age estimation result
            if f.age is not None:
                face_res.age = AgeResult(f.age.age, f.age.conf)
            # Gender estimation result
            if f.gender is not None:
                face_res.gender = GenderResult(f.gender.gender, f.gender.conf)
            # Gaze estimation result
            if f.gaze is not None:
                face_res.gaze = GazeResult(f.gaze.gazeLR, f.gaze.gazeUD)
            # Blink estimation result
            if f.blink is not None:
                face_res.blink = BlinkResult(f.blink.ratioR, f.blink.ratioL)
            # Expression estimation result
            if f.expression is not None:
                face_res.expression = ExpressionResult(f.expression.neutral,\
                                         f.expression.happiness,\
                                         f.expression.surprise,\
                                         f.expression.anger,\
                                         f.expression.sadness,\
                                         f.expression.neg_pos)
            # Face recognition result
            if f.recognition is not None:
                 face_res.recognition = RecognitionResult(f.recognition.uid,
                                                          f.recognition.score)

            # Appends to face list.
            self.faces.append(face_res)

if __name__ == '__main__':
    pass