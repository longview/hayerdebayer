# HayerDebayer

This is a set of basic tools to work with Hayer HY-6110 .RAW still images.

The .RAW format of the HY-6110 can be accessed by changing the Image Format setting in the camera to JPEG+RAW.

The .RAW files are incredibly basic, they are 12-bit packed raw sensor dumps, without any debayering or seemingly any denoising or similar. The resolution is 3840x2160.

I made a set of tools to work with these images, the results are not perfect but are a dramatic improvement to achievable image quality. Below a comparison of the camera JPEG's and a basic ACR processed RAW file is shown.

![](assets/20230928_233930_Comparison.jpg)

convert.py uses OpenCV to read in the packed 12 bit format and try to convert it to a 16-bit TIFF format including debayering. This tool is interesting but will likely not be maintained as the .DNG method is much more practical for photographic purposes.

hayerdng.py uses PiDNG to read the packed 12 bit data and store it as a 16 bit linear DNG file that can be read in using e.g. Adobe Camera RAW or Lightroom.

This tool uses a set of (hard coded) colour correction matrix with two calibration temperatures made using a Macbeth chart at 6500 K and approximately 3000 K.

It takes no arguments and converts any .RAW file in it's current working directory into a .DNG file, overwriting any existing files.

These corrections were made using Adobe DNG Profile Editor, the exported .dcp files were then read out using dcpTool (MacOS binary included) and copied into the source code. The source files were 20230928_164557.RAW (6500 K) and 20230928_164654.RAW (3000 K).

Note that the PiDNG sample code will not produce a standards compliant .DNG, dng_validate was used to detect these issues and make something ACR will accept. This tool is quite useful when making changes.

Currently the main issue is that the JPEG previews in the .DNG files are not corrected (not major IMO), the other annoyance is that ACR doesn't correctly detect the white balance of the camera, thinking the image is much warmer than it actually is. I *believe* this is caused by incorrect ForwardMatrix entries. The current set is copied from the PiDNG source code for one of the Pi cameras and is not correct, but works better than leaving them out. From what I know there is enough data here to calculate appropriate matrices but I haven't gotten around to it yet.

To work around this I loaded up the two reference images in ACR and white balanced off the chart then saved those as presets for use as baselines for outdoors and indoor settings. It is also advisable to configure other parameters like CA removal at this time.
