import sys
import io
from PIL import Image
import binascii as bia
import zlib
import numpy as np
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTContainer, LTTextBox
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams, LTImage, LTFigure
from pdfminer.pdfdocument import PDFDocument

def find_textboxes_recursively(layout_obj):
    """
    再帰的にテキストボックス（LTTextBox）を探して、テキストボックスのリストを取得する。
    """
    # LTTextBoxを継承するオブジェクトの場合は1要素のリストを返す。
    if isinstance(layout_obj, LTTextBox):
        return [layout_obj]

    # LTContainerを継承するオブジェクトは子要素を含むので、再帰的に探す。
    if isinstance(layout_obj, LTContainer):
        boxes = []
        for child in layout_obj:
            boxes.extend(find_textboxes_recursively(child))

        return boxes

    return []  # その他の場合は空リストを返す。

def print_and_write(txt):
    print(txt)
    #box_replace = box.encode('cp932',"ignore")
            #box_alta = box_replace.decode('cp932')
    output_txt.write((txt.encode('cp932',"ignore").decode('cp932')))
    output_txt.write('\n')

def determine_image_type(stream_first_4_bytes):
    file_type = None
    is_img = False
    bytes_as_hex = bia.b2a_hex(stream_first_4_bytes)
    if bytes_as_hex.startswith(b"ffd8"):
        file_type = ".jpg"
        is_img = True
    elif bytes_as_hex == "89504e47":
        file_type = ".png"
        is_img = True
    elif bytes_as_hex == "47494638":
        file_type = ".gif"
        is_img = True
    elif bytes_as_hex.startswith(b"424d"):
        file_type = ".bmp"
        is_img = True
    elif bytes_as_hex.startswith(b"002a"):
        file_type = ".tiff"
        is_img = True
    elif bytes_as_hex.startswith(b"789c"):
        file_type = "789c"
    elif bytes_as_hex.startswith(b"78da"):
        file_type = "78da"
    return file_type, is_img

with open(sys.argv[1], 'rb') as f:
    # Layout Analysisのパラメーターを設定。縦書きの検出を有効にする。
    laparams = LAParams(detect_vertical=True)

    document = PDFDocument(PDFParser(f))

    # 共有のリソースを管理するリソースマネージャーを作成。
    resource_manager = PDFResourceManager()

    # ページを集めるPageAggregatorオブジェクトを作成。
    device = PDFPageAggregator(resource_manager, laparams=laparams)

    # Interpreterオブジェクトを作成。
    interpreter = PDFPageInterpreter(resource_manager, device)

    # 出力用のテキストファイル
    output_txt = open('output2.txt', 'w')

    print(sys.argv[1])
    print('Press Enter >>',end='')

    # PDFPage.get_pages()にファイルオブジェクトを指定して、PDFPageオブジェクトを順に取得する。
    # 時間がかかるファイルは、キーワード引数pagenosで処理するページ番号（0始まり）のリストを指定するとよい。
    for page in PDFPage.get_pages(f):
        print_and_write('\n====== ページ区切り ======\n')
        interpreter.process_page(page)  # ページを処理する。
        layout = device.get_result()  # LTPageオブジェクトを取得。

        # ページ内のテキストボックスのリストを取得する。
        boxes = find_textboxes_recursively(layout)

        #figs = [obj for obj in layout if isinstance(obj, LTFigure)][0]
        #ltimg = [obj for obj in figs if isinstance(obj, LTImage)][0]
        #画像のheight, widthを取得
        #width, height = ltimg.srcsize
        #rawデータを取得
        #img_stream = ltimg.stream.get_rawdata()

        ##   !!!! ここのせいでboxesの順が論文の読み順になってない

        # テキストボックスの左上の座標の順でテキストボックスをソートする。
        # y1（Y座標の値）は上に行くほど大きくなるので、正負を反転させている。
        #boxes.sort(key=lambda b: (-b.y1, b.x0))

        for box in boxes:
            print_and_write('-' * 10)  # 読みやすいよう区切り線を表示する。
            print_and_write((box.get_text().strip()).replace('\n',''))  # テキストボックス内のテキストを表示する。



print(str(sys.argv[1])+" // Convert Successful.")
output_txt.close()