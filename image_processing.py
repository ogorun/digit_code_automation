import numpy as np, cv2, os, textwrap
from text_recognition import ocr


def clean_horizontal_image(horizontal):
    cols = horizontal.shape[1]
    row_white_counts = np.count_nonzero(horizontal, axis=1) # count number of white pixels along horizontal lines
    rows_with_horizontal_line_indexes = np.where((row_white_counts > 0.1*cols) & (row_white_counts < 0.7*cols))[0] # indexes of rows with long white lines
    group_lower_border_indexes = np.where(np.diff(rows_with_horizontal_line_indexes)>6)[0]
    group_lower_border_indexes = np.append(group_lower_border_indexes, -1)
    rows_with_horizontal_line_indexes = rows_with_horizontal_line_indexes[group_lower_border_indexes]

    start_border_row = rows_with_horizontal_line_indexes[0] - 5
    end_border_row = rows_with_horizontal_line_indexes[-1]

    n_diff = np.diff(np.copy(horizontal))
    border_cols = np.where(np.count_nonzero(n_diff, axis=0)>10)[0]
    start_numbers_col = border_cols[0]
    end_numbers_col = border_cols[-1]

    horizontal[:,end_numbers_col:]=0
    horizontal[:,:start_numbers_col]=0
    horizontal[:start_border_row,:] = 0
    horizontal[end_border_row:,:] = 0

    horizontal[:, end_numbers_col] = 127
    horizontal[:, start_numbers_col] = 127
    horizontal[start_border_row, :] = 127
    horizontal[end_border_row,:] = 127

    return (horizontal, (start_border_row, end_border_row), (start_numbers_col, end_numbers_col))


def create_horizontal_image(bw):
    horizontal = np.copy(bw)

    cols =  bw.shape[1]
    horizontal_size = cols // 30
    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure, iterations=2)
    #horizontal = cv2.blur(horizontal, (7,7))
    return horizontal


def create_vertical_image(bw):
    vertical = np.copy(bw)
    rows = vertical.shape[0]
    verticalsize = rows // 10 # The image is smaller now, so kernel size is changed from size/30 -> size/10
    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure, iterations=2)
    vertical = cv2.blur(vertical, (7,7)) # blur should make the lines wider

    # Avoid numbers influence
    black_mask = np.count_nonzero(vertical, axis=0) < 0.9*vertical.shape[0]
    vertical[:,black_mask] = 0

    return vertical


def clean_grayscale_image_with_helper_images(gray_image, horizontal, vertical):
    gray_image[horizontal > 0] = 255
    gray_image[vertical > 0] = 255


def detect_numbers_and_text_areas(image):
    # convert to grayscale. It will be base of digits and text area images
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Now we need to get rid of all the rest.
    # Create inverted black-white image
    ret, bw = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('images/bw.jpg', bw)
    #bw = cv2.adaptiveThreshold(inverted, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2) # black-white version

    # create image with horizontal lines of grid only
    horizontal = create_horizontal_image(bw)
    horizontal, (start_border_row, end_border_row), (start_numbers_col, end_number_col) = clean_horizontal_image(horizontal)

    horizontal = horizontal[start_border_row:end_border_row+1,start_numbers_col:]
    bw = bw[start_border_row:end_border_row+1,start_numbers_col:]
    gray_image = gray_image[start_border_row:end_border_row+1,start_numbers_col:]

    vertical = create_vertical_image(bw)
    clean_grayscale_image_with_helper_images(gray_image, horizontal, vertical)

    numbers_path = 'images/numbers.png'
    text_path = 'images/text.png'
    numbers = gray_image[:,:end_number_col-start_numbers_col - 10]
    numbers[numbers > 150] = 255

    cv2.imwrite(numbers_path, numbers)
    cv2.imwrite(text_path, gray_image[:,end_number_col-start_numbers_col - 10:])
    return numbers_path, text_path


def get_textual_connstraints_from_image(image_path):
    image = cv2.imread(image_path)

    numbers_path, text_path = detect_numbers_and_text_areas(image)
    return ocr(numbers_path, text_path)


def constraint2image(constraints, filename):
    image = cv2.imread('images/will_you_crack_the_code_base.png')
    digits_num = len(constraints[0]['digits'])

    cv2.putText(image, 'WILL YOU CRACK THE CODE?', (180, 225), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,0,0), 2)
    cv2.putText(image, 'CODE', (60, 475), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0,0,0), 2)

    # squares for final code
    left = 100 - 20*digits_num
    for i in range(digits_num):
        cv2.rectangle(image, (left + i*40, 400), (left+(i+1)*40, 440), (0,0,0), 2)

    # constraint lines
    left = 280 - 20*digits_num
    top = 388 - len(constraints)*25
    for index, constraint in enumerate(constraints):
        for i in range(digits_num):
            cv2.rectangle(image, (left + i*40, index*50 + top), (left + (i+1)*40, index*50 + top + 40), (0,0,0), 2)
            cv2.putText(image, str(constraint['digits'][i]), (left + 10 + i*40, index*50 + top + 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,0,0), 2)
        text = textwrap.wrap(constraint['sentence'], 42)
        top_indent = 20 if len(text) == 1 else 20-(len(text)-1)*10
        for line_index, line in enumerate(text):
            cv2.putText(image, line, (375, index*50 + top + top_indent + 20*line_index), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0,0,0), 1)

    filepath = f"generated/{filename}.jpg"
    cv2.imwrite(filepath, image)
    return filepath


if __name__ == '__main__':
    imagePath = os.getcwd() + '/images/will_you_crack_the_code.jpg'
    conditions = get_textual_connstraints_from_image(imagePath)
    for condition in conditions:
        print(condition)
