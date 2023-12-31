# HayerDebayer

This is a few tools to work with Hayer HY-6110 .RAW still images.

The .RAW format of the HY-6110 can be accessed by changing the Image Format setting in the camera to JPEG+RAW.

The .RAW files are incredibly basic, they are 12-bit packed raw sensor dumps, without any debayering or seemingly any denoising or similar, or headers for that matter. The resolution is 3840x2160.

I made two tools to work with these images, the results are not perfect but are a dramatic improvement to achievable image quality. Below a comparison of the camera JPEG's and a basic ACR processed RAW file is shown.

![](assets/20230928_233930_Comparison.jpg)

`convert.py` uses OpenCV to read in the packed 12 bit format and try to convert it to a 16-bit TIFF format including debayering but in linear RGB. This is basically a test-program that is modified as needed to e.g. compute colour matrices for the DNG converter.

`hayerdng.py` uses PiDNG to read the packed 12 bit data and store it as a 16 bit linear DNG file that can be read in using e.g. Adobe Camera RAW or Lightroom.

`parsexmp.py` is used to parse the generated .xmp profiles converted from the DNG Profile Creator DCP files. It extracts the CCM's, tonecurves (only read from cold profile), and the HueSat tables for the two reference colour temperatures. These are read by hayerdng.py and embedded in the .DNG files.

Required Python modules: `PiDNG` (use latest GitHub, not pip), `numpy`, and `OpenCV2`. The OpenCV part is only used for image rotation currently and could in principle be removed.

The tool embeds a set of (hard coded) colour correction matrices for two calibration temperatures made using a Macbeth chart at 6500 K and approximately 3000 K.

It takes no arguments and converts any .RAW file in it's current working directory into a .DNG file, overwriting any existing files.

The correction matrices were made using Adobe DNG Profile Editor, the exported .dcp files were then read out using dcpTool (MacOS binary included) to convert them to XMP format. These XMP files are then converted to JSON arrays in parsexmp.py. The source files were *cal_reference_5500k.RAW* (5500 K) and *cal_reference_warm.RAW* (~3000 K).

