import pytesseract, re
try:
    from PIL import Image
except ImportError:
    import Image


def text_to_sentences(text_lines_str):
    text_lines = [re.sub('[^a-zA-Z\s]+', '',  line.strip()) for line in text_lines_str.split("\n") if len(line.strip()) > 0]
    final_text_lines = []
    current_text_line = []
    for line in text_lines:
        if len(current_text_line) > 0 and line[0].isupper():
            final_text_lines.append(' '.join(current_text_line))
            current_text_line = []
        current_text_line.append(line)

    # Finish lines
    final_text_lines.append(' '.join(current_text_line))

    return final_text_lines


def ocr(numbers_field_path, text_file_path):
    number_lines_str = pytesseract.image_to_string(Image.open(numbers_field_path), config=("--psm 6"))
    number_lines = [re.sub('[^0-9]','', line) for line in number_lines_str.split("\n")]
    number_lines = [[int(ch) for ch in line] for line in number_lines if len(line) > 0]
    text_lines_str = pytesseract.image_to_string(Image.open(text_file_path), config=("--psm 6"))
    text_lines = text_to_sentences(text_lines_str)
    assert len(number_lines) == len(text_lines)

    return [{'digits': digits, 'sentence': sentence} for digits, sentence in zip(number_lines, text_lines)]
