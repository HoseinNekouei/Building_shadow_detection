import cv2 as cv
import numpy as np
import uuid

count = 0
bbox_list = [] 


def crop_image(x,y,w,h):
    global count
    x -=  200
    y -= 200
    if y < 0: y = 0
    if x < 0: x = 0
    if (x + 700) > width: x -= 700 - (width - x )
    if (y + 700) > height: y -= 700 - (height - y) 
    #ROI = frame[y:y+h , x:x+w]
    #croped image with green rectangle
    cropped_frame = frame[y : y + 700 , x : x + 700]
    #croped image without green rectangle
    cropped_frame_clear = frame_copy[y : y + 700 , x : x + 700]
    fileName = uuid.uuid1().hex
    try:
        if cropped_frame.size > 0 :
            cv.imwrite('Photos/Cropped/{}.jpg'.format(fileName),cropped_frame)
            cv.imwrite('Photos/Cropped-1/{}.jpg'.format(fileName),cropped_frame_clear)
            count +=1
            return True
    except:
        print('cropped frame is empty')


def iteration_Search(x,y,w,h):
    status = False
    for item in bbox_list:
        if (item[0] >= (x - 25) and \
            item[0] <= (x + 25) and \
            item[2] >= (w - 25) and \
            item[2] <= (w + 25) and \
            item[3] >= (h - 25) and \
            item[3] <= (h + 25) or \
            item[1] >= (y - 25) and \
            item[1] <= (y + 25) and \
            item[2] >= (w - 25) and \
            item[2] <= (w + 25) and \
            item[3] >= (h - 25) and \
            item[3] <= (h + 25)): 
            status = True
            break
    if status == True:
        return True
    else:
        return False


#Get Video
capVid = cv.VideoCapture('videos/DJI_0001.Mp4')
while capVid.isOpened():   
    ret,frame = capVid.read()
    if not ret: break

    height,width,_ = frame.shape
    frame_copy = frame.copy()
    frame = cv.GaussianBlur(frame,(85,85),0,0)

    hsv_frame = cv.cvtColor(frame,cv.COLOR_BGR2HSV)

    color_low = np.array([70,24,62])
    color_up = np.array([124,111,78])
    color_mask =cv.inRange(hsv_frame,color_low,color_up)

    contours,_ = cv.findContours(color_mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    
    for cont in contours:
        contourArea = cv.contourArea(cont)
        if contourArea > 5000  and contourArea < 90000: 
            hull = cv.convexHull(cont)
            cv.drawContours(frame,[hull],-1,(120,120,120),3)
            #w=width , h=height
            x,y,w,h = cv.boundingRect(cont)
            cv.putText(frame,str((x,y,w,h)),(x-10,y-10),cv.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2) 

            if w < 320 and h < 320:    
                if y >= 100 and ( (y+h) + 130 ) <= height:
                    if x >= 100 and ( (x+w) + 130 ) <= width:
                        # call a function for search any iteration contours
                        isIteration = iteration_Search(x,y,w,h)
                        if isIteration == False:
                            cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
                            #append a contour in the list
                            bbox_list.append((x,y,w,h))
                            if crop_image(x,y,w,h): print(len(bbox_list))

    frame = cv.resize(frame,(900,700))
    cv.imshow('frame',frame)

    color_mask = cv.resize(color_mask,(900,700))
    cv.imshow('mask',color_mask)

    key = cv.waitKey(60)
    if key & 0xff == ord('c'): 
        break

cv.destroyAllWindows()    
capVid.release()

print('Done, {} image/s cropped!'.format(count))