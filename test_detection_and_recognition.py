from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import argparse
import cv2, os, imutils

# See https://www.pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/

imagePath = os.getcwd() + '/images/will_you_crack_the_code.jpg'

# initialize a rectangular and square structuring kernel
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

image = cv2.imread(imagePath)
#cv2.imshow('original', image)
print(image.shape)
#image = imutils.resize(image, height=600)
grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('gray.jpg',grayImage)

gray = cv2.bitwise_not(grayImage)
bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)
cv2.imwrite('bw.jpg',bw)
cols = bw.shape[1]
rows = bw.shape[0]

horizontal = np.copy(bw)

horizontal_size = cols // 30
# Create structure element for extracting horizontal lines through morphology operations
horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
# Apply morphology operations
horizontal = cv2.erode(horizontal, horizontalStructure)
horizontal = cv2.dilate(horizontal, horizontalStructure, iterations=2)
#horizontal = cv2.dilate(horizontal, horizontalStructure)
cv2.imwrite('horizontal.jpg', horizontal)

row_white_counts = np.count_nonzero(horizontal, axis=1)
rows_with_horizontal_line_indexes = np.where((row_white_counts > 0.1*cols) & (row_white_counts < 0.7*cols))[0]
group_lower_border_indexes = np.where(np.diff(rows_with_horizontal_line_indexes)>6)[0]
group_lower_border_indexes = np.append(group_lower_border_indexes, -1)
rows_with_horizontal_line_indexes2 = rows_with_horizontal_line_indexes[group_lower_border_indexes]
#rows_with_horisontal_lines = row_white_counts[rows_with_horizontal_line_indexes]
horizontal_copy = np.copy(horizontal)
horizontal_copy[rows_with_horizontal_line_indexes2] = 255
cv2.imwrite('horizontal3.jpg', horizontal_copy)

low_border_row = rows_with_horizontal_line_indexes2[-1]
upper_border_row=rows_with_horizontal_line_indexes2[0]

horizontal = horizontal[upper_border_row:low_border_row+1]
bw=bw[upper_border_row:low_border_row+1]
grayImage=grayImage[upper_border_row:low_border_row+1]
cv2.imwrite('horizontal2.jpg', horizontal)


vertical = np.copy(bw)
rows = vertical.shape[0]
verticalsize = rows // 10
# Create structure element for extracting vertical lines through morphology operations
verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
# Apply morphology operations
vertical = cv2.erode(vertical, verticalStructure)
vertical = cv2.dilate(vertical, verticalStructure, iterations=2)
#vertical = cv2.dilate(vertical, verticalStructure)
#vertical = cv2.dilate(vertical, verticalStructure)
cv2.imwrite('vertical.jpg', vertical)

# find columns with with more than two peaces and approximately the same y1, y2
# unite them
columns = np.count_nonzero(vertical == 255, axis=0)

gray_copy = np.copy(grayImage)
horizontal_mask = (horizontal == 255)
gray_copy[horizontal_mask] = 255
cv2.imwrite('gray_wo_horizontal.jpg', gray_copy)

vertical_mask =  (vertical == 255)
gray_copy[vertical_mask] = 255
cv2.imwrite('gray_wo_horizontal_and_vertical.jpg', gray_copy)

# choose the most left vertical and crop gray_copy


exit(0)

edges = cv2.Canny(grayImage,50,150,apertureSize = 3)
(thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
cv2.imwrite('edges-50-150.jpg',blackAndWhiteImage)
lines = cv2.HoughLinesP(edges,1,np.pi/180,100,50,15)
for rho,theta in lines[0]:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a))

    cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imwrite('houghlines3.jpg',image)
# lines = cv2.HoughLinesP(image=edges,rho=0.02,theta=np.pi/500, threshold=10,lines=np.array([]), minLineLength=minLineLength,maxLineGap=100)

#cv2.imshow('gray', grayImage)
(thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)
#cv2.imshow('black_white', blackAndWhiteImage)

# smooth the image using a 3x3 Gaussian, then apply the blackhat
# morphological operator to find dark regions on a light background
# gray = cv2.GaussianBlur(grayImage, (5, 5), 0)
# blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)
# cv2.imshow('blackhat', blackAndWhiteImage)


kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
dilate = cv2.dilate(thresh, kernel, iterations=4)
cv2.imshow('dilate', dilate)
cv2.waitKey(0)
cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]


print("Found %d objects." % len(cnts))
for (i, c) in enumerate(cnts):
    print("\tSize of contour %d: %d" % (i, len(c)))


# cv2.drawContours(image = image,
#                  contours = contours,
#                  contourIdx = -1,
#                  color = (0, 0, 255),
#                  thickness = 5)

ROI_number = 0
for c in cnts:
    area = cv2.contourArea(c)
    if area > 10000:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
        # ROI = image[y:y+h, x:x+w]
        # cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)
        # ROI_number += 1

cv2.imshow('thresh', thresh)
cv2.imshow('dilate', dilate)
cv2.imshow('image', image)
cv2.waitKey()
cv2.imshow('original', image)

cv2.waitKey(0)

# # compute the Scharr gradient of the blackhat image and scale the
# # result into the range [0, 255]
# gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
# gradX = np.absolute(gradX)
# (minVal, maxVal) = (np.min(gradX), np.max(gradX))
# gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")
#
# # apply a closing operation using the rectangular kernel to close
# # gaps in between letters -- then apply Otsu's thresholding method
# gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
# thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
# #cv2.imshow('thresh', thresh)
#
# # perform another closing operation, this time using the square
# # kernel to close gaps between lines of the MRZ, then perform a
# # series of erosions to break apart connected components
# thresh2 = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
# thresh2 = cv2.erode(thresh2, None, iterations=4)
# #cv2.imshow('thresh2', thresh2)
# #cv2.waitKey(0)
#
# p = int(image.shape[1] * 0.05)
# thresh[:, 0:p] = 0
# thresh[:, image.shape[1] - p:] = 0
# thresh2[:, 0:p] = 0
# thresh2[:, image.shape[1] - p:] = 0
#
# for (im, name) in [ (thresh2, 'thresh2'), (thresh, 'thresh'), (blackhat, 'blackhat'), (grayImage, 'gray'),  (image, 'original')]:
#     cnts = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL,
#                             cv2.CHAIN_APPROX_SIMPLE)[-2]
#     cnts = imutils.grab_contours(cnts)
#     cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
#
#     # loop over the contours
#     roi = None
#     for c in cnts:
#         # compute the bounding box of the contour and use the contour to
#         # compute the aspect ratio and coverage ratio of the bounding box
#         # width to the width of the image
#         (x, y, w, h) = cv2.boundingRect(c)
#         ar = w / float(h)
#         crWidth = w / float(gray.shape[1])
#
#         # check to see if the aspect ratio and coverage width are within
#         # acceptable criteria
#         if ar > 5 and crWidth > 0.75:
#             # pad the bounding box since we applied erosions and now need
#             # to re-grow it
#             pX = int((x + w) * 0.03)
#             pY = int((y + h) * 0.03)
#             (x, y) = (x - pX, y - pY)
#             (w, h) = (w + (pX * 2), h + (pY * 2))
#
#             # extract the ROI from the image and draw a bounding box
#             # surrounding the MRZ
#             roi = im[y:y + h, x:x + w].copy()
#             cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
#             break
#
#     # show the output images
#     cv2.imshow(name, im)
#     cv2.imshow(name + " ROI", roi)
#
# cv2.waitKey(0)