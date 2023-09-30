from pidng.core import RAW2DNG, DNGTags, Tag
from pidng.defs import *
import numpy as np
import struct
import cv2
import json
import os

absolute_path = os.path.dirname(__file__)

# image specs
width = 3840
height = 2160
bpp= 16

with open(os.path.join(absolute_path, 'calibration/ccm_warm.json'), 'r') as filehandle:
    ccm_3000k = json.load(filehandle)
with open(os.path.join(absolute_path, 'calibration/ccm_cold.json'), 'r') as filehandle:
    ccm_5500k = json.load(filehandle)

with open(os.path.join(absolute_path, 'calibration/tonecurve.json'), 'r') as filehandle:
    tonecurve = json.load(filehandle)

# these are manually tweaked to make the two reference images look ok
# when opened in ACR with the default white-balance
camera_calibration_3000k = [[178, 100], [0, 10], [0, 10],
                              [0, 10], [200, 100], [0, 10],
                              [0, 10], [0, 10], [118, 100]]
camera_calibration_5500k = [[135, 100], [0, 10], [0, 10],
                              [0, 10], [229, 100], [0, 10],
                              [0, 10], [0, 10], [191, 100]]

# load the huesats
with open(os.path.join(absolute_path,'calibration/warm_huesat.json'), 'r') as filehandle:
    huesat_3000k = json.load(filehandle)
with open(os.path.join(absolute_path,'calibration/cold_huesat.json'), 'r') as filehandle:
    huesat_5500k = json.load(filehandle)

import glob, os
files = glob.glob("*.RAW")
files.sort()
for file in files:
    try:
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
        #rawImage = cv2.cvtColor(rawImage, cv2.COLOR_BAYER_RGGB2RGB)
        #rawImage = cv2.rotate(rawImage, cv2.ROTATE_180)
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
        t.set(Tag.Orientation, Orientation.Rotate180)
        t.set(Tag.PhotometricInterpretation, PhotometricInterpretation.Color_Filter_Array)
        t.set(Tag.SampleFormat, SampleFormat.Uint)
        t.set(Tag.SamplesPerPixel, 1)
        t.set(Tag.BitsPerSample, bpp)
        t.set(Tag.CFARepeatPatternDim, [2,2])
        t.set(Tag.CFAPattern, CFAPattern.RGGB)
        #t.set(Tag.BlackLevel, 0)
        #t.set(Tag.WhiteLevel, ((1 << bpp) -1) )
        t.set(Tag.ColorMatrix1, ccm_5500k)
        t.set(Tag.ColorMatrix2, ccm_3000k)
        #t.set(Tag.ForwardMatrix1, fm1)
        #t.set(Tag.ForwardMatrix2, fm2)
        t.set(Tag.CameraCalibration1, camera_calibration_5500k)
        t.set(Tag.CameraCalibration2, camera_calibration_3000k)
        t.set(Tag.CalibrationIlluminant1, CalibrationIlluminant.D55)
        t.set(Tag.CalibrationIlluminant2, CalibrationIlluminant.Standard_Light_A)
        # skipping this is allowed but not recommended – but we have no white-balancer so kind of have to!
        #t.set(Tag.AsShotNeutral, camera_calibration)
        t.set(Tag.BaselineExposure, [[-150,100]])
        t.set(Tag.Make, "Hayear")
        t.set(Tag.Model, "HY-6110")
        t.set(Tag.DNGVersion, DNGVersion.V1_4)
        t.set(Tag.DNGBackwardVersion, DNGVersion.V1_2)
        t.set(Tag.PreviewColorSpace, PreviewColorSpace.sRGB)
        t.set(Tag.PhotographicSensitivity, [100]) 
        t.set(Tag.ExposureTime, [[1,30]])  
        profile_name = "PiDNG / hayerdebayer / HY-6110 Profile"
        profile_embed = 3
        t.set(Tag.ProfileName, profile_name)
        t.set(Tag.ProfileEmbedPolicy, [profile_embed])
        t.set(Tag.ProfileHueSatMapDims, [90, 25, 1])
        t.set(Tag.ProfileHueSatMapData1, huesat_5500k)
        t.set(Tag.ProfileHueSatMapData2, huesat_3000k)
        t.set(Tag.ProfileToneCurve, tonecurve)
        t.set(Tag.NewSubfileType, 0)
        t.set(Tag.UniqueCameraModel, "HY-6110")

        # save to dng file.
        r = RAW2DNG()
        r.options(t, path="", compress=False)
        r.convert(rawImage, filename=newfile)
    except Exception as error:
        print(type(error))    # the exception type
        print(error.args)     # arguments stored in .args
        print(error)

