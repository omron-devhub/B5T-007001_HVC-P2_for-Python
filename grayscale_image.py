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

from PIL import Image

class GrayscaleImage(object):
    """8 bit grayscale image. """
    __slots__ = ['width', 'height', 'data']

    def __init__(self):
        self.width = 0
        self.height = 0
        self.data = b''

    def save(self, fname):
        w = self.width
        h = self.height

        # if no data, no save.
        if w == 0 or h == 0:
            return False

        img = Image.new("L", (w, h), 0)
        x = 0
        y = 0
        for y in range(h):
            for x in range(w):
                img.putpixel((x, y), ord(self.data[w * y + x]))
        img.save(fname)
        return True
