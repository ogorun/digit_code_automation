from test_detection_and_recognition import get_textual_connstraints_from_image
from sentence_parsing import extract_condition_from_sentence
from crack_code import crack_code

image_path = 'images/will_you_crack_the_code.jpg'
constraints = get_textual_connstraints_from_image(image_path)
for constraint in constraints:
    data = extract_condition_from_sentence(constraint['sentence'])
    constraint['valid_and_placed'] = data['valid_and_placed']
    constraint['valid_on_invalid_places'] = data['valid_on_invalid_places']

print(constraints)
print(crack_code(constraints))