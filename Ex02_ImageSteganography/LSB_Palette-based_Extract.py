from bitarray import bitarray
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Hàm xác định bit nhúng của pixels
def specify_bit_embed(rgb):
    if (rgb[0] + rgb[1] + rgb[2]) % 2 == 1:
        return 1
    else:
        return 0

def main():
    stego_img_file = 'correct_baboon_stego.gif'

    imgStego = Image.open(stego_img_file)
    print(imgStego)
    print(type(imgStego))

    tableIndexs = np.array(imgStego)
    print(type(tableIndexs))
    print(tableIndexs.shape)
    print('---------------------------------------------')
    palette = imgStego.getpalette()
    nparrayImg = np.array(palette)
    npReshape = nparrayImg.reshape((1,-1,3))

    # RGB pixels đầu tiên
    # pixels_idx00 = tableIndexs[0][0] # Lấy chỉ số của pixels đâu tiên dựa vào table index
    # rgb_pixels_idx00 = npReshape[0, pixels_idx00] # Lấy RGB của pixels đầu tiên dựa vào chỉ số của table index và palette
    # print(type(rgb_pixels_idx00))
    # print(rgb_pixels_idx00)
    # RGB pixels đầu tiên
    # pixels_idx01 = tableIndexs[0][1] # Lấy chỉ số của pixels đâu tiên dựa vào table index
    # rgb_pixels_idx01 = npReshape[0, pixels_idx01] # Lấy RGB của pixels đầu tiên dựa vào chỉ số của table index và palette
    # print(rgb_pixels_idx01)

    ################################################ Test specify_bit_embed
    # a = specify_bit_embed(rgb_pixels_idx00)
    # print(a)

    # a = specify_bit_embed(rgb_pixels_idx01)
    # print(a)
    ################################################

    #print(tableIndexs)
    lstBitEmbed = list()
    #for idx, row in np.ndenumerate(tableIndexs):
    for pixelsIdxRow in tableIndexs:
        for pixelsIdx in pixelsIdxRow:
            rgbPixels = npReshape[0, pixelsIdx]
            #print(rgbPixels)
            bit = specify_bit_embed(rgbPixels)
            lstBitEmbed.append(bit)
    #print(lstBitEmbed)
    
    msgBit = bitarray(lstBitEmbed)
    msgBit = msgBit[:msgBit.to01().rfind('1')]
    text = msgBit.tostring()
    print(text)

if __name__ == "__main__":
    main()