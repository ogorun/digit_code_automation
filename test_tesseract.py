import os

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

print(pytesseract.image_to_string(Image.open(os.getcwd() + '/images/number1.png'), config= ("-l eng --oem 1 --psm 7")))
print(pytesseract.image_to_string(Image.open(os.getcwd() + '/images/numbers.png'), config= ("-l eng --oem 1 --psm 3")))
print(pytesseract.image_to_string(Image.open(os.getcwd() + '/images/text.png')))