import cv2
import numpy as np

img = cv2.imread('solver/seal.jpg', 0)
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
imcolor = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
ret, thresh = cv2.threshold(img, 90, 255, 1)

kernel = np.ones((5,5), np.uint8) 
img_erosion = cv2.erode(thresh, kernel, iterations=1) 
img_dilation = cv2.dilate(img_erosion, kernel, iterations=1) 

# cv2.imshow('img_erosion', img_erosion)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
# cv2.imshow('img_dilation', img_dilation)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

contours, hierarchy = cv2.findContours(img_dilation,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
# img1 = cv2.drawContours(imcolor, contours, -1, (0,255,255), 3)
#
# cv2.imshow('img1', img1)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

cnt = contours[0]
print(len(contours))

hull = cv2.convexHull(cnt)
simplified_cnt = cv2.approxPolyDP(hull,0.001*cv2.arcLength(hull,True),True)

print(simplified_cnt)

# img2 = cv2.drawContours(imcolor, [simplified_cnt], 0, (0,255,0), 3)

# TODO: REMOVE!!! This was only to prove that findHomography needs just 4 input points
# simplified_cnt has to be further simplified to four points
# (probably easy math)
# Update: simplified_cnt actually works well for well-lit, higher contrast photos :P
cnt = np.array([[[423., 390.]],[[97., 385.]],[[114., 69.]],[[427.,61.]]],dtype=np.single)

H,mask = cv2.findHomography(cnt, np.array([[[128., 128.]],[[0., 128.]],[[0., 0.]],[[128.,0.]]],dtype=np.single), cv2.RANSAC)

final_image = cv2.warpPerspective(img,H,(128, 128))

# cv2.imshow('final_image', final_image)
# cv2.waitKey(0)

more_ret, more_thresh = cv2.threshold(final_image, 40, 255, 0)

kernel = np.ones((5,5), np.uint8) 
img_erosion2 = cv2.erode(more_thresh, kernel, iterations=1) 
img_dilation2 = cv2.dilate(img_erosion2, kernel, iterations=1) 

cv2.imshow('img_dilation2', img_dilation2)
cv2.waitKey(0)
cv2.destroyAllWindows()


