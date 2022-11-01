import segyio as sgy
import numpy as np
import math


def read_segy(filename, window):
    read_ok = True
    
    try:
        with sgy.open(filename, ignore_geometry=True) as segyfile:
            segyfile.mmap()
            window['-PROG-'].update(current_count=0, max=segyfile.tracecount//100)
            inlines = []
            xlines = []
            x = []
            y = []
            for i in range(segyfile.tracecount):
                header = segyfile.header[i]

                inlines.append(header[sgy.TraceField.INLINE_3D])
                xlines.append(header[sgy.TraceField.CROSSLINE_3D])
                x.append(header[sgy.TraceField.CDP_X])
                y.append(header[sgy.TraceField.CDP_Y])
                if i%100 == 0:
                    window['-PROG-'].update(i//100+1)
            
    except (UnboundLocalError, RuntimeError):
        read_ok = False
        return read_ok, None, None, None, None    
   
    return read_ok, inlines, xlines, x, y


def get_regression(inlines, xlines, x, y):
    X = np.vstack([inlines, xlines]).T
    X = np.c_[X, np.ones(X.shape[0])]
    linregX = np.linalg.lstsq(X, np.array(x), rcond=None)[0]
    linregY = np.linalg.lstsq(X, np.array(y), rcond=None)[0]

    X = np.vstack([x, y]).T
    X = np.c_[X, np.ones(X.shape[0])]
    linregInl = np.linalg.lstsq(X, np.array(inlines), rcond=None)[0]
    linregXln = np.linalg.lstsq(X, np.array(xlines), rcond=None)[0]

    step = np.sqrt(linregX[0]**2 + linregX[1]**2)
    inline_along_y = math.copysign(1.0, linregX[0]*linregY[1]) == -1
    
    # вариант через тангенс даёт верный результат в 1 и 4 четвертях. Вариант через косинус - в 1 и 2
    # учитывая, что 1 и 4 наиболее частый вариант, то оставляю тангенс
    if inline_along_y:
     
        alpha = np.degrees(np.arctan(linregX[0]/linregX[1]))
    else:
       
        alpha = np.degrees(np.arctan(linregX[1]/linregX[0]))       
    

    return { 
            'x_coefs': linregX.tolist(), 
            'y_coefs': linregY.tolist(),            
            'inline_coefs': linregInl.tolist(),
            'xline_coefs': linregXln.tolist(),
            'X0': linregX[0] + linregX[1] + linregX[2],
            'Y0': linregY[0] + linregY[1] + linregY[2],
            'step': step,
            'inline_along_y': inline_along_y,
            'alpha': alpha,        
           }
    
def get_linear_from_ab(a, b, coefs1, coefs2):
    c = coefs1[0]*a + coefs1[1]*b + coefs1[2]
    d = coefs2[0]*a + coefs2[1]*b + coefs2[2]
    return c, d
    