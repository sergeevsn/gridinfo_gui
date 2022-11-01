import re
import PySimpleGUI as sg
import time
import os

from services import *

def open_results_window(**kwargs):
    data1 = [['1.', kwargs.get('inl1'), kwargs.get('xln1'), f"{kwargs.get('x1'):.2f}", f"{kwargs.get('y1'):.2f}"],
            ['2.', kwargs.get('inl2'), kwargs.get('xln2'), f"{kwargs.get('x2'):.2f}", f"{kwargs.get('y2'):.2f}"],
            ['3.', kwargs.get('inl3'), kwargs.get('xln3'), f"{kwargs.get('x3'):.2f}", f"{kwargs.get('y3'):.2f}"],
    ] 
    headings1 = ['№', 'INLINE', 'XLINE', 'X', 'Y']
    data2 = [['X0', f"{kwargs.get('x0'):.2f}"],
             ['Y0', f"{kwargs.get('y0'):.2f}"],
             ['step', f"{kwargs.get('step'):.2f}"],
             ['alpha', f"{kwargs.get('alpha'):.2f}"],
             ['INL Y',  kwargs.get('inly')]
            ]
    headings2 = ['Параметр', 'Значение']        
    layout = [
              [sg.Text(f"{kwargs['filename']} прочитан за {kwargs['dur']:.1f} сек.")],
              [sg.Text("Три угловые точки", key="new")],
              [sg.Table(values=data1, headings=headings1, max_col_width=35, hide_vertical_scroll=True, auto_size_columns=True, num_rows=6,  row_height=15, key='-TABLE1-')],
              [sg.Text("Параметры грида", key="new")],
              [sg.Table(values=data2, headings=headings2, auto_size_columns=True,  hide_vertical_scroll=True, num_rows=6, row_height=15, key='-TABLE2-')],
              [sg.Button('OK', key='-OK-')]
             ]
    window = sg.Window("Gridinfo: Результаты", layout, modal=True)

    choice = None
    while True:
        event, values = window.read()
        if event == "-OK-" or event == sg.WIN_CLOSED:
            break
        
    window.close()


# Define the window's contents
layout = [ [sg.Text("Выберите SEG-Y файл")],
           [sg.Input(key='-SEGY FILE-', size=(40,20)), sg.FileBrowse('Выбрать', key='-CHOOSE-', file_types = (('SEG-Y файлы', '*.sgy'),('Все файлы', '*.*')), target='-SEGY FILE-')],
           [sg.Button('Открыть', key='-OPEN-'), sg.Button('Выход', key='-QUIT-')],
           [sg.ProgressBar(100, orientation='h', visible=False, size=(22,20), key='-PROG-')] 

         ]   

# Create the window
window = sg.Window('GridInfo: Выбор файла', layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == '-QUIT-':
        break
    if event == '-OPEN-':
        
        if os.path.isfile(values['-SEGY FILE-']):       
           
            window['-CHOOSE-'].update(disabled=True)
            window['-OPEN-'].update(disabled=True)
            window['-QUIT-'].update(disabled=True)
            window['-PROG-'].update(visible=True)
            start1 = time.time()
            read_ok, inlines, xlines, x, y = read_segy(values['-SEGY FILE-'], window)
            end1 = time.time()
            start2 = end1
            regr = get_regression(inlines, xlines, x, y)
            end2 = time.time()
            if not read_ok:
                sg.PopupError('Wrong file')
                break
            #sg.Popup(f'TIME READING: {(end1 - start1):.2f} sec, TIME CALC: {(end2 - start2):.2f} sec')
            inl1 = inl2 = min(inlines)
            xln1 = min(xlines)
            inl3 = max(inlines)
            xln2 = xln3 = max(xlines)
            x1, y1 = get_linear_from_ab(inl1, xln1, regr['x_coefs'], regr['y_coefs'])
            x2, y2 = get_linear_from_ab(inl2, xln2, regr['x_coefs'], regr['y_coefs'])
            x3, y3 = get_linear_from_ab(inl3, xln3, regr['x_coefs'], regr['y_coefs'])
            window['-CHOOSE-'].update(disabled=False)
            window['-OPEN-'].update(disabled=False)
            window['-QUIT-'].update(disabled=False)
            window['-PROG-'].update(visible=False)
            open_results_window(filename=values['-SEGY FILE-'], inl1=inl1, xln1=xln1, x1=x1, y1=y1, 
                        inl2=inl2, xln2=xln2, x2=x2, y2=y2,
                        inl3=inl3, xln3=xln3, x3=x3, y3=y3,
                        x0=regr['X0'], y0=regr['Y0'], alpha=regr['alpha'], step=regr['step'], inly=regr['inline_along_y'], dur=end2-start1)
            

# Finish up by removing from the screen
window.close()
