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
import glob
import subprocess
import StringIO
import os
import sys
import traceback

# 0-127
DEFAULT_VBRQ=105

def convert(vbrq=DEFAULT_VBRQ):
    print "Converting FLAC files to AAC..."
    
    for infile in glob.iglob('*.flac'):
        #infile = os.path.abspath(infile)
        
        file_parts = infile.rsplit('.',1)
        wavfile = file_parts[0]+'.wav'
        outfile = file_parts[0]+'.m4a'

        p = subprocess.Popen([
                'flac',
                '-d',
                '-f',
                '%s' % infile],
            executable="flac")
            
        p.wait()
        
        p = subprocess.Popen([
                'metaflac',
                '--export-tags-to=-',
                '%s' % infile],
            executable='metaflac',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        data = p.communicate()
        data = data[0].splitlines()
        info = {}
        for i in data:
            i = i.split('=')
            info[i[0].upper()] = i[1]
        
        
        CONVERT_CMD = [
            'afconvert',
            '-q','127',
            '-f','m4af',
            '-d','alac'
        ]
        
        CONVERT_CMD.append('%s' % wavfile)
        CONVERT_CMD.append('%s' % outfile)
        
        if os.path.exists(outfile):
            os.unlink(outfile)
        
        p = subprocess.Popen(CONVERT_CMD,executable="afconvert")
        p.wait()
        os.unlink(wavfile)
        
        TAGS_CMD = [
            'AtomicParsley',
            '%s' % outfile,
            '--freefree'
        ]
        if info.has_key('TITLE'):
            TAGS_CMD.append('--title')
            TAGS_CMD.append('%s' % info['TITLE'])
        if info.has_key('ARTIST'):
            TAGS_CMD.append('--artist')
            TAGS_CMD.append('%s' % info['ARTIST'])
        if info.has_key('ALBUM'):
            TAGS_CMD.append('--album')
            TAGS_CMD.append('%s' % info['ALBUM'])
        if info.has_key('DATE'):
            TAGS_CMD.append('--year')
            TAGS_CMD.append('%s' % info['DATE'])
        if info.has_key('TRACK'):
            TAGS_CMD.append('--tracknum')
            if info.has_key('TRACKTOTAL'):
                TAGS_CMD.append('%s/%s' % (info['TRACK'],info['TRACKTOTAL']))
            else:
                TAGS_CMD.append('%s' % info['TRACK'])
        elif info.has_key('TRACKNUMBER'):
            TAGS_CMD.append('--tracknum')
            if info.has_key('TRACKTOTAL'):
                TAGS_CMD.append('%s/%s' % (info['TRACKNUMBER'],info['TRACKTOTAL']))
            else:
                TAGS_CMD.append('%s' % info['TRACKNUMBER'])
        if info.has_key('DISC'):
            TAGS_CMD.append('--disk')
            if info.has_key('DISCTOTAL'):
                TAGS_CMD.append('%s/%s' % (info['DISC'],info['DISCTOTAL']))
            else:
                TAGS_CMD.append('%s/1' % info['DISC'])
        else:
            TAGS_CMD.append('--disk')
            TAGS_CMD.append('1/1')
        if info.has_key('GENRE'):
            TAGS_CMD.append('--genre')
            TAGS_CMD.append('%s' % info['GENRE'])
        if info.has_key('COPYRIGHT'):
            TAGS_CMD.append('--copyright')
            TAGS_CMD.append('%s' % info['COPYRIGHT'])
        
        TAGS_CMD.append('--overWrite')
        
        p = subprocess.Popen(TAGS_CMD,executable="AtomicParsley")
        p.wait()

def main(args):
    if len(args) == 1:
        convert(args[0])
    elif len(args) == 0:
        convert()
    else:
        print "Usage:"
        print "convert [VBR quality, 0-127; default=%s]"%DEFAULT_VBRQ

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        print sys.argv[1:]
        sys.exit(1)
