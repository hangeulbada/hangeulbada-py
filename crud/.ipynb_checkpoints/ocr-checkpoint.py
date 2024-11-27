# Import
import io
import re
import cv2
import easyocr
import numpy as np


def group_text_by_coord(texts, coordinates, y_threshold=40):
    """
    Group Text by Coordinates
    
    Parameters:
        - texts: List of Texts
        - coordinates: List of Coordinates [[x1, y1], [x2, y2], ...]
        - y_threshold: Y Difference Threshold
    
    Returns:
        - [['str1', 'str1-1'], ['str2', 'str2-1']]
    """
    # Sort Coordinates
    sorted_coords = sorted(coordinates, key=lambda p: p[1])
    
    # List of Coordinate and Text Pairs
    coord_text_pairs = list(zip(coordinates, texts))
    
    groups = []
    current_group = []
    current_y = sorted_coords[0][1]
    
    # Sort Coordinate and Text Pairs by Y
    sorted_pairs = sorted(coord_text_pairs, key=lambda x: x[0][1])
    
    for coord, text in sorted_pairs:
        if not current_group or abs(coord[1] - current_y) <= y_threshold:
            current_group.append((coord, text))
        else:
            # Sort Group by X
            groups.append(sorted(current_group, key=lambda x: x[0][0]))
            current_group = [(coord, text)]
            current_y = coord[1]
    
    # Append Last Group
    if current_group:
        groups.append(sorted(current_group, key=lambda x: x[0][0]))
    
    # Get Texts Each Group
    text_groups = [[pair[1] for pair in group] for group in groups]
    
    return text_groups


def text_preprocess(infer_text, first_coord, coord, y_thres):
    """ Text Preprocessing """
    number_count = 0
    number_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
    output_text = []
    output_coord = []

    for i, text in enumerate(infer_text):
        if text in number_list:
            number_count += 1

    for i, text in enumerate(infer_text):
        # Case 1. Remove Full Stop Char
        if text == ".":
            text = re.sub(r'.', '', text)

        # Case 2. Remove Number Pattern - e.g., 1., 1-
        text = re.sub(r'^[0-9]{1,2}[.-]', '', text)

        # Case 2-1. If Number Count More Than 5, Remove Number
        if number_count >= 5:
            text = re.sub(r'^[0-9]{1,2}', '', text)

        # Case 2-2. If box size of a number is too small, remove number
        if abs(float(coord[i][2][1]) - float(coord[i][0][1])) <= y_thres:
            text = re.sub(r'^[0-9]{1,2}', '', text)

        # Case 3. Remove Special Symbol
        text = re.sub(r'^[!?~/\@#$%^&*,.-_+=]*|[\/@#$%^&*_+=]*$', '', text)
        
        # Case 4. Remove Alphabet
        text = re.sub(r'^[a-zA-Z]*|[a-zA-Z]*$', '', text)
        
        # Case 5. Remove Front/End Space
        text = re.sub(r'^\s*|\s*$', '', text)

        # Case 6. Replace Last Hyphen to Full Stop
        result = text.replace("-", ".")

        if result != "":
            output_text.append(result)
            output_coord.append(first_coord[i])
    
    return output_text, output_coord


def infer_ocr(filepath): # `filepath` is S3 Path
    """ Inference OCR Using Image File Path """
    # Initialize EasyOCR Reader
    reader = easyocr.Reader(
        ['ko'], 
        model_storage_directory='ml/model',
        user_network_directory='ml/user_network',
        recog_network='custom',
        download_enabled=False,
    )

    # Inference OCR
    result = reader.readtext(filepath, width_ths=0.2)
    
    # Define Confidence Threshold
    conf_thres = 0.1
    
    coord = []
    first_coord = []
    infer_text = []
    infer_conf = []
    y_thres_list = []
    y_thres = 50
    for i, rst in enumerate(result):
        if rst[2] >= conf_thres: # If confidence more than threshold, append element to list
            tmp = []
            for j in rst[0]:
                tmp.append([j[0], j[1]])
            first_coord.append(tmp[0])
            coord.append(tmp)
            infer_text.append(rst[1])
            infer_conf.append(rst[2])
    
    # Calculate Y Threshold
    for i in coord:
        height = abs(float(i[0][1]) - float(i[2][1]))
        y_thres_list.append(height)
    y_thres = np.mean(y_thres_list)

    # Text Preprocessing
    infer_text, first_coord = text_preprocess(infer_text, first_coord, coord, y_thres)

    # Group Text by Coord
    grouped_texts = group_text_by_coord(infer_text, first_coord, y_thres)
    
    infer_proc_text = {}
    for i, group in enumerate(grouped_texts):
        tmp = " ".join(group)
        infer_proc_text[str(i + 1)] = tmp

    return {"results": infer_proc_text}