import numpy as np
import cv2
import matplotlib.pyplot as plt

##################################################################################
# polynomial function
################################################################################## 
def polynomialFit(x, y):
    # calculate polynomial
    z = np.polyfit(x, y, 3) # 3 degree polynomial fit
    f = np.poly1d(z) # create a function

    # calculate new x's and y's
    x_new = np.arange(256)
    y_new = np.clip(f(x_new),0,255)
    return y_new

##################################################################################
# main
################################################################################## 
# output color (based on wiki)
outpt = [[115, 82, 68], [194, 150, 130], [98, 122, 157], [87, 108, 67], [133, 128, 177], [103, 189, 170],
        [214, 126, 44], [80, 91, 166], [193, 90, 99], [94, 60, 108], [157, 188, 64], [224, 163, 46],
        [56, 61, 150], [70, 148, 73], [175, 54, 60], [231, 199, 31], [187, 86, 149], [8, 133, 161],
        [243, 243, 242], [200, 200, 200], [160, 160, 160], [122, 122, 122], [85, 85, 85], [52, 52, 52]]

# input color (based on your image)
# 3200k
inpt = [[42, 42, 16], [, 132, 45], [83, 105, 49], [77, 94, 30], [105, 109, 55], [110, 153, 63],
        [131, 116, 28], [66, 85, 47], [129, 102, 32], [68, 69, 30], [124, 153, 43], [157, 152, 37],
        [45, 58, 36], [72, 104, 34], [112, 84, 23], [160, 167, 42], [127, 105, 43], [68, 106, 54],
        [154, 174, 68], [131, 150, 59], [111, 128, 50], [89, 102, 39], [69, 79, 29], [47, 53, 18]]

outpt = np.array(outpt)
inpt = np.array(inpt)

import csv

with open('ccm_3200k.csv', 'w') as f:
    
    # Create a CSV writer object that will write to the file 'f'
    csv_writer = csv.writer(f)
    
    # Write all of the rows of data to the CSV file
    csv_writer.writerows(inpt/255)

with open('ccm_ref_srgb.csv', 'w') as f:
    
    # Create a CSV writer object that will write to the file 'f'
    csv_writer = csv.writer(f)
    
    # Write all of the rows of data to the CSV file
    csv_writer.writerows(outpt/255)

quit

""" # calculate polynomial fitting
lineR = polynomialFit(inpt[:,0], outpt[:,0])
lineG = polynomialFit(inpt[:,1], outpt[:,1])
lineB = polynomialFit(inpt[:,2], outpt[:,2])

# plot input output RGB lines
line = np.arange(256)
plt.plot(line, lineR, label = "Red", color='red')
plt.plot(line, lineG, label = "Green", color='green')
plt.plot(line, lineB, label = "Blue", color='blue')
plt.legend()
plt.show()

# look up table from polyline
lutR = np.uint8(lineR)
lutG = np.uint8(lineG)
lutB = np.uint8(lineB)

# read image
img = cv2.imread('test_3200k.tif')
img = cv2.resize(img, (600, 400), interpolation = cv2.INTER_AREA)

# generate output image using look up table
res = img.copy()
res[:,:,0] = lutB[img[:,:,0]]
res[:,:,1] = lutG[img[:,:,1]]
res[:,:,2] = lutR[img[:,:,2]]

# show result
cv2.imshow('img', img)
cv2.imshow('res', res)
cv2.waitKey(0) """