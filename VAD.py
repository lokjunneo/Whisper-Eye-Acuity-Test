# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
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

import math
import numpy as np


class VAD(object):
    """docstring for VAD"""
    def __init__(self, sampleRate=16000):
        super(VAD, self).__init__()

        self.sampleRate = sampleRate

        self.reset()

    def reset(self):
        self.isFirst = True

        self.energyMAX = 0.0
        self.energyMIN = 0.0

        self.energyMIN_INITIAL = 0.1

        self.resetDelta()

        self.frameCount = 0
        self.inactiveFrameCount = 0
        self.activeFrameCount = 0

        self.threshold = 0

        self.lam = 0

        #self.wait = True
        self.wait = False
        self.state = 0

    def resetDelta(self):
        self.delta = 1.01

    def energy(self, frame):
        result = 0.0
        
        if (len(frame) <= 0):
            return result

        for value in frame:
            result += value * value

        return math.sqrt(result / float(len(frame)))

    def processFrame(self, frame_input):
        if (len(frame_input)<=0):
            return self.state
        state = 0

        frame = np.array(frame_input).astype(np.float32)
        frame = frame / float(np.iinfo(np.int16).max)

        energy = self.energy(frame)

        if self.isFirst:
            self.isFirst = False
            self.energyMAX = energy
            self.energyMIN_INITIAL = energy
            self.energyMIN = self.energyMIN_INITIAL
            return 1

        if energy > self.energyMAX:
            self.energyMAX = energy

        if energy < self.energyMIN:
            if energy < 0.025:
                self.energyMIN = self.energyMIN_INITIAL
            else:
                self.energyMIN = energy

            self.resetDelta()

        lam = abs(self.energyMAX - self.energyMIN) / (self.energyMAX + 0.01)

        threshold = (1. - lam) * self.energyMAX + lam * self.energyMIN
        self.threshold = threshold

        if energy * 1.01 > threshold and lam > 0.35:
            if self.activeFrameCount > 1:
            #if self.activeFrameCount > 3:
                state = 1
                self.inactiveFrameCount = 0
                self.wait = False
            else:
                state = 0

            self.activeFrameCount += 1
        else:
            #if self.inactiveFrameCount > 8 * 1:
            if self.inactiveFrameCount > 8 * 3:
            #if self.inactiveFrameCount > 8 * 4:
                state = 0
                self.activeFrameCount = 0
                #self.reset()
            else:
                state = 1
                self.inactiveFrameCount += 1

        self.delta = self.delta * 1.001

        if state == 0 and self.wait:
            if self.inactiveFrameCount > 40:
                state = 0
                self.wait = False
            else:
                state = 1

        self.energyMIN = self.energyMIN * self.delta
        self.energyMAX = self.energyMAX * 0.999

        self.state = state
        return state