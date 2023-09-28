from pidng.core import RAW2DNG, DNGTags, Tag
from pidng.defs import *
import numpy as np
import struct
import cv2

# image specs
width = 3840
height = 2160
bpp= 16



# uncalibrated color matrix, just for demo. 
ccm1 = [[22100, 10000], [-8907, 10000], [-2920, 10000],	
        [-6472, 10000], [11444, 10000], [2168, 10000],
        [-1433, 10000], [ -124, 10000], [ 7487, 10000]]
ccm2 = [[15445, 10000], [-4930, 10000], [-1174, 10000],	
        [192, 10000], [8682, 10000], [1374, 10000],
        [-653, 10000], [ 124, 10000], [ 5655, 10000]]
camera_calibration = [[1, 1], [0, 1], [0, 1],
                              [0, 1], [1, 1], [0, 1],
                              [0, 1], [0, 1], [1, 1]]
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
    t.set(Tag.ColorMatrix1, ccm1)
    t.set(Tag.ColorMatrix1, ccm2)
    t.set(Tag.ForwardMatrix1, fm1)
    t.set(Tag.ForwardMatrix2, fm2)
    t.set(Tag.CameraCalibration1, camera_calibration)
    t.set(Tag.CameraCalibration2, camera_calibration)
    t.set(Tag.CalibrationIlluminant1, CalibrationIlluminant.Warm_White_Fluorescent)
    t.set(Tag.CalibrationIlluminant2, CalibrationIlluminant.D65)
    t.set(Tag.AsShotNeutral, [[1,1],[1,1],[1,1]])
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