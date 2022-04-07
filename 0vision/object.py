import pyrealsense2 as rs
import numpy as np
import keyboard

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

#######################################################################

import cv2
#thres = 0.45 # Threshold to detect object
thres = gerandthres = 0.12
gerandalpha = 0.16
 
##cap = cv2.VideoCapture(2)
##cap.set(3,1280)
##cap.set(4,720)
##cap.set(10,70)

classNames= []
classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')
 
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'
 
net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


### Start streaming
##pipeline.start(config)

# get camera intrinsics
profile = pipeline.start(config)
intr = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
try:
    i=1
    while i<30:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=gerandalpha), cv2.COLORMAP_JET)
        #depth_colormap = color_image

    ##    depth_colormap_dim = depth_colormap.shape
    ##    color_colormap_dim = color_image.shape
    ##
    ##    # If depth and color resolutions are different, resize color image to match depth image for display
    ##    if depth_colormap_dim != color_colormap_dim:
    ##        resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
    ##        images = np.hstack((resized_color_image, depth_colormap))
    ##    else:
    ##        images = np.hstack((color_image, depth_colormap))
        
        #success,img = cap.read()
        classIds, confs, bbox = net.detect(depth_colormap,confThreshold=thres)
        #print(classIds,bbox)

     
        if len(classIds) != 0:
            areabefore=310000
            goodbox=[]
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                areanow=box[2]*box[3]
                if areanow<areabefore and areanow<160000 and areanow>10000 and classId!=9 and classId!=67 and classId!=61 and classId!=7 and classId!=15 and classId!=90 and classId!=19 and classId!=5 and classId!=1 and classId!=16 and classId!=28 and classId!=11 and classId!=86 and classId!=10:
                    dx=round(0.5*box[2])
                    dy=round(0.5*box[3])
                    centre=[box[0]+dx, box[1]+dy]
                    dist = depth_frame.get_distance(centre[0], centre[1])*1000
                    if dist < 1000 :
                        goodbox=box
                        areabefore=areanow
                        cv2.putText(depth_colormap,classNames[classId-1].upper(),(goodbox[0]+10,goodbox[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                        cv2.putText(depth_colormap,str(round(confidence*100,2)),(goodbox[0]+200,goodbox[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    
            if len(goodbox) != 0:
                cv2.rectangle(depth_colormap,goodbox,color=(255,255,255),thickness=2)
                dx=round(0.5*goodbox[2])
                dy=round(0.5*goodbox[3])
                centre=[goodbox[0]+dx, goodbox[1]+dy]
                dist = depth_frame.get_distance(centre[0], centre[1])*1000
                #calculate real world coordinates
                Xtemp = round(dist*(centre[0] -intr.ppx)/intr.fx)
                print('intr.ppx={}'.format(intr.ppx))
                print(intr.fx)
                Ytemp = round(dist*(centre[1] -intr.ppy)/intr.fy)
                Ztemp = round(dist)
                if Xtemp != 0 :
                    with open('coordinates.txt', 'w') as f:
                        f.write(str(Xtemp))
                        f.write('\n')
                        f.write(str(Ytemp))
                        f.write('\n')
                        f.write(str(Ztemp))
                    #print(Xtemp, Ytemp, Ztemp)
     
        cv2.imshow("Output",depth_colormap)
        cv2.waitKey(1)

        # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('Esc'):  # if key 'q' is pressed
            with open('coordinates.txt', 'w') as f:
                f.write(str(0))
                f.write('\n')
                f.write(str(0))
                f.write('\n')
                f.write(str(0))
            print('You switched off the vision system!')
            break  # finishing the loop
        
            ##break  # if user pressed a key other than the given key the loop will break

        #i=i+1

finally:
    # Stop streaming
    pipeline.stop()
