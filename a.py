import pytesseract
from pytesseract import Output
from PIL import Image
import pyperclip
import pandas as pd
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
custom_config = r'-c preserve_interword_spaces=1 --oem 1 --psm 1 -l eng+ita'
texto = ''

d = pytesseract.image_to_data(Image.open(r'savedimage.jpg'), config=custom_config, output_type=Output.DICT)
df = pd.DataFrame(d)

df1 = df[(df.conf!='-1')&(df.text!=' ')&(df.text!='')]
sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
for block in sorted_blocks:
    curr = df1[df1['block_num']==block]
    sel = curr[curr.text.str.len()>3]
    char_w = (sel.width/sel.text.str.len()).mean()
    prev_par, prev_line, prev_left = 0, 0, 0
    text = ''
    for ix, ln in curr.iterrows():
        if prev_par != ln['par_num']:
            text += '\n'
            prev_par = ln['par_num']
            prev_line = ln['line_num']
            prev_left = 0
        elif prev_line != ln['line_num']:
            text += '\n'
            prev_line = ln['line_num']
            prev_left = 0

        added = 0  
        if ln['left']/char_w > prev_left + 1:
            added = int((ln['left'])/char_w) - prev_left
            text += ' ' * added 
        text += ln['text'] + ' '
        prev_left += len(ln['text']) + added + 1
    text += '\n'
    texto += text
pyperclip.copy(texto)
spam = pyperclip.paste()