#!/usr/bin/env python
import sys
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
import time

import PIL
from PIL import Image, ImageDraw, ImageFont

import io

global gauge_in
gauge_in = Image.open('/Users/stevenhoglund/pyenv/pysimple_test/gauge_psi.gif').convert('RGBA')
global gauge_B_in
gauge_B_in = Image.open('/Users/stevenhoglund/pyenv/pysimple_test/gauge_bar.gif').convert('RGBA')
global needle_in
needle_in = Image.open('/Users/stevenhoglund/pyenv/pysimple_test/needle.gif').convert('RGBA')

class Dial_screen():    # Loco operation screen
   def __init__(self):
       
    global imgbytes
    imgbytes=''
    global imgbytes_B
    imgbytes_B=''

    global bigfont
    bigfont=str('Helvetica 17 bold')
    
    global PSI
    PSI = 0
    global BAR
    BAR = PSI / 14.504
    
    PG_image_H = 300                        # pressure gauge image height
    PG_image_W = PG_image_H                 # pressure gauge image width
    PG_needle_Y = 150                       # pressure gauge needle pivot height - currently mid vertical point on needle gif
    PG_needle_X = PG_image_W/2              # pressure gauge needle pivot width

    global pivot
    pivot = (PG_needle_Y, PG_needle_X)
    
    imgbytes=dial_setup()
    imgbytes_B=dial_setup_B()

    layout = [
        [sg.Text('Dial demo', size=(30, 1), justification='center', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
        [sg.Text('\nPSI gauge demo         '),
        sg.Image(filename='',data=imgbytes,key='_dialP_', size = (PG_image_H, PG_image_W))],
        [sg.Text('\nBAR gauge demo         '),
        sg.Image(filename='',data=imgbytes,key='_dialB_', size = (PG_image_H, PG_image_W))],
        [sg.Text('\nPSI control     '), sg.Slider(range=(1, 75), resolution = 5, orientation='h', size=(30, 20), default_value=0, key='_SLIDER_PSI_', change_submits=True)],
        [sg.Text('\nAuto run control\n milliseconds'), sg.Slider(range=(1, 1000), resolution = 100, orientation='h', size=(30, 20), default_value=0, key='_SLIDER_time_', change_submits=True)],
        [sg.Text('')],
        [sg.Button('AUTO RUN', key='_AR_'), sg.Text(' ' * 10), sg.Button('FINISH')],
        ]

    window = sg.Window('Dial demo' , font=bigfont, background_color='white', disable_close=True, default_button_element_size=(12, 1),auto_size_buttons=False).Layout(layout)
#   Note -   ,disable_close=True prevents the user from using the top corner X button

    while True:
        event, values = window.Read()
#        print(event, values)
            
        if event == '_SLIDER_PSI_':
            PSI = values['_SLIDER_PSI_']
            BAR = PSI / 14.504
            imgbytes=dial_setup()
            imgbytes_B=dial_setup_B()
#            print ('attempting to update screen - PSI only')
            window.FindElement('_dialP_').Update(data=imgbytes)
#            print ('attempting to update screen - BAR only')
            window.FindElement('_dialB_').Update(data=imgbytes_B)
            continue
        
        if event == '_SLIDER_time_':
            secs= values['_SLIDER_time_'] / 1000

        if event == '_AR_':
            PSI = 0
            while PSI < 80:
                time.sleep(secs)
                PSI += 1
                BAR = PSI / 14.504
#                print ('delay = : ', secs, ' PSI = :', PSI)
                imgbytes=dial_setup()
                imgbytes_B=dial_setup_B()
                window.FindElement('_dialP_').Update(data=imgbytes)
                window.FindElement('_dialB_').Update(data=imgbytes_B)
                window.Refresh()         
        
        if event == 'FINISH':
            break
    
    window.Close()
    
def dial_setup():
    
    bio_out=io.BytesIO()
# Revised code - not updating screen - output file changes, but not screen

    rotation = (PSI - 40) * -1
    needle2 = needle_in.rotate(rotation, resample=PIL.Image.BICUBIC, center=pivot)  # Rotate needle, pivot is centre point of needle gif
    gauge=gauge_in.copy()   # create true copy, NOT a link!
    gauge.paste(needle2,box =(0, 63), mask=needle2)  # Paste needle onto gauge
# the needle pivot defaults to the centre of the dial: box moves it 0 pixels right, 63 pixels down to where the actual pivot is
# the needle gif needs to be the same dimensions as the dial, with the actual pivot at the centre of the gif
# you will need to calculate the vertical offset from your original drawing files
# the gifs are transparent outside the area of the actual graphic
    if PSI > 60:
        text_color = 'red'
    else:
        text_color = 'black'
    fnt=ImageFont.truetype(font='FreeMono.ttf', size=48)     # in CURRENT folder - download if missing
    img_draw=ImageDraw.Draw(gauge)
    img_draw.text((60,185),str(int(PSI)), text_color, font=fnt)  # Coordinates, Text, Color
    img_draw.text((60,187),str(int(PSI)), text_color, font=fnt)  # Faking bold font
    img_draw.text((62,185),str(int(PSI)), text_color, font=fnt)  # Faking bold font
    gauge.save(bio_out, format="PNG")                            # PIL writes to memory, image format PNG
#    gauge.save('new_gauge.png')     # NOT part of final code - just here so I can monitor the change in Windows Explorer preview pane
    imgbytes = bio_out.getvalue()
#    open('bio_gauge.png', 'wb').write(imgbytes)
    return imgbytes

def dial_setup_B():
    
    bio_out=io.BytesIO()
# Old code - not updating screen - output file changes, but not screen

    rotation = (PSI - 40) * -1
    needle2 = needle_in.rotate(rotation, resample=PIL.Image.BICUBIC, center=pivot)  # Rotate needle, pivot is centre point of needle gif
    gauge_B=gauge_B_in.copy()   # create true copy, NOT a link!
    gauge_B.paste(needle2,box =(0, 63), mask=needle2)  # Paste needle onto gauge
# the needle pivot defaults to the centre of the dial: box moves it 0 pixels right, 63 pixels down to where the actual pivot is
# the needle gif needs to be the same dimensions as the dial, with the actual pivot at the centre of the gif
# you will need to calculate the vertical offset from your original drawing files
# the gifs are transparent outside the area of the actual graphic
    if PSI > 60:
        text_color = 'red'
    else:
        text_color = 'black'
    fnt=ImageFont.truetype(font='FreeMono.ttf', size=48)     # in CURRENT folder - download if missing
    img_draw=ImageDraw.Draw(gauge_B)
    img_draw.text((40,187),str('{0:3.1f}'.format(BAR)),text_color, font=fnt)       # Coordinates, Text, Color
    img_draw.text((40,189),str('{0:3.1f}'.format(BAR)),text_color, font=fnt)       # Faking bold font
    img_draw.text((42,187),str('{0:3.1f}'.format(BAR)),text_color, font=fnt)       # Faking bold font
    gauge_B.save(bio_out, format="PNG")                            # PIL writes to memory, image format PNG
#    gauge_B.save('new_gauge_B.png')     # NOT part of final code - just here so I can monitor the change in Windows Explorer preview pane
    imgbytes_B = bio_out.getvalue()
#    open('bio_gauge_B.png', 'wb').write(imgbytes_B)
    return imgbytes_B

if __name__ == '__main__':
    Dial_screen()