The HueSat profiles are used, the effect is relatively subtle (compared to the CCM's!):

![](assets/20230929_224345_huesat_comparison_copy.jpg)

For easier comparison:

![](assets/20230929_233331_huesat_comparison2_copy.jpg)

Note that the PiDNG sample code at the time of writing will not produce a standards compliant .DNG. dng_validate was used to detect and correct these issues to make something ACR will accept. The validation tool is quite useful when making changes.

Currently the major issues are:

1. idk what I'm doing
2. (Resolved?) The JPEG previews in the .DNG files are not corrected (not major)
3. (Somewhat resolved) ACR doesn't correctly detect the white balance of the camera, thinking the image is much warmer than it actually is.E.g. a RAW file at 3000 K must be processed as approximately 5800 K with a heavy purple tint to make the white balance look right.

These errors seem to be corrected by generating a CameraCalibration1/2 matrix, this matrix was tweaked by opening the DNG in ACR and adjusting until the default view was correct for warm/white light.

To work around the residual error I loaded up the two reference images in ACR and white balanced off the chart then saved those as presets for use as baselines for outdoors and indoor settings. It is also advisable to configure other parameters like CA removal at this time, but those are lens specific so you will have to make your own.

TODO's:

* It seems like OpenCV may have a better debayer than ACR? Try to make the conversion tool do debayering before DNG conversion.

Here is the exiftool output for the currently generated files:

```ExifTool Version Number         : 12.60
File Name                       : cal_reference_5500k.dng
Directory                       : .
File Size                       : 17 MB
File Modification Date/Time     : 2023:09:29 22:46:59+02:00
File Access Date/Time           : 2023:09:29 22:47:28+02:00
File Inode Change Date/Time     : 2023:09:29 22:47:04+02:00
File Permissions                : -rw-r--r--
File Type                       : DNG
File Type Extension             : dng
MIME Type                       : image/x-adobe-dng
Exif Byte Order                 : Little-endian (Intel, II)
Subfile Type                    : Full-resolution image
Image Width                     : 3840
Image Height                    : 2160
Bits Per Sample                 : 16
Compression                     : Uncompressed
Photometric Interpretation      : Color Filter Array
Make                            : Hayear
Camera Model Name               : HY-6110
Strip Offsets                   : 54924
Orientation                     : Rotate 180
Samples Per Pixel               : 1
Rows Per Strip                  : 2160
Strip Byte Counts               : 16588800
Software                        : PiDNG
Sample Format                   : Unsigned
CFA Repeat Pattern Dim          : 2 2
CFA Pattern 2                   : 0 1 1 2
Exposure Time                   : 1/30
ISO                             : 100
DNG Version                     : 1.4.0.0
DNG Backward Version            : 1.2.0.0
Unique Camera Model             : HY-6110
Color Matrix 1                  : 1.5445 -0.493 -0.1174 0.0191 0.8682 0.1374 -0.0653 0.1245 0.5655
Color Matrix 2                  : 1.5445 -0.493 -0.1174 0.0191 0.8682 0.1374 -0.0653 0.1245 0.5655
Camera Calibration 1            : 1.35 0 0 0 2.29 0 0 0 1.91
Camera Calibration 2            : 1.78 0 0 0 2 0 0 0 1.18
Baseline Exposure               : -1.5
Calibration Illuminant 1        : D55
Calibration Illuminant 2        : Standard Light A
Profile Name                    : PiDNG / HY-6110 Profile
Profile Hue Sat Map Dims        : 90 25 1
Profile Hue Sat Map Data 1      : (Binary data 80482 bytes, use -b option to extract)
Profile Hue Sat Map Data 2      : (Binary data 80086 bytes, use -b option to extract)
Profile Tone Curve              : (Binary data 189 bytes, use -b option to extract)
Profile Embed Policy            : No Restrictions
Preview Color Space             : sRGB
CFA Pattern                     : [Red,Green][Green,Blue]
Image Size                      : 3840x2160
Megapixels                      : 8.3
Shutter Speed                   : 1/30

```

## Microphone Noise

The HY-6110 microphone input pinout is not documented:

* Tip: Unfiltered (noisy!) 3.3 V power supply through R88 on the I/O board
* Ring: 2 V biased electret microphone input
* Sleeve: Ground (differential to whatever processor/ASIC is used)

If your microphone is like mine it will be severely affected by the tip power supply, leading to significant noise in recordings. I removed R88 from the I/O board to disconnect this power supply and make it work with a fairly generic shotgun mic.

Using a microphone which only connects the signal output to the Ring would likely also work fine.

## Video Mode

Below is the output of mediainfo for a video recording in H.265 mode. In my opinion the video recordings look pretty good, much better than the JPEG outputs!

```
Format                                   : MPEG-4
Format profile                           : Base Media / Version 2
Codec ID                                 : mp42 (isom/avc1/mp42)
File size                                : 459 MiB
Duration                                 : 2 min 28 s
Overall bit rate mode                    : Variable
Overall bit rate                         : 25.9 Mb/s
Frame rate                               : 30.000 FPS
Encoded date                             : 2022-01-02 06:01:24 UTC
Tagged date                              : 2022-01-02 06:01:24 UTC

Video
ID                                       : 1
Format                                   : HEVC
Format/Info                              : High Efficiency Video Coding
Format profile                           : Main@L5@High
Codec ID                                 : hvc1
Codec ID/Info                            : High Efficiency Video Coding
Duration                                 : 2 min 28 s
Bit rate                                 : 25.6 Mb/s
Width                                    : 3 840 pixels
Height                                   : 2 160 pixels
Display aspect ratio                     : 16:9
Frame rate mode                          : Constant
Frame rate                               : 30.000 FPS
Color space                              : YUV
Chroma subsampling                       : 4:2:0
Bit depth                                : 8 bits
Bits/(Pixel*Frame)                       : 0.103
Stream size                              : 454 MiB (99%)
Language                                 : English
Encoded date                             : 2022-01-02 06:01:24 UTC
Tagged date                              : 2022-01-02 06:01:24 UTC
Color range                              : Full
Color primaries                          : BT.709
Transfer characteristics                 : BT.709
Matrix coefficients                      : BT.709
Codec configuration box                  : hvcC

Audio
ID                                       : 2
Format                                   : AAC LC
Format/Info                              : Advanced Audio Codec Low Complexity
Codec ID                                 : mp4a-40-2
Duration                                 : 2 min 28 s
Bit rate mode                            : Variable
Bit rate                                 : 96.0 kb/s
Channel(s)                               : 1 channel
Channel layout                           : M
Sampling rate                            : 32.0 kHz
Frame rate                               : 31.250 FPS (1024 SPF)
Compression mode                         : Lossy
Stream size                              : 1.70 MiB (0%)
Language                                 : English
```

## USB-C Mode

A USB-C to USB 3.0 A cable is included (many USB-C cables are too wide to fit the narrow camera cutout by the way).

When connected the camera works as a 4k30 capable webcam with monoaural audio, I haven't really tested it.
