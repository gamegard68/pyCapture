# pyCapture
Python 2 tool for capturing analogue SD video from a TV card.
Porting to python 3
Use this tool to capture video from a video recorder without risking lipsynch problems, see howto below.

HOWTO - Capture

; First before launching tool set input
v4l2-ctl --set-input 1

; Launch the tool 
; If you are having lipsynch issue launch the tool as root with a nice level -10.
./pyCapture.py

or 

sudo nice -10 ./pyCapture.py

; The tool uses the gstreamer library, so you can also use gst-launch to capture instead, see examples below:

sudo nice --10 gst-launch-0.10 -e v4l2src device=/dev/video0 norm=PAL-BG do-timestamp=true ! 'video/x-raw-yuv,format=(fourcc)YV12,width=720,height=576,framerate=25/1' ! queue ! cogcolorspace ! videorate ! 'video/x-raw-yuv,format=(fourcc)YV12,framerate=25/1' ! queue ! jpegenc ! queue ! mux. alsasrc device=hw:2,0 buffer-time=2000000 do-timestamp=true ! 'audio/x-raw-int,rate=32000,channels=1,depth=16' ! queue ! audioconvert ! queue ! mux. avimux name=mux ! filesink location=capture_test.avi

sudo nice --10 gst-launch-0.10 -e v4l2src device=/dev/video0 norm=PAL-BG do-timestamp=true ! 'video/x-raw-yuv,format=(fourcc)YV12,width=720,height=576,framerate=25/1' ! queue ! videorate ! cogcolorspace ! 'video/x-raw-yuv,format=(fourcc)YV12,framerate=25/1,interlaced=true,aspect-ratio=4/3' ! jpegenc ! queue ! mux. alsasrc device=hw:2,0 buffer-time=2000000 do-timestamp=true ! 'audio/x-raw-int,rate=32000,channels=1,depth=16' ! audioconvert ! queue ! mux. avimux name=mux ! filesink location=capture_vhs_02.avi

sudo nice --10 gst-launch-0.10 -e v4l2src device=/dev/video0 norm=PAL-BG do-timestamp=true ! 'video/x-raw-yuv,format=(fourcc)YV12,width=720,height=576,framerate=25/1' ! queue ! videorate ! cogcolorspace ! 'video/x-raw-yuv,format=(fourcc)YV12,framerate=25/1,interlaced=true,aspect-ratio=4/3' ! jpegenc ! queue ! mux. pulsesrc buffer-time=2000000 do-timestamp=true ! queue ! audioconvert ! audiorate ! 'audio/x-raw-int,rate=32000,channels=1,depth=16' ! queue ! mux. avimux name=mux ! filesink location=capture_vhs_02.avi


HOWTO - Encode to x264

Handbrake

Storage Custom 512x384
Denoise Weak
Decomb Fast
Crop: H:2x14 / V:2x12

Audio: mono mp3 lame 64kbps

Advanced Encoding Settings
level=4.0:vbv-bufsize=25000:vbv-maxrate=20000:8x8dct=0:b-adapt=2:psy-rd=1|0.2:ref=5:bframes=4




