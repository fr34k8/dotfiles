#!/bin/bash
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

#ffmpeg -i $1 -f rawvideo -threads 0 -vcodec libx264 -vpre placebo_firstpass -level 31 -crf 25 -an -pass 1  -y /dev/null
#ffmpeg -i $1 -f mp4 -threads 0 -vcodec libx264 -vpre hq2 -level 31 -crf 25 -acodec libfaac -ab 160kb -ac 2 -pass 3 -y $1.m4v

BASENAME=`python -c "import os;print os.path.basename('$1').rsplit('.',1)[0]"`
AUDIO_VBR_QUALITY=95 # 0-127

# ===== FAAC
#mkdir $BASENAME
#ffmpeg -i $1 -f mp4 -threads 0 -vcodec libx264 -vpre hq2 -level 31 -profile aac_main -crf 23 -qmin 1 -qmax 32 -qdiff 6 -acodec libfaac -ab 192kb -alang eng -y $BASENAME/RAW.m4v

# ===== afconvert, VBR
mkdir $BASENAME
ffmpeg -i $1 -f mp4 -threads 0 -vcodec libx264 -vpre hqi -level 31 -crf 23 -qmin 1 -qmax 32 -qdiff 6 -an -y $BASENAME/RAW.m4v &
ffmpeg -i $1 -f wav -y $BASENAME/RAW.wav > /dev/null 2>&1
#afconvert -q 127 -s 3 -f m4af -d aac -u vbrq $AUDIO_VBR_QUALITY $BASENAME/RAW.wav $BASENAME/RAW.m4a
wine /Users/mtigas/Library/_LocalApps/win32/neroAacEnc.exe -q 1 -he -if $BASENAME/RAW.wav -of $BASENAME/RAW.m4a
rm $BASENAME/RAW.wav
wait

# win32\neroAacEnc -q 1 -if dropouts.wav -of dropouts-2.m4a
# win32\neroAacEnc -q 1 -he -if dropouts.wav -of dropouts-3.m4a
# win32\neroAacEnc -q 1 -hev2 -if dropouts.wav -of dropouts-4.m4a

# ===== afconvert, VBR; downmixed to stereo
#mkdir $BASENAME
#ffmpeg -i $1 -f mp4 -threads 0 -vcodec libx264 -vpre hq2 -level 31 -crf 23 -qmin 1 -qmax 32 -qdiff 6 -an -y $BASENAME/RAW.m4v &
#ffmpeg -i $1 -f wav -ac 2 -y $BASENAME/RAW.wav
#afconvert -q 127 -s 3 -f m4af -d aac -u vbrq $AUDIO_VBR_QUALITY $BASENAME/RAW.wav $BASENAME/RAW.m4a
#rm $BASENAME/RAW.wav
wait
