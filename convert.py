import cv2
import numpy as np

width = 3840
height = 2160

def lin2rgb(im):
    """ Convert im from "Linear sRGB" to sRGB - apply Gamma. """
    # sRGB standard applies gamma = 2.4, Break Point = 0.00304 (and computed Slope = 12.92)    
    # lin2rgb MATLAB functions uses the exact formula [we may approximate it to power of (1/gamma)].
    g = 2.4
    bp = 0.00304
    inv_g = 1/g
    sls = 1 / (g/(bp**(inv_g - 1)) - g*bp + bp)
    fs = g*sls / (bp**(inv_g - 1))
    co = fs*bp**(inv_g) - sls*bp

    srgb = im.copy()
    srgb[im <= bp] = sls * im[im <= bp]
    srgb[im > bp] = np.power(fs*im[im > bp], inv_g) - co
    return srgb

with open("reference_photos/20230928_164654.RAW", "rb") as rawimg:
    # Read the packed 12bits as bytes - each 3 bytes applies 2 pixels
    data = np.fromfile(rawimg, np.uint8, width * height * 3//2)

    data = data.astype(np.uint16)  # Cast the data to uint16 type.
    result = np.zeros(data.size*2//3, np.uint16)  # Initialize matrix for storing the pixels.

    # 12 bits packing: ######## ######## ########
    #                  | 8bits| | 4 | 4  |  8   |
    #                  |  lsb | |msb|lsb |  msb |
    #                  <-----------><----------->
    #                     12 bits       12 bits
    result[0::2] = ((data[1::3] &  15) << 8) | data[0::3]
    result[1::2] = (data[1::3] >> 4) | (data[2::3] << 4)
    bayer_im = np.reshape(result, (height, width))

    # Apply Demosacing (COLOR_BAYER_BG2BGR gives the best result out of the 4 combinations).
    rgb = cv2.cvtColor(bayer_im, cv2.COLOR_BAYER_RGGB2RGB)  # The result is RGB format with 16 bits per pixel and 12 bits range [0, 2^12-1].

    # correct to normalized format
    img_in_range_0to1 = rgb.astype(np.float32)/4096
    lin_img = lin2rgb(img_in_range_0to1)
    #lin_img = img_in_range_0to1;
    ccm_identity = np.array([ [ 1, 0, 0],
                     [0,  1, 0], 
                     [0,  0,  0] ])
    ccm_test1 = np.array([ [ 1.047806, 0.022888, -0.050110],
                     [0.029541,  0.990479, -0.017029], 
                     [-0.009216,  0.015045,  0.752136] ])
    lin_img = lin_img.astype(np.float32).reshape((lin_img.shape[0] * lin_img.shape[1], 3))
    colourcorrected_img = np.matmul(lin_img, ccm_test1)  
    colourcorrected_img = colourcorrected_img.reshape(rgb.shape).astype(colourcorrected_img.dtype)

    normalized_img = cv2.normalize(colourcorrected_img, None, 0, 1.0,
cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    # scale to 16-bit normalized
    gamma_img = np.round(normalized_img * 65535).astype(np.uint16)

    # TODO: colour correction stuff here

    # rotate image
    image = cv2.rotate(gamma_img, cv2.ROTATE_180)
    # set 16-bit TIFF mode
    image = cv2.cvtColor(image, cv2.CV_16U)
    # write image
    cv2.imwrite("test.tif", image)


    # Convert to uint8 before saving as JPEG (not part of the conversion).
    #colimg = np.round(image.astype(float) * (255/65535))
    #cv2.imwrite("test.jpeg", colimg)

# now read back and apply the .icc profile
# then the image viewer will have to deal with the conversion for us

""" from PIL import Image, ImageCms
# Read image
img = Image.open("test.tif")

# Read profile
# this profile made with ColorChecker shooting a macbeth chart under 6500k illumination
src_profile = ImageCms.getOpenProfile("CameraProfile2.icc")
dst_profile = ImageCms.createProfile('sRGB')
imgcorrected = ImageCms.profileToProfile(img, src_profile, dst_profile)

# Save image with profile
imgcorrected.save("test2.tif") """