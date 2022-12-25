import cv2 as cv
import numpy as np
import uuid

def draw_contour(rect):

    boxpoint = cv.boxPoints(rect)
    boxpoint = np.reshape(boxpoint,(4,1,2))
    boxpoint = np.int32(boxpoint)

    #  calculate edge of contour
    centerX = int(rect[0][0])
    centerY = int(rect[0][1])
    rightY = int(boxpoint[1][0][1])

    if (height - centerY ) >= 256:
        if (width - centerX ) >= 256:
            if (centerX - 0 ) >= 256:
                if (centerY - 0 ) >= 256:
                    crop_image(centerX,centerY,rightY)


count = 0
def crop_image(centerX,centerY,rightY):
    global count
    global height
    global width

    height += 50
    width += 50
    leftupX = centerX - 350
    rightBtmX = centerX + 350
    rightBtmY = centerY + 350
    rightY -=  100  

    if (rightY + 700 ) > height:
        rightY -=  (700 - (rightBtmY - rightY))
        rightBtmY = (rightY + 700)
    if (leftupX + 700 ) > width:
        leftupX -= (700 - (rightBtmX - leftupX))
        rightBtmX = (leftupX + 700)
    if leftupX < 0:
        leftupX = 0
        rightBtmX = 700    
    if rightBtmX <= width and rightBtmY <= height:  
        cv.rectangle(frame_copy,(leftupX,rightY),(rightBtmX,rightBtmY),(255,0,0),3)     
        #ROI = frame[y:y+h , x:x+w]
        cropped_frame = frame[rightY:rightY+700 , leftupX:leftupX+700]
        fileName = uuid.uuid1().hex
        try:
            if cropped_frame.size > 0 :
                cv.imwrite('Photos/Cropped/{}.jpg'.format(fileName),cropped_frame)
                count +=1
        except:
            print('cropped frame is empty')


bbox_list = [] 
#Get Video
capVid = cv.VideoCapture('videos/DJI_0002.Mp4')

while capVid.isOpened():   
    ret,frame = capVid.read()
    if not ret: break

    height,width,_ = frame.shape
    frame = cv.GaussianBlur(frame,(9,9),0,0)
    frame_copy = frame.copy()

    hsv_frame = cv.cvtColor(frame,cv.COLOR_BGR2HSV)

    color_low = np.array([60,27,64])
    color_up = np.array([134,129,100])
    color_mask =cv.inRange(hsv_frame,color_low,color_up)

    contours,_ = cv.findContours(color_mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
    # print(_)
    for cont in contours:
        contourArea = cv.contourArea(cont)
        if contourArea > 5000  and contourArea < 90000: 
            rect = cv.minAreaRect(cont)                    
            
            if rect[1][1] <400:
                status = False
                for item in bbox_list:
                        # (rect[0][0] - 20) <= item[0][0] and \
                        # (rect[0][0] + 20) >= item[0][0] and \
                    if (rect[0][1] - 20) <= item[0][1] and \
                        (rect[0][1] + 20) >= item[0][1] and \
                        (rect[1][0] - 40) <= item[1][0] and \
                        (rect[1][0] + 40) >= item[1][0] and \
                        (rect[1][1] - 40) <=item[1][1]  and \
                        (rect[1][1] + 40) >= item[1][1]:
                            status = True
                                
                if not status:
                    (center,wh,angle) = rect
                    bbox_list.append(
                        ((int(center[0]),int(center[1]))
                        ,(int(wh[0]),int(wh[1])))
                        )
                    draw_contour(rect)
                    status = False
                    print(bbox_list)

    frame_copy = cv.resize(frame_copy,(900,700))
    cv.imshow('frame',frame_copy)

    key = cv.waitKey(60)
    if key & 0xff == ord('c'): 
        break

cv.destroyAllWindows()    
capVid.release()

print('Done, {} image/s cropped!'.format(count))