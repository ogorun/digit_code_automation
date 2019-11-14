from imutils.object_detection import non_max_suppression
import numpy as np
import pytesseract
import argparse
import cv2, os, imutils
import os

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


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
#cv2.imwrite('horizontal.jpg', horizontal)

row_white_counts = np.count_nonzero(horizontal, axis=1)
rows_with_horizontal_line_indexes = np.where((row_white_counts > 0.1*cols) & (row_white_counts < 0.7*cols))[0]
group_lower_border_indexes = np.where(np.diff(rows_with_horizontal_line_indexes)>6)[0]
group_lower_border_indexes = np.append(group_lower_border_indexes, -1)
rows_with_horizontal_line_indexes2 = rows_with_horizontal_line_indexes[group_lower_border_indexes]
#rows_with_horisontal_lines = row_white_counts[rows_with_horizontal_line_indexes]
horizontal_copy = np.copy(horizontal)
horizontal_copy[rows_with_horizontal_line_indexes2] = 255
cv2.imwrite('horizontal3.jpg', horizontal_copy)

n_diff = np.diff(np.copy(horizontal))
cv2.imwrite('n_diff.jpg', n_diff)
border_cols = np.where(np.count_nonzero(n_diff, axis=0)>10)[0]


end_border_row = rows_with_horizontal_line_indexes2[-1]
start_border_row=rows_with_horizontal_line_indexes2[0]

horizontal[:,border_cols[1]:]=0

horizontal = horizontal[start_border_row:end_border_row+1,border_cols[0]:]
bw=bw[start_border_row:end_border_row+1,border_cols[0]:]
grayImage=grayImage[start_border_row:end_border_row+1,border_cols[0]:]

cv2.imwrite('horizontal0.jpg', horizontal)
horizontal = cv2.blur(horizontal, (7,7))
cv2.imwrite('horizontal.jpg', horizontal)


vertical = np.copy(bw)
rows = vertical.shape[0]
verticalsize = rows // 10
# Create structure element for extracting vertical lines through morphology operations
verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
# Apply morphology operations
vertical = cv2.erode(vertical, verticalStructure)
vertical = cv2.dilate(vertical, verticalStructure, iterations=2)
vertical = cv2.blur(vertical, (7,7))

#vertical = cv2.dilate(vertical, verticalStructure)
#vertical = cv2.dilate(vertical, verticalStructure)
cv2.imwrite('vertical.jpg', vertical)

# find columns with with more than two peaces and approximately the same y1, y2
# unite them
columns = np.count_nonzero(vertical == 255, axis=0)

gray_copy = np.copy(grayImage)
horizontal_mask = (horizontal > 0)
gray_copy[horizontal_mask] = 255
cv2.imwrite('gray_wo_horizontal.jpg', gray_copy)

vertical_mask =  (vertical > 0)
gray_copy[vertical_mask] = 255
cv2.imwrite('gray_wo_horizontal_and_vertical.jpg', gray_copy)

numbers = gray_copy[:,:border_cols[1]-border_cols[0] - 5]
numbers[numbers > 150] = 255
# cv2.imwrite('numbers_line1.png', numbers[:rows_with_horizontal_line_indexes2[2]-start_border_row])
# cv2.imwrite('numbers_line2.png', numbers[rows_with_horizontal_line_indexes2[2]-start_border_row:rows_with_horizontal_line_indexes2[3]-start_border_row])
# cv2.imwrite('numbers_line3.png', numbers[rows_with_horizontal_line_indexes2[3]-start_border_row:rows_with_horizontal_line_indexes2[4]-start_border_row])
# cv2.imwrite('numbers_line4.png', numbers[rows_with_horizontal_line_indexes2[4]-start_border_row:rows_with_horizontal_line_indexes2[5]-start_border_row])
# cv2.imwrite('numbers_line5.png', numbers[rows_with_horizontal_line_indexes2[5]-start_border_row])
cv2.imwrite('gray_wo_horizontal_and_vertical.jpg', gray_copy)
cv2.imwrite('numbers.png', numbers)

# # Find contours in the image
# numbers_copy = numbers.copy()
# canny_output = cv2.Canny(numbers_copy, 50, 150)
#
# ctrs, hier = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
# # Get rectangles contains each contour
# rects = [cv2.boundingRect(ctr) for ctr in ctrs]
# for index, rect in enumerate(rects):
#     # Draw the rectangles
#     cv2.rectangle(numbers_copy, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
#     filename = f'number_{index}.png'
#     cv2.imwrite(filename, numbers[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]])
#     print(pytesseract.image_to_string(Image.open(os.getcwd() + '/' + filename)))
# cv2.imwrite('numbers_copy.png', numbers_copy)



cv2.imwrite('numbers.png', numbers)
cv2.imwrite('text.png', gray_copy[:,border_cols[1]-border_cols[0] - 5:])



# choose the most left vertical and crop gray_copy

# print(pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers_line1.png')))
# print(pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers_line2.png')))
# print(pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers_line3.png')))
# print(pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers_line4.png')))
# print(pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers_line5.png')))
print('============================')
number_lines_str = pytesseract.image_to_string(Image.open(os.getcwd() + '/numbers.png'), config=("--psm 6"))
print(number_lines_str)
number_lines = [line.replace(' ', '') for line in number_lines_str.split("\n")]
number_lines = [[int(ch) for ch in line] for line in number_lines if len(line) > 0]
print(number_lines)
print('============================')
text_lines_str = pytesseract.image_to_string(Image.open(os.getcwd() + '/text.png'))
print(text_lines_str)
text_lines = [line.strip() for line in text_lines_str.split("\n") if len(line.strip()) > 0]
print(text_lines)

assert len(number_lines) == len(text_lines)
