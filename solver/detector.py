import cv2
import numpy as np

from puzzle import get_board_from_img 


IMG_SIZE = 128

# TODO: define a better way to define this for different images
# For now, I'll just focussing on solving the puzzle
BLACK_THRESH = 40

def show_image(image_obj, caption = ''):
  cv2.imshow(caption, image_obj)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  
def get_line_coeffs(x1, y1, x2, y2):
  a = 0.0
  b = 0.0
  c = 0.0
  
  if y2 - y1 == 0:
    a = 0.0
    b = 1.0
    c = y1
  elif x2 - x1 == 0:
    a = 1.0
    b = 0.0
    c = x1
  else:
    n = y2 - y1
    d = x2 - x1
    m = n/d
    c = (y1 - (m * x1))
    b = 1.0
    a = -1 * m
  
  return a, b, c
  
def get_lines_by_categories(lines, w, h):
  up_hori = []
  down_hori = []
  left_vert = []
  right_vert = []
  
  for line in lines:
    a, b, c = line
    
    near_hori = a < 0.5 and a > -0.5
    near_vert = b == 0 or a > 2
    
    if near_hori:
      if c < h/2:
        up_hori.append(line)
      else:
        down_hori.append(line)
    elif near_vert:
      comp = c if b == 0 else c/a
      if comp < w/2:
        left_vert.append(line)
      else:
        right_vert.append(line)
  
  lines_by_categories = {
    'up_hori': up_hori,
    'down_hori': down_hori,
    'left_vert': left_vert,
    'right_vert': right_vert
  }
  return lines_by_categories
  
def get_intersection(line1, line2):
  a1, b1, c1 = line1
  a2, b2, c2 = line2
  
  det = a1 * b2 - a2 * b1;
  
  x = ((b2 * c1) - (b1 * c2)) / det;
  y = ((a1 * c2) - (a2 * c1)) / det;
  
  return [x, y]


def get_pattern_img():
  # img = cv2.imread('./images/97_1.jpg', 0)
  # img = cv2.imread('./images/45_2.jpg', 0)
  # img = cv2.imread('./images/61_2.jpg', 0)
  # img = cv2.imread('./images/65_2.jpg', 0)
  # img = cv2.imread('./images/6_1.jpg', 0)
  img = cv2.imread('./images/18_1.jpg', 0)
  # img = cv2.imread('./images/van.jpg', 0)
  # img = cv2.imread('./images/car.jpg', 0)
  # img = cv2.imread('./images/periscope.jpg', 0)
  # img = cv2.imread('./images/greek_temple.jpg', 0)
  # img = cv2.imread('./images/crossroads.jpg', 0)
  # img = cv2.imread('./images/no_single_squares.jpg', 0)
  img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)

  h, w = img.shape[:2]
  
  if abs(w - h) < 10:
    return cv2.resize(img, (128,128))
  
  mask_color = (0, 0, 0)

  hull_mask = img.copy()
  hull_mask = cv2.rectangle(hull_mask, (0, 0), (w, h), mask_color, -1)
  hull_mask_lines = hull_mask.copy()

  # show_image(img)
  # show_image(hull_mask)

  # # imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  imcolor = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
  ret, thresh = cv2.threshold(img, 100, 255, 1)


  kernel = np.ones((5,5), np.uint8)
  img_erosion = cv2.erode(thresh, kernel, iterations=1)
  img_dilation = cv2.dilate(img_erosion, kernel, iterations=2)
  img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

  # show_image(img_erosion, 'erod')
  # show_image(img_dilation, 'dil')

  contours, hierarchy = cv2.findContours(img_erosion,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  img1 = cv2.drawContours(imcolor, contours, -1, (0,0,255), 3)

  # # foo 1
  # show_image(img1, 'ctrs')

  areas = [cv2.contourArea(cnt) for cnt in contours]
  max_area = max(areas)
  cnt = contours[areas.index(max_area)]
  # print(areas)
  # # print(cnt)
  # print(len(contours))

  hull = cv2.convexHull(cnt)
  simplified_cnt = cv2.approxPolyDP(hull,0.001*cv2.arcLength(hull,True),True)
  # hull = cv2.convexHull(simplified_cnt)

  img2 = cv2.drawContours(imcolor, [simplified_cnt], 0, (0,255,0), 3)

  hull_mask_drawn = cv2.drawContours(hull_mask, [simplified_cnt], 0, (255,255,255), 2)

  # # foo 2
  # show_image(img2, 'simplifiedctrs')
  # show_image(hull_mask_drawn)


  # edges = cv2.Canny(hull_mask_drawn,50,150,apertureSize = 5)
  # show_image(edges, "edges")
  minLineLength = 100
  maxLineGap = 10
  lines = cv2.HoughLinesP(hull_mask_drawn,1,np.pi/180,100,minLineLength,maxLineGap)
  # print(lines, lines[0])
  lines_as_coeffs = []
  for line in lines:
      x1,y1,x2,y2 = line[0]
    
      a, b, c = get_line_coeffs(x1,y1,x2,y2)
      # print(line[0], a, b, c)
    
      lines_as_coeffs.append((a, b, c))
    
      # even if you categorize, WE NEED ALL EXACT values, to get intersection points. I think.
    
      cv2.line(hull_mask_lines,(x1,y1),(x2,y2),(155,155,155),2)
    
  # # foo 3
  # show_image(hull_mask_lines, "LINES")

  lbc = get_lines_by_categories(lines_as_coeffs, w, h)
  top_left = get_intersection(lbc['up_hori'][0], lbc['left_vert'][0])
  top_right = get_intersection(lbc['up_hori'][0], lbc['right_vert'][0])
  bottom_left = get_intersection(lbc['down_hori'][0], lbc['left_vert'][0])
  bottom_right = get_intersection(lbc['down_hori'][0], lbc['right_vert'][0])

  cnt = np.array([[top_left],[top_right],[bottom_left],[bottom_right]], dtype=np.single)

  H,mask = cv2.findHomography(cnt, np.array([[[0., 0.]],[[IMG_SIZE, 0.]],[[0., IMG_SIZE]],[[IMG_SIZE,IMG_SIZE]]],dtype=np.single), cv2.RANSAC)
  cropped_pattern = cv2.warpPerspective(img,H,(IMG_SIZE, IMG_SIZE))

  # # foo 4
  # show_image(cropped_pattern, 'cropped')

  

  return cropped_pattern

  # for row in pattern_vals:
#     print(" ".join(row))



def get_black_thresh():
  return BLACK_THRESH



# more_ret, more_thresh = cv2.threshold(img, 40, 255, 0)
#
# kernel = np.ones((5,5), np.uint8)
# img_erosion2 = cv2.erode(more_thresh, kernel, iterations=1)
# img_dilation2 = cv2.dilate(img_erosion2, kernel, iterations=1)
#
# cv2.imshow('img_dilation2', img_dilation2)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#
#
# edges = cv2.Canny(img_dilation2,50,150,apertureSize = 3)
# minLineLength = 100
# maxLineGap = 10
# lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
# for x1,y1,x2,y2 in lines[0]:
#     cv2.line(imcolor,(x1,y1),(x2,y2),(0,255,0),2)
#
# cv2.imshow('img_dilation2', imcolor)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
#



