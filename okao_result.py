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

from p2def import *

gender_dic = {GENDER_UNKNOWN:"-",\
              GENDER_FEMALE :"Female",\
              GENDER_MALE   :"Male"}

exp_dic = {EXP_UNKNOWN  :"-",\
           EXP_NEUTRAL  :"Neutral",\
           EXP_HAPPINESS:"Happiness",\
           EXP_SURPRISE :"Surprise",\
           EXP_ANGER    :"Anger",\
           EXP_SADNESS  :"Sadness"}

class DetectionResult(object):
    """General purpose detection result"""
    __slots__ = ['pos_x', 'pos_y', 'size', 'conf']
    def __init__(self, pos_x=None, pos_y=None, size=None, conf=None):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = size
        self.conf = conf

    def __str__(self):
        x = self.pos_x
        y = self.pos_y
        size = self.size
        conf = self.conf
        return 'X:%s Y:%s Size:%s Conf:%s' % (x,y,size,conf)

class FaceResult(DetectionResult):
    """Detection result for face"""
    __slots__ = ['direction','age','gender','gaze','blink','expression','recognition']
    def __init__(self, pos_x=None, pos_y=None, size=None, conf=None):
        DetectionResult.__init__(self,pos_x,pos_y,size,conf)
        self.direction = None
        self.age = None
        self.gender = None
        self.gaze = None
        self.blink = None
        self.expression = None
        self.recognition = None

    def __str__(self):
        s = DetectionResult.__str__(self) +'\n'
        if self.direction is not None:    s += '\t\t' + self.direction.__str__() +'\n'
        if self.age is not None:    s += '\t\t' + self.age.__str__() +'\n'
        if self.gender is not None: s += '\t\t' + self.gender.__str__() +'\n'
        if self.gaze is not None:   s += '\t\t' + self.gaze.__str__() +'\n'
        if self.blink is not None:  s += '\t\t' + self.blink.__str__() +'\n'
        if self.expression is not None:    s += '\t\t' + self.expression.__str__() +'\n'
        if self.recognition is not None:  s += '\t\t' + self.recognition.__str__()
        return s

class DirectionResult(object):
    """Result for Facial direction estimation"""
    __slots__ = ['LR', 'UD', 'roll', 'conf']
    def __init__(self, LR=None, UD=None, roll=None, conf=None):
        self.LR = LR
        self.UD = UD
        self.roll = roll
        self.conf = conf

    def __str__(self):
        return 'Direction     LR:{0} UD:{1} Roll:{2} Conf:{3}'.\
                   format(self.LR, self.UD, self.roll, self.conf)

class AgeResult(object):
    """Result of Age estimation"""
    __slots__ = ['age','conf']
    def __init__(self, age=None, conf=None):
        self.age = age
        self.conf = conf

    def __str__(self):
        str = 'Age           '
        if self.age == EST_NOT_POSSIBLE:
            str += 'Age:- '
        else:
            str += 'Age:{0} '.format(self.age)
        return str + 'Conf:{0}'.format(self.conf)

class GenderResult(object):
    """Result of Gender estimation"""
    __slots__ = ['gender', 'conf']
    def __init__(self, gender=None, conf=None):
        self.gender = gender
        self.conf = conf

    def __str__(self):
        if self.gender == EST_NOT_POSSIBLE:
            _dic_key = GENDER_UNKNOWN
        else:
            _dic_key = self.gender
        return 'Gender        Gender:{0} Conf:{1}'.format(gender_dic[_dic_key], self.conf)

class GazeResult(object):
    """Result of Gaze estimation"""
    __slots__ = ['gazeLR','gazeUD']
    def __init__(self, gazeLR=None, gazeUD=None):
        self.gazeLR = gazeLR
        self.gazeUD = gazeUD

    def __str__(self):
        return 'Gaze          LR:{0} UD:{1}'.format(self.gazeLR, self.gazeUD)

class BlinkResult(object):
    """Result of Blink estimation"""
    __slots__ = ['ratioR','ratioL']
    def __init__(self, ratioR=None, ratioL=None):
        self.ratioR = ratioR
        self.ratioL = ratioL

    def __str__(self):
        return 'Blink         R:{0} L:{1}'.format(self.ratioR, self.ratioL)

class ExpressionResult(object):
    """Result of Expression estimation"""
    __slots__ = ['neutral','happiness','surprise','anger','sadness','neg_pos']
    def __init__(self, neutral=None, happiness=None, surprise=None,\
                       anger=None, sadness=None, neg_pos=None, degree=None):
        self.neutral = neutral
        self.happiness = happiness
        self.surprise = surprise
        self.anger = anger
        self.sadness = sadness
        self.neg_pos = neg_pos

    def get_top1(self):
        x = [self.neutral, self.happiness, self.surprise, self.anger, self.sadness]

        max_score = max(x)
        if max_score == EST_NOT_POSSIBLE:
            max_idx = EXP_UNKNOWN
        else:
            max_idx = x.index(max_score)

        exp_str = exp_dic[max_idx]
        return exp_str, max_score

    def __str__(self):
        str ='Expression    '
        if self.neutral == EST_NOT_POSSIBLE:
            str += 'Exp:- Score:- (Neutral:- Happiness:- Surprise:- Anger:- Sadness:- NegPos:-)'
        else:
            top1_exp, top1_score = self.get_top1()
            str += 'Exp:{0} Score:{1} '.format(top1_exp, top1_score)\
                + '(Neutral:{0} Happiness:{1} Surprise:{2} Anger:{3} Sadness:{4} NegPos:{5})'\
                .format(self.neutral, self.happiness, self.surprise, self.anger,\
                self.sadness, self.neg_pos)
        return str

class RecognitionResult(object):
    """Result of Recognition"""
    __slots__ = ['uid','score']
    def __init__(self, uid=None, score=None):
        self.uid = uid
        self.score = score

    def __str__(self):
        if self.uid == RECOG_NO_DATA_IN_ALBUM:
            str = 'Recognition   No data is registered in the album.'
        elif self.uid == RECOG_NOT_POSSIBLE:
            str = 'Recognition   Uid:- Score:{0}'.format(self.score)
        elif self.uid == -1:
            str = 'Recognition   Uid:Unknown Score:{0}'.format(self.score)
        else:
            str = 'Recognition   Uid:{0} Score:{1}'.format(self.uid, self.score)
        return str

if __name__ == '__main__':
    pass
