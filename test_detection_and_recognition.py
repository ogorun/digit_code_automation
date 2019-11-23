import numpy as np, cv2, os, pytesseract, textwrap, re
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

    start_border_row = rows_with_horizontal_line_indexes[0] - 5
    end_border_row = rows_with_horizontal_line_indexes[-1]

    n_diff = np.diff(np.copy(horizontal))
    border_cols = np.where(np.count_nonzero(n_diff, axis=0)>10)[0]
    horizontal[:,border_cols[-1]:]=0

    horizontal = horizontal[start_border_row:end_border_row+1,border_cols[0]:]
    return (horizontal, (start_border_row, end_border_row), (border_cols[0], border_cols[-1]))


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

    # Avoid numbers influence
    black_mask = np.count_nonzero(vertical, axis=0) < 0.9*vertical.shape[0]
    vertical[:,black_mask] = 0

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

    numbers = gray_copy[:,:end_number_col-start_numbers_col - 10]
    numbers[numbers > 150] = 255
    cv2.imwrite('numbers.png', numbers)
    cv2.imwrite('text.png', gray_copy[:,end_number_col-start_numbers_col - 10:])
    return 'numbers.png', 'text.png'


def text_to_sentences(text_lines_str):
    text_lines = [re.sub('[^a-zA-Z\s]+', '',  line.strip()) for line in text_lines_str.split("\n") if len(line.strip()) > 0]
    final_text_lines = []
    current_text_line = []
    for line in text_lines:
        if line[0].isupper() and len(current_text_line) > 0:
            final_text_lines.append(' '.join(current_text_line))
            current_text_line = []
        current_text_line.append(line)

    # Finish lines
    final_text_lines.append(' '.join(current_text_line))

    return final_text_lines


def ocr(numbers_fiel_path, text_file_path):
    number_lines_str = pytesseract.image_to_string(Image.open(numbers_fiel_path), config=("--psm 6"))
    number_lines = [re.sub('[^0-9]','', line) for line in number_lines_str.split("\n")]
    number_lines = [[int(ch) for ch in line] for line in number_lines if len(line) > 0]
    text_lines_str = pytesseract.image_to_string(Image.open(text_file_path))
    text_lines = text_to_sentences(text_lines_str)
    assert len(number_lines) == len(text_lines)

    return [{'digits': digits, 'sentence': sentence} for digits, sentence in zip(number_lines, text_lines)]


def get_textual_connstraints_from_image(image_path):
    image = cv2.imread(image_path)

    numbers_path, text_path = detect_numbers_and_text_areas(image)
    return ocr(numbers_path, text_path)


def constraint2image(constraints, filename):
    image = cv2.imread('images/will_you_crack_the_code_base.png')
    digits_num = len(constraints[0]['digits'])

    cv2.putText(image, 'WILL YOU CRACK THE CODE?', (180, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    cv2.putText(image, 'CODE', (60, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

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
            cv2.putText(image, str(constraint['digits'][i]), (left + 10 + i*40, index*50 + top + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,0), 2)
        text = textwrap.wrap(constraint['sentence'], 42)
        top_indent = 20 if len(text) == 1 else 20-(len(text)-1)*10
        for line_index, line in enumerate(text):
            cv2.putText(image, line, (375, index*50 + top + top_indent + 20*line_index), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

    filepath = f"generated/{filename}.jpg"
    cv2.imwrite(filepath, image)
    return filepath


if __name__ == '__main__':
    imagePath = os.getcwd() + '/images/will_you_crack_the_code.jpg'
    print(get_textual_connstraints_from_image(imagePath))
