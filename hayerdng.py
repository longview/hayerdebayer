from pidng.core import RAW2DNG, DNGTags, Tag
from pidng.defs import *
import numpy as np
import struct
import cv2
from xml.dom import minidom

# image specs
width = 3840
height = 2160
bpp= 16

'''import xml.etree.ElementTree as ET
tree_w = ET.parse('HY-6110_3200k.xmp')
root_w = tree_w.getroot()
tree_d = ET.parse('HY-6110_6500k.xmp')
root_d = tree_d.getroot()

ccm_3200k = [[int(float(root_w[3][8].text)*10000), 10000], [int(float(root_w[3][7].text)*10000), 10000], [int(float(root_w[3][6].text)*10000), 10000],	
        [int(float(root_w[3][5].text)*10000), 10000], [int(float(root_w[3][4].text)*10000), 10000], [int(float(root_w[3][3].text)*10000), 10000],
        [int(float(root_w[3][2].text)*10000), 10000], [ int(float(root_w[3][1].text)*10000), 10000], [ int(float(root_w[3][0].text)*10000), 10000]]
ccm_6500k = [[int(float(root_d[3][8].text)*10000), 10000], [int(float(root_d[3][7].text)*10000), 10000], [int(float(root_d[3][6].text)*10000), 10000],	
        [int(float(root_d[3][5].text)*10000), 10000], [int(float(root_d[3][4].text)*10000), 10000], [int(float(root_d[3][3].text)*10000), 10000],
        [int(float(root_d[3][2].text)*10000), 10000], [ int(float(root_d[3][1].text)*10000), 10000], [ int(float(root_d[3][0].text)*10000), 10000]]
print(ccm_3200k)
print(ccm_6500k)'''

ccm_6500k = [[15445, 10000], [-4930, 10000], [-1174, 10000], [191, 10000], [8682, 10000], [1374, 10000], [-653, 10000], [1245, 10000], [5655, 10000]]
ccm_3200k = [[15445, 10000], [-4930, 10000], [-1174, 10000], [191, 10000], [8682, 10000], [1374, 10000], [-653, 10000], [1245, 10000], [5655, 10000]]

camera_calibration = [[135, 100], [0, 10], [0, 10],
                              [0, 10], [229, 100], [0, 10],
                              [0, 10], [0, 10], [191, 100]]
# these are lifted elsewhere, should really be calculated
fm1 = [[7889, 10000], [1273, 10000], [482, 10000],
        [2401, 10000], [9705, 10000], [-2106, 10000],
        [-26, 10000], [-4406, 10000], [12683, 10000]]

fm2 = [[6591, 10000], [3034, 10000], [18, 10000],
        [1991, 10000], [10585, 10000], [-2575, 10000],
        [-493, 10000], [-919, 10000], [9663, 10000]]

import glob, os
for file in glob.glob("*.RAW"):
    newfile = os.path.splitext(file)[0] + '.dng'
    print('Processing file ' + file + ' to ' + newfile)
    # load raw data into 16-bit numpy array.
    numPixels = width*height
    rawFile = file
    rf = open(rawFile, mode='rb')
    data = np.fromfile(rf, np.uint8, width * height * 3//2)

    data = data.astype(np.uint16)  # Cast the data to uint16 type.
    result = np.zeros(data.size*2//3, np.uint16)  # Initialize matrix for storing the pixels.

    # 12 bits packing: ######## ######## ########
    #                  | 8bits| | 4 | 4  |  8   |
    #                  |  lsb | |msb|lsb |  msb |
    #                  <-----------><----------->
    #                     12 bits       12 bits
    result[0::2] = ((data[1::3] &  15) << 8) | data[0::3]
    result[1::2] = (data[1::3] >> 4) | (data[2::3] << 4)
    rawImage = np.reshape(result, (height, width))
    
    rawImage = cv2.rotate(rawImage, cv2.ROTATE_180)
    #rawImage = rawImage.astype(np.float32)/4096
    rawImage = rawImage * 16
    #rawImage = rawImage >> (16 - bpp)
    # set DNG tags.
    t = DNGTags()
    t.set(Tag.ImageWidth, width)
    t.set(Tag.ImageLength, height)
    #t.set(Tag.TileWidth, width)
    #t.set(Tag.TileLength, height)
    t.set(Tag.RowsPerStrip, height)
    t.set(Tag.Orientation, Orientation.Horizontal)
    t.set(Tag.PhotometricInterpretation, PhotometricInterpretation.Color_Filter_Array)
    t.set(Tag.SampleFormat, SampleFormat.Uint)
    t.set(Tag.SamplesPerPixel, 1)
    t.set(Tag.BitsPerSample, bpp)
    t.set(Tag.CFARepeatPatternDim, [2,2])
    t.set(Tag.CFAPattern, CFAPattern.BGGR)
    t.set(Tag.BlackLevel, 0)
    t.set(Tag.WhiteLevel, ((1 << bpp) -1) )
    t.set(Tag.ColorMatrix1, ccm_3200k)
    t.set(Tag.ColorMatrix1, ccm_6500k)
    #t.set(Tag.ForwardMatrix1, fm1)
    #t.set(Tag.ForwardMatrix2, fm2)
    t.set(Tag.CameraCalibration1, camera_calibration)
    t.set(Tag.CameraCalibration2, camera_calibration)
    t.set(Tag.CalibrationIlluminant1, CalibrationIlluminant.Tungsten_Incandescent)
    t.set(Tag.CalibrationIlluminant2, CalibrationIlluminant.D65)
    t.set(Tag.AsShotNeutral, camera_calibration)
    t.set(Tag.BaselineExposure, [[-150,100]])
    t.set(Tag.Make, "HY-6110")
    t.set(Tag.Model, "Hayear")
    t.set(Tag.DNGVersion, DNGVersion.V1_4)
    t.set(Tag.DNGBackwardVersion, DNGVersion.V1_2)
    t.set(Tag.PreviewColorSpace, PreviewColorSpace.sRGB)
    t.set(Tag.PhotographicSensitivity, [100]) 
    t.set(Tag.ExposureTime, [[1,30]])  
    profile_name = "PiDNG / HY-6110 Profile"
    profile_embed = 3
    t.set(Tag.ProfileName, profile_name)
    t.set(Tag.ProfileEmbedPolicy, [profile_embed])
    t.set(Tag.NewSubfileType, 0)
    t.set(Tag.UniqueCameraModel, "HY-6110")

    # save to dng file.
    r = RAW2DNG()
    r.options(t, path="", compress=False)
    r.convert(rawImage, filename=newfile)