import pdfplumber
from typing import Iterator
from langchain_core.documents import Document
from tqdm import tqdm
from paddleocr import PaddleOCR
from pprint import pprint
import re
import os

### [Start] File Path 추출 Helper Functions ##############################
def has_subfolders(directory) -> bool:  # 대상 폴더 디렉토리에 하위폴더가 있는지 여부를 확인하는 함수
    try:
        items = os.listdir(directory)
        for item in items:
            if os.path.isdir(os.path.join(directory, item)):
                return True
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
### [End] File Path 추출 Helper Functions ##############################
    


### [Start] Parsing Helper Functions ##############################
def create_folder_if_not_exists(folder_path:str):  # 이미지 저장 폴더 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"폴더가 생성되었습니다: {folder_path}")
    else:
        print(f"폴더가 이미 존재합니다: {folder_path}")

def save_pdf_to_img(path:str, file_name:str, page_num:int):  # pdf를 png 이미지 파일로 저장
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_num]
        im = page.to_image(resolution=150)
        # im.draw_rects(first_page.extract_words())  # 글자에 Red Box 그리기
        save_path = f"{os.getcwd()}/images/{file_name}/{file_name}_{page_num}.png"
        im.save(save_path, format="PNG", )
    return save_path

def text_parser(path:str, page_num:int, crop:bool):   # 텍스트 파싱, A4상단 표준 크롭핑 적용 선택 가능
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_num]
        if crop:
            bounding_box = (3, 70, 590, 770)   #default : (0, 0, 595, 841)
            page = page.crop(bounding_box, relative=False, strict=True)
        else: pass
        result = page.extract_text(layout=False)
    return result

table_settings={      # extract_tables method variable
    "vertical_strategy": "lines", 
    "horizontal_strategy": "lines",
    "explicit_vertical_lines": [],
    "explicit_horizontal_lines": [],
    "snap_tolerance": 3,
    "snap_x_tolerance": 3,
    "snap_y_tolerance": 3,
    "join_tolerance": 3,
    "join_x_tolerance": 3,
    "join_y_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
    "intersection_tolerance": 3,
    "intersection_x_tolerance": 3,
    "intersection_y_tolerance": 3,
    "text_tolerance": 3,
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    # "text_*": …,
    }

def convert_header_to_separator(header: str) -> str:   # 테이블 첫줄 파싱후, 두번째 줄에 Header Line 추가 함수(마크다운 형식을 위한)
    # Use a regex to replace each header content with the appropriate number of hyphens
    separator = re.sub(r'[^|]+', lambda m: '-' * len(m.group(0)), header)
    return separator

def table_parser(pdf_path:str, page_num:int, crop:bool) -> list:   # 테이블 파싱(마크다운 형식), A4상단 표준 크롭핑 적용 선택 가능
    full_table = []
    with pdfplumber.open(pdf_path) as pdf:
        # Find the examined page
        table_page = pdf.pages[page_num]
        if crop:
            bounding_box = (3, 70, 590, 770)   #default : (0, 0, 595, 841)
            table_page = table_page.crop(bounding_box, relative=False, strict=True)
        else: pass
        tables = table_page.extract_tables(table_settings = table_settings)
        # if tables:
        for table in tables:
            table_string = ''
            # Iterate through each row of the table
            for row_num in range(len(table)):
                row = table[row_num]
                # Remove the line breaker from the wrapped texts
                cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
                # Convert the table into a string 
                table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
                if row_num ==0:  # 첫줄 작업이면, Header Line 추가
                    header_line = convert_header_to_separator(table_string[:-1])
                    table_string+= header_line+'\n'
            # Removing the last line break
            table_string = table_string[:-1]
            full_table.append(table_string)
        return full_table


# def get_table_bbox(path:str, page_num:int) -> list:
#     result = []
#     with pdfplumber.open(path) as pdf:
#         pages = pdf.pages
#         page = pages[page_num]
#         for table in page.find_tables():
#             bbox = table.bbox
#             result.append(bbox)
#     return result

def extract_level_name(path:str) -> list:  # 폴더 구조(lv1, lv2, lv3를 metadata로 추출하는 함수)
    temp = path.split("\\")  # path 예시 : ['.\\2024\\Manual\\Guidance for Autonomous Ships_2023.pdf','.\\2024\\POS\\FWG.pdf']
    lv1 = temp[1]
    if temp[2]:
        if temp[2] != temp[-1]:
            lv2 = temp[2]
            lv3 = temp[-1].replace(".pdf", "")
        else:
            lv2 = None
            lv3 = temp[-1].replace(".pdf", "")
    result = [lv1, lv2, lv3]
    return result


### [End] Parsing Helper Functions ##############################

### [Start] Main Fucntions ###########################################################################################
total_results =[]
def main_filepath_extractor(path:str) -> list:   # 폴더 트리를 리커시브하게 읽어서 전체 PDF 파일의 full 경로를 리스트에 수집 
    global total_results
    
    all_items = os.listdir(path)
    files = [f for f in all_items if os.path.isfile(os.path.join(path, f))]
    results = [os.path.join(path, file) for file in files]
    total_results.extend(results)

    dirs = [f for f in all_items if os.path.isdir(os.path.join(path, f))]
    if dirs:
        dirs = [path+"\\" + lv2_dir for lv2_dir in dirs]
        for dir in dirs:
            main_filepath_extractor(dir)
    return total_results

def main_parser(path:str, crop:bool) -> Iterator[Document]:  # 메인 Parsing 함수
    full_result = []
    file_name = path.split("\\")[-1].split(".")[0].strip() 
    img_save_folder = os.path.join(os.getcwd(), f"images/{file_name}")  # images 폴더 생성후 그 안에 file_name폴더 생성
    create_folder_if_not_exists(img_save_folder)
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    with pdfplumber.open(path) as pdf:
        page_number = 0  # for metadata
        for _ in tqdm(pdf.pages):

            level_names = extract_level_name(path)  # for metadata
            img_path = save_pdf_to_img(path, file_name, page_number) # for saving pdf page as png img file
            text_result = text_parser(path, page_number, crop)  # for page_content
            fixed_first_line = f"This page explains {level_names[2]}"  # for page_content
            if len(text_result) == 0:  # 텍스트 추출 결과가 없으면, OCR 실시
                print("이미지 OCR")
                ocr_result = ocr.ocr(img_path)
                for idx in range(len(ocr_result)):
                    res = ocr_result[idx]
                    temp_result = []
                    for line in res:
                        temp_result.append(line[1][0])
                text_result = " ".join(temp_result)

            table_result = table_parser(path, page_number, crop)  # for page_content

            if table_result:
                total_page_result = ""
                for table in table_result:
                    total_page_result = fixed_first_line + "\n\n" + text_result + "\n\n" + table   # table_result가 있으면, text_result 끝에 엔터후 이어붙이기
                    result = Document(
                        page_content=total_page_result,
                        metadata={"page_number": page_number, "lv1":level_names[0], "lv2": level_names[1], "lv3": level_names[2], "source": path},
                        )
            else:
                result = Document(
                    page_content = fixed_first_line + "\n\n" + text_result,
                    metadata={"page_number": page_number, "lv1":level_names[0], "lv2": level_names[1], "lv3": level_names[2], "source": path},
                    )
            full_result.append(result)
            page_number += 1
        parsed_document = full_result
    return parsed_document   # langchain Document type

### [End] Main Fucntions ###########################################################################################

if __name__ == "__main__":

    lv1_dir = ".\\2024"     # 최상단 엄마 폴더
    total_results = main_filepath_extractor(path=lv1_dir)  # 모든 PDF의 Full Path를 리스트에 담기
    print(total_results)
    print()

    path = total_results[2]
    try:
        result = main_parser(path=path, crop=True)
    except:
        result = main_parser(path=path, crop=False)  # 크롭핑 여백의 차이가 있어서 에러 발생시
    print(type(result))
    pprint(len(result))
    pprint(result)