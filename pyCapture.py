#!/usr/bin/python

import sys, gobject

try:
    import pygst
    pygst.require("0.10")
    import gst
except:
    sys.exit(1)
 
mainloop = gobject.MainLoop()
 
# original pipeline:
"""
gst-launch-1.0 -v avimux name=mux v4l2src device=/dev/video0 do-timestamp=true ! 'video/x-raw,format=(string)YUY2,width=(int)720,height=(int)576' !\
videorate ! 'video/x-raw,format=(string)YV12,framerate=25/1' ! videoconvert ! 'video/x-raw,format=(string)YV12,width=(int)720,height=(int)576' !\
jpegenc  ! queue ! mux. alsasrc device=hw:2,0 ! 'audio/x-raw,format=(string)S16LE,rate=(int)32000,channels=(int)1' !\
audiorate ! audioresample ! 'audio/x-raw,rate=(int)32000' ! audioconvert ! 'audio/x-raw,channels=(int)1' ! queue ! mux. mux. ! filesink location=capture.avi
"""
 
def make (factory, pipeline=None, name=None):
    elt = gst.element_factory_make(factory, name)
    if pipeline: pipeline.add(elt)
    return elt
 
link = gst.element_link_many
 
p = gst.Pipeline()

v4l2src = make("v4l2src", p)
v4l2src.set_property("norm", "PAL-BG")
v4l2src.set_property("device", "/dev/video0")
caps = gst.Caps("video/x-raw-yuv,width=720,height=576,framerate=25/1")
capsfilter = make("capsfilter", p)
capsfilter.set_property("caps", caps)
capsfilter2 = make("capsfilter", p)
capsfilter2.set_property("caps", caps)
tee = make("tee", p)
xvimagesink = make("xvimagesink", p)
xvimagesink.set_property("sync", "false")
videorate = make("videorate", p)
pulsesrc = make("pulsesrc", p)
audiocaps = gst.Caps("audio/x-raw-int,rate=32000,channels=1,depth=16")
audiocapsfilter = make("capsfilter", p)
audiocapsfilter.set_property("caps", audiocaps)
audioconvert = make("audioconvert", p)
mux = make("avimux", p)
filesink = make("filesink", p)
filesink.set_property("location", "capture.avi")
 
q = []
for i in range(5):
    q.append(make("queue", p))
 
link(v4l2src, capsfilter, tee, q[0], xvimagesink)
link(tee, q[1], videorate, capsfilter2, q[2], mux)
link(pulsesrc, audiocapsfilter, q[3], audioconvert, q[4], mux)
link(mux, filesink)
 
p.set_state(gst.STATE_PLAYING)
 
try:
    mainloop.run()
except: # an interruption from Ctrl-C
    print "stopping"
 
p.set_state(gst.STATE_NULL)

