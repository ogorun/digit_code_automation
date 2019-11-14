import numpy as np, cv2, os, pytesseract
try:
    from PIL import Image
except ImportError:
    import Image


def clean_and_crop_horizontal_image(horizontal):
    cols = horizontal.shape[1]
    row_white_counts = np.count_nonzero(horizontal, axis=1)
    rows_with_horizontal_line_indexes = np.where((row_white_counts > 0.1*cols) & (row_white_counts < 0.7*cols))[0]
    group_lower_border_indexes = np.where(np.diff(rows_with_horizontal_line_indexes)>6)[0]
    group_lower_border_indexes = np.append(group_lower_border_indexes, -1)
    rows_with_horizontal_line_indexes = rows_with_horizontal_line_indexes[group_lower_border_indexes]

    start_border_row = rows_with_horizontal_line_indexes[0]
    end_border_row = rows_with_horizontal_line_indexes[-1]

    n_diff = np.diff(np.copy(horizontal))
    border_cols = np.where(np.count_nonzero(n_diff, axis=0)>10)[0]
    horizontal[:,border_cols[1]:]=0

    horizontal = horizontal[start_border_row:end_border_row+1,border_cols[0]:]
    return (horizontal, (start_border_row, end_border_row), (border_cols[0], border_cols[1]))


def create_horizontal_image(bw):
    horizontal = np.copy(bw)

    cols =  bw.shape[1]
    horizontal_size = cols // 30
    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure, iterations=2)
    return horizontal


def create_vertical_image(bw):
    vertical = np.copy(bw)
    rows = vertical.shape[0]
    verticalsize = rows // 10
    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure, iterations=2)
    vertical = cv2.blur(vertical, (7,7))

    return vertical


def clean_grayscale_image_with_helper_images(gray_image, horizontal, vertical):
    gray_copy = np.copy(gray_image)
    gray_copy[horizontal > 0] = 255
    gray_copy[vertical > 0] = 255
    return gray_copy


def detect_numbers_and_text_areas(image):
    # convert to grayscale. It will be base of image
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Now we need to get rid of all the rest.
    # Create inverted black-white image
    gray = cv2.bitwise_not(gray_image)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

    # create image with horizontal lines of grid only
    horizontal = create_horizontal_image(bw)
    horizontal, (start_border_row, end_border_row), (start_numbers_col, end_number_col) = clean_and_crop_horizontal_image(horizontal)

    bw = bw[start_border_row:end_border_row+1,start_numbers_col:]
    gray_image = gray_image[start_border_row:end_border_row+1,start_numbers_col:]

    vertical = create_vertical_image(bw)
    gray_copy = clean_grayscale_image_with_helper_images(gray_image, horizontal, vertical)

    numbers = gray_copy[:,:end_number_col-start_numbers_col - 5]
    numbers[numbers > 150] = 255
    cv2.imwrite('numbers.png', numbers)
    cv2.imwrite('text.png', gray_copy[:,end_number_col-start_numbers_col - 5:])
    return 'numbers.png', 'text.png'


def ocr(numbers_fiel_path, text_file_path):
    number_lines_str = pytesseract.image_to_string(Image.open(numbers_fiel_path), config=("--psm 6"))
    number_lines = [line.replace(' ', '') for line in number_lines_str.split("\n")]
    number_lines = [[int(ch) for ch in line] for line in number_lines if len(line) > 0]
    text_lines_str = pytesseract.image_to_string(Image.open(text_file_path))
    text_lines = [line.strip() for line in text_lines_str.split("\n") if len(line.strip()) > 0]
    assert len(number_lines) == len(text_lines)

    return [{'digits': digits, 'sentence': sentence} for digits, sentence in zip(number_lines, text_lines)]


def get_textual_connstraints_from_image(image_path):
    image = cv2.imread(image_path)

    numbers_path, text_path = detect_numbers_and_text_areas(image)
    return ocr(numbers_path, text_path)


imagePath = os.getcwd() + '/images/will_you_crack_the_code.jpg'
print(get_textual_connstraints_from_image(imagePath))
