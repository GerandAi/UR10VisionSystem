::@echo off
cd yolov5/0vision
start control_loop.py
start startup.py
::timeout /t 3
cd ..
python detect.py --source 1 --weights best.pt --img 416 --conf 0.5
cd 0vision
echo 0.0>coordinates.txt
echo 0.0>>coordinates.txt
echo 0.0>>coordinates.txt
pause