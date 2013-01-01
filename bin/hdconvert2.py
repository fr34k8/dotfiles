#!/usr/bin/env python
# coding=utf8
#
# Copyright 2012-2013, Mike Tigas
# https://mike.tig.as/
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
import subprocess
import StringIO
import os
import sys
import traceback
import fnmatch

FILETYPE_MATCHES = ("mkv", "avi", "mov", "wmv")

def convert():
    for filename in os.listdir('.'):
        is_video_file = False
        for ftype in FILETYPE_MATCHES:
            if fnmatch.fnmatch(filename, '*.%s' % ftype):
                is_video_file = True
                break
        
        if not is_video_file:
            print "%s is not a video file" % filename
            continue
        
        file_parts = filename.rsplit('.',1)
        video_outfile = file_parts[0]+'-RAW-FAST.m4v'
        audio_wavfile = file_parts[0]+'-RAW.wav'
        audio_outfile = file_parts[0]+'-RAW.m4a'
        

        print
        print
        print "="*40
        print file_parts[0]
        print "="*40

        video_p = subprocess.Popen([
                'ffmpeg',
                '-i', '%s' % filename,
                #'-t', '20',
                '-f', 'mp4',
                '-threads', '0',
                '-vcodec', 'libx264',
                '-vpre', 'fast',
                '-level', '31',
                '-crf', '25',
                '-an',
                '-y',
                '%s' % video_outfile],
            executable="ffmpeg")


        audio_p = subprocess.Popen([
                'ffmpeg',
                '-i', '%s' % filename,
                #'-t', '20',
                '-f', 'wav',
                '-y',
                '%s' % audio_wavfile],
            executable="ffmpeg")
        audio_p.wait()
        
        audioaac_p = subprocess.Popen([
                'wine',
                '/Users/mtigas/Library/_LocalApps/win32/neroAacEnc.exe',
                '-q', '1',
                '-he',
                '-if',
                '%s' % audio_wavfile,
                '-of',
                '%s' % audio_outfile],
            executable="wine")

        video_p.wait()
        audioaac_p.wait()
        
        os.unlink(audio_wavfile)

if __name__ == '__main__':
    convert()
