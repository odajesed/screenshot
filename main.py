import tkinter as tk
import pytesseract
from pytesseract import Output
from PIL import Image, ImageTk, ImageGrab, ImageEnhance
import pyperclip
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
custom_config = r'-c preserve_interword_spaces=1 --oem 1 --psm 1 -l eng+ita'
texto = ''

d = pytesseract.image_to_data(Image.open(r'savedimage.jpg'), config=custom_config, output_type=Output.DICT)
df = pd.DataFrame(d)

root = tk.Tk()
root.resizable(0, 0)
def saveit():
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
def show_image(image):
    win = tk.Toplevel()
    win.image = ImageTk.PhotoImage(image)
    tk.Label(win, image=win.image).pack()
    win.grab_set()
    win.wait_window(win)
    image = image.save('savedimage.jpg')
    saveit()


def area_sel():
    x1 = y1 = x2 = y2 = 0
    roi_image = None

    def on_mouse_down(event):
        nonlocal x1, y1
        x1, y1 = event.x, event.y
        canvas.create_rectangle(x1, y1, x1, y1, outline='red', tag='roi')

    def on_mouse_move(event):
        nonlocal roi_image, x2, y2
        x2, y2 = event.x, event.y
        canvas.delete('roi-image')
        roi_image = image.crop((x1, y1, x2, y2))
        canvas.image = ImageTk.PhotoImage(roi_image)
        canvas.create_image(x1, y1, image=canvas.image, tag=('roi-image'), anchor='nw')
        canvas.coords('roi', x1, y1, x2, y2)
    
        canvas.lift('roi') 

    root.withdraw() 
    image = ImageGrab.grab()  
    bgimage = ImageEnhance.Brightness(image).enhance(0.3)  
    
    win = tk.Toplevel()
    win.attributes('-fullscreen', 1)
    win.attributes('-topmost', 1)
    canvas = tk.Canvas(win, highlightthickness=0)
    canvas.pack(fill='both', expand=1)
    tkimage = ImageTk.PhotoImage(bgimage)
    canvas.create_image(0, 0, image=tkimage, anchor='nw', tag='images')
    
    win.bind('<ButtonPress-1>', on_mouse_down)
    win.bind('<B1-Motion>', on_mouse_move)
    win.bind('<ButtonRelease-1>', lambda e: win.destroy())
    
    win.bind('<Escape>', lambda e: win.destroy())
    
    win.focus_force()
    win.grab_set()
    win.wait_window(win)
    root.deiconify()
    
    
    if roi_image:
        show_image(roi_image)

tk.Button(root, text='select area', width=30, command=area_sel).pack()

root.mainloop()