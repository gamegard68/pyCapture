#!/usr/bin/python -tt

import sys
import gobject
import getopt
import threading
import time
import os
import signal
import re

try:
    import pygst
    pygst.require("0.10")
    import gst
except:
    sys.exit(1)


# original pipeline:
"""
gst-launch-0.10 -e v4l2src device=/dev/video0 norm=PAL-BG do-timestamp=true ! 'video/x-raw-yuv,format=(fourcc)YV12,width=720,height=576,framerate=25/1,interlaced=true,aspect-ratio=4/3' !\
 queue ! videorate ! cogcolorspace ! 'video/x-raw-yuv,format=(fourcc)YV12,framerate=25/1,interlaced=true,aspect-ratio=4/3' ! queue !\
 jpegenc ! queue ! mux. alsasrc device=hw:2,0 buffer-time=2000000 do-timestamp=true ! 'audio/x-raw-int,rate=32000,channels=1,depth=16' ! queue !\
 audioconvert ! queue ! mux. avimux name=mux ! filesink location=capture_vhs_02.avi
"""

class ExitCommand(Exception):
    pass

def parse_opts(argv):
    global outputfile
    global timestr
    try:
        opts, args = getopt.getopt(argv,"ho:e:")
        if not opts:
            print 'No options supplied'
            print 'Usage: pyCapture.py -o <capture_mjpeg.avi> -e <HH:MM:SS>'
            sys.exit(2)
    except getopt.GetoptError:
        print 'pyCapture.py -o <capture_mjpeg.avi> -e <HH:MM:SS>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'pyCapture.py -o <capture_mjpeg.avi> -e <HH:MM:SS>'
            sys.exit()
        elif opt == '-e':
            timestr = arg
        elif opt == '-o':
            outputfile = arg
        else:
            assert False, "unhandled option"
            sys.exit(2)

def signal_handler(signal, frame):
    raise ExitCommand()

def thread_job():
    time.sleep(secs)
    os.kill(os.getpid(), signal.SIGUSR1)

def make (factory, pipeline=None, name=None):
    elt = gst.element_factory_make(factory, name)
    if pipeline: pipeline.add(elt)
    return elt

avioutfile = ''
timestr = '00:00:05'

parse_opts(sys.argv[1:])

try:
    times = map(int, re.split(r"[:]", timestr))
except ValueError:
    print "ERROR: Not a valid number, exiting ..."
    sys.exit(2)
	
if len(times) != 3:
        print "ERROR: Not a correct time string ie. <HH:MM:SS>, exiting ..."
        sys.exit(2)

secs = times[0]*3600+times[1]*60+times[2]

print '*** Output file is   :', outputfile
print '*** Capture Duration :', timestr

mainloop = gobject.MainLoop()

link = gst.element_link_many
 
p = gst.Pipeline()

v4l2src = make("v4l2src", p)
v4l2src.set_property("norm", "PAL-BG")
v4l2src.set_property("device", "/dev/video0")
v4l2src.set_property("do-timestamp", "true")
videocaps = gst.Caps("video/x-raw-yuv,format=(fourcc)YV12,width=720,height=576,framerate=25/1")
videocapsfilter = make("capsfilter", p)
videocapsfilter.set_property("caps", videocaps)
videocapsfilter2 = make("capsfilter", p)
videocapsfilter2.set_property("caps", videocaps)
#aspectratiocrop = make("aspectratiocrop", p)
#aspectratiocrop.set_property("aspect-ratio", gst.Fraction(4,3))
videorate = make("videorate", p)
cogcolorspace = make("cogcolorspace", p)
jpegenc = make("jpegenc", p)
alsasrc = make("alsasrc", p)
alsasrc.set_property("device", "hw:2,0")
alsasrc.set_property("buffer-time", 2000000)
alsasrc.set_property("do-timestamp", "true")
audiocaps = gst.Caps("audio/x-raw-int,rate=32000,channels=1,depth=16")
audiocapsfilter = make("capsfilter", p)
audiocapsfilter.set_property("caps", audiocaps)
audioconvert = make("audioconvert", p)
mux = make("avimux", p)
filesink = make("filesink", p)
filesink.set_property("location", avioutfile)

q = []
for i in range(5):
    q.append(make("queue", p))
 
link(v4l2src, videocapsfilter, q[0], videorate, cogcolorspace, videocapsfilter2, q[1], jpegenc, q[2], mux)
link(alsasrc, audiocapsfilter, q[3], audioconvert, q[4], mux)
link(mux, filesink)
 
p.set_state(gst.STATE_PLAYING)

signal.signal(signal.SIGUSR1, signal_handler)
threading.Thread(target=thread_job).start()  # thread will fire in 5 seconds

try:
    gobject.threads_init() # necessary to allow python.thread to run
    mainloop.run()
except: # an interruption from Ctrl-C
    print "Stopping ..."
    mainloop.quit()
    p.send_event(gst.event_new_eos())
 
p.set_state(gst.STATE_NULL)

