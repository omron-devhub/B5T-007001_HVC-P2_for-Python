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

from struct import *
from p2def import *
from okao_result import *


class HVCResult(object):
    """Class storing the detection/estimation result of HVC-P2"""
    __slots__ = ['faces', 'bodies', 'hands']
    def __init__(self):
        self.faces = []
        self.bodies = []
        self.hands = []

    def read_from_buffer(self, exec_func, data_len, data):
        cur = 0
        body_count, = unpack_from('B',data, cur)
        hand_count, = unpack_from('B',data, cur+1)
        face_count, = unpack_from('B',data, cur+2)
        cur+=4  # for reserved

        # Human body detection
        for i in range(body_count):
            x, y, size, conf = unpack_from('<HHHH', data, cur)
            res = DetectionResult(x,y,size,conf)
            self.bodies.append(res)
            cur += 8

        # Hand detection
        for i in range(hand_count):
            x, y, size, conf = unpack_from('<HHHH', data, cur)
            res = DetectionResult(x,y,size,conf)
            self.hands.append(res)
            cur += 8

        # Face detection
        for i in range(face_count):
            x, y, size, conf = unpack_from('<HHHH', data, cur)
            res = FaceResult(x,y,size,conf)
            cur +=8

            # Face direction
            if exec_func & EX_DIRECTION:
                LR, UD, roll, conf = unpack_from('<hhhH', data, cur)
                res.direction = DirectionResult(LR, UD, roll, conf)
                cur += 8

            # Age estimation
            if exec_func & EX_AGE:
                age, conf = unpack_from('<bh', data, cur)
                res.age = AgeResult(age,conf)
                cur += 3

            # Gender estimation
            if exec_func & EX_GENDER:
                gen, conf = unpack_from('<bh', data, cur)
                res.gender = GenderResult(gen,conf)
                cur += 3

            # Gaze estimation
            if exec_func & EX_GAZE:
                LR, UD = unpack_from('<bb', data, cur)
                res.gaze = GazeResult(LR,UD)
                cur += 2

            # Blink estimation
            if exec_func & EX_BLINK:
                L, R = unpack_from('<hh', data, cur)
                res.blink = BlinkResult(L, R)
                cur += 4

            # Expression estimation
            if exec_func & EX_EXPRESSION:
                neu, hap, sur, ang, sad, neg = unpack_from('<bbbbbb', data, cur)
                res.expression = ExpressionResult(neu, hap, sur, ang, sad, neg)
                cur += 6

            # Face recognition
            if exec_func & EX_RECOGNITION:
                uid, score = unpack_from('<hh', data, cur)
                res.recognition = RecognitionResult(uid, score)
                cur += 4

            self.faces.append(res)
        return cur

    def export_to_C_FRAME_RESULT(self, frame_result):
        # Human body detection result
        frame_result.bodys.nCount = len(self.bodies)
        for i in range(len(self.bodies)):
            src_body = self.bodies[i]
            dst_body = frame_result.bodys.body[i]

            dst_body.center.nX = src_body.pos_x
            dst_body.center.nY = src_body.pos_y
            dst_body.nSize = src_body.size
            dst_body.nConfidence = src_body.conf

        # Face detection result
        frame_result.faces.nCount = len(self.faces)
        for i in range(len(self.faces)):
            src_face = self.faces[i]
            dst_face = frame_result.faces.face[i]

            dst_face.center.nX = src_face.pos_x
            dst_face.center.nY = src_face.pos_y
            dst_face.nSize = src_face.size
            dst_face.nConfidence = src_face.conf

            # Face direction result
            if src_face.direction is not None:
                dst_face.direction.nLR = src_face.direction.LR
                dst_face.direction.nUD = src_face.direction.UD
                dst_face.direction.nRoll = src_face.direction.roll
                dst_face.direction.nConfidence = src_face.direction.conf
            # Age estimation result
            if src_face.age is not None:
                dst_face.age.nAge = src_face.age.age
                dst_face.age.nConfidence = src_face.age.conf
            # Gender estimation result
            if src_face.gender is not None:
                dst_face.gender.nGender = src_face.gender.gender
                dst_face.gender.nConfidence = src_face.gender.conf
            # Gaze estimation result
            if src_face.gaze is not None:
                dst_face.gaze.nLR = src_face.gaze.gazeLR
                dst_face.gaze.nUD = src_face.gaze.gazeUD
            # Blink estimation result
            if src_face.blink is not None:
                dst_face.blink.nLeftEye = src_face.blink.ratioL
                dst_face.blink.nRightEye = src_face.blink.ratioR
            # Expression estimation result
            if src_face.expression is not None:
                dst_face.expression.neutral = src_face.expression.neutral
                dst_face.expression.happiness = src_face.expression.happiness
                dst_face.expression.surprise = src_face.expression.surprise
                dst_face.expression.anger = src_face.expression.anger
                dst_face.expression.sadness = src_face.expression.sadness
                dst_face.expression.neg_pos = src_face.expression.neg_pos
            # Recognition result
            if src_face.recognition is not None:
                dst_face.recognition.nUID = src_face.recognition.uid
                dst_face.recognition.nScore = src_face.recognition.score

        return

    def __str__(self):
        s = 'Face count= %s\n' % len(self.faces)
        for i in range(len(self.faces)):
            face = self.faces[i]
            s += '\t[%s]\t' % i + face.__str__() +'\n'

        s += 'Body count= %s\n' % len(self.bodies)
        for i in range(len(self.bodies)):
            s += '\t[%s]\t' % i + self.bodies[i].__str__() +'\n'

        s += 'Hand count= %s\n' % len(self.hands)
        for i in range(len(self.hands)):
            s += '\t[%s]\t' % i + self.hands[i].__str__() +'\n'
        return s

if __name__ == '__main__':
    hvc_res = HVCResult()
    print hvc_res
