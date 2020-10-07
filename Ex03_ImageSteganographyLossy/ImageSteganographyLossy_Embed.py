import constants
from huffman import Huffman 
import jpeg_decoder

import struct 
import numpy as np
from scipy import fftpack
from PIL import Image
from bitarray import bitarray
import matplotlib.pyplot as plt

def dct2(pixels):
    '''
    Hàm biến đổi từ ma trận điểm ảnh sang ma trận hệ số DCT (2 ma trận có cùng shape).
    '''
    return fftpack.dct(fftpack.dct(pixels, axis=0, norm='ortho'), axis=1, norm='ortho')

def idct2(dct_coefs):
    '''
    Hàm biến đổi từ ma trận hệ số DCT sang ma trận điểm ảnh (2 ma trận có cùng shape).
    '''
    return fftpack.idct(fftpack.idct(dct_coefs, axis=0 , norm='ortho'), axis=1, norm='ortho')

def get_header(img_height, img_width, quant_table):
    '''
    Hàm tính chuỗi byte ứng với header của ảnh JPEG.
    (Code được điều chỉnh từ nguồn: https://github.com/reinhrst/pygreypeg.)
    '''
    buf = bytearray()

    def writebyte(val):
        buf.extend(struct.pack(">B", val))

    def writeshort(val):
        buf.extend(struct.pack(">H", val))

    # SOI
    writeshort(0xFFD8)  # SOI marker

    # APP0
    writeshort(0xFFE0)  # APP0 marker
    writeshort(0x0010)  # segment length
    writebyte(0x4A)     # 'J'
    writebyte(0x46)     # 'F'
    writebyte(0x49)     # 'I'
    writebyte(0x46)     # 'F'
    writebyte(0x00)     # '\0'
    writeshort(0x0101)  # v1.1
    writebyte(0x00)     # no density unit
    writeshort(0x0001)  # X density = 1
    writeshort(0x0001)  # Y density = 1
    writebyte(0x00)     # thumbnail width = 0
    writebyte(0x00)     # thumbnail height = 0

    # DQT
    quant_table = quant_table.reshape(-1)
    writeshort(0xFFDB)  # DQT marker
    writeshort(0x0043)  # segment length
    writebyte(0x00)     # table 0, 8-bit precision (0)
    for index in constants.zz:
        writebyte(quant_table[index])

    # SOF0
    writeshort(0xFFC0)  # SOF0 marker
    writeshort(0x000B)  # segment length
    writebyte(0x08)     # 8-bit precision
    writeshort(img_height)
    writeshort(img_width)
    writebyte(0x01)     # 1 component only (grayscale)
    writebyte(0x01)     # component ID = 1
    writebyte(0x11)     # no subsampling
    writebyte(0x00)     # quantization table 0

    # DHT
    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.dc_nb_vals)  # segment length
    writebyte(0x00)                        # table 0 (DC), type 0 (0 = Y, 1 = UV)
    for node in constants.dc_nodes[1:]:
        writebyte(node)
    for val in constants.dc_vals:
        writebyte(val)

    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.ac_nb_vals)
    writebyte(0x10)                        # table 1 (AC), type 0 (0 = Y, 1 = UV)
    for node in constants.ac_nodes[1:]:
        writebyte(node)
    for val in constants.ac_vals:
        writebyte(val)

    # SOS
    writeshort(0xFFDA)  # SOS marker
    writeshort(8)       # segment length
    writebyte(0x01)     # nb. components
    writebyte(0x01)     # Y component ID
    writebyte(0x00)     # Y HT = 0
    # segment end
    writebyte(0x00)
    writebyte(0x3F)
    writebyte(0x00)

    return buf

def main():
    msg_file = 'msg.txt'
    cover_img_file = 'cover.bmp'
    quant_table = np.array([
        16, 11, 10, 16,  1,  1,  1,  1,
        12, 12, 14,  1,  1,  1,  1, 55,
        14, 13,  1,  1,  1,  1, 69, 56,
        14,  1,  1,  1,  1, 87, 80, 62,
         1,  1,  1,  1, 68, 109, 103, 77,
         1,  1,  1, 64, 81, 104, 113, 92,
         1,  1, 78, 87, 103, 121, 120, 101,
         1, 92, 95, 98, 112, 100, 103, 99
    ]).reshape(8, 8)
    stego_img_file = 'stego.jpg'

    # I. Đọc cover img file
    cover_pixels = np.array(Image.open(cover_img_file))
    #print(cover_pixels)
    #print(cover_pixels.shape)
    shape_img = cover_pixels.shape
    height = 512 # shape_img[0]
    width = 512 #shape_img[1]

    # II. Đọc msg file, chuyển msg thành msg bits, kiểm xem có đủ chỗ nhúng không, thêm 100... vào msg bits
        # Đọc msg file
    with open(msg_file, 'r') as f:
        msg = f.read()
    #print(msg)

        # Chuyển msg thành msg bits
    msg_bits = bitarray()
    msg_bits.fromstring(msg)
    print(msg_bits[26:52])

        # Lấy danh sách index ChangChenChung của bảng quatization
    lst_idxCCC_quant = list()
    for idx, item in np.ndenumerate(quant_table):
        if item == 1:
            lst_idxCCC_quant.append(idx)
    np_idxCCC_quant = np.array(lst_idxCCC_quant)
    #print(len(np_idxCCC_quant))

        # Kiểm xem có đủ chỗ nhúng không?
    num_block8x8 = cover_pixels.size / (8*8)    # Số block 8x8 =  Số pixels của ảnh / 64
    capacity = num_block8x8 * len(np_idxCCC_quant) # Sức chứa = Số block 8x8 * Số bit có thể nhúng trong mỗi block
    if len(msg_bits) + 1 > capacity:
        print("Not Embed")

        # Thêm 100... vào msg bits
    capacity = int(capacity)
    msg_bits.extend('1' + '0' * (capacity - len(msg_bits) - 1))   # Trừ 1 vì đã thêm số 1 trong dãy 100...
    #print(msg_bits[:16])

    # III. Nén jpeg, trong quá trình nén thực hiện nhúng msg bits
    jpeg_bytes = bytearray()
    jpeg_bytes.extend(get_header(height, width, quant_table))
    huf = Huffman()

    lst_block8x8 = list()
    row = 0
    while row < 512:
        col = 0
        while col < 512:
            pos = (row, col)
            block8x8 = cover_pixels[pos[0]:pos[0]+8, pos[1]:pos[1]+8]    
            lst_block8x8.append(block8x8)        
            col = col + 8
        row = row + 8
    np_block8x8 = np.array(lst_block8x8, dtype=int)
    #print(np_block8x8[64])

    a = list()
    num_lsbs = 1
    i = 0
    idx_bit = 0
    for block_8x8 in np_block8x8: # Duyệt từng block 8x8
        if i == 0:
            i = i +1
            continue
        if i == 8:
            block_8x8_subtract = block_8x8 - 128            # Trừ 128
            block_dct = dct2(block_8x8_subtract)            # Tính các hệ số DCT
            block_quantized_dct = block_dct / quant_table   # Tính các hệ số quantized DCT
            block_round = np.round(block_quantized_dct, 0)  # Làm tròn thành số nguyên gần nhất

            # Nhúng msg bits vào các hệ số quantized DCT
            block_stego = np.array(block_round, dtype=int)
            print(block_stego)


            for idx, item in np.ndenumerate(block_round): # Duyệt từng phần tử trong block 8x8            
                item_abs = int(item)
                if (idx == np_idxCCC_quant).all(1).any(): # Nếu phần tử có index nằm trong danh sách index ChangChenChung của bảng quatization thì xét tiếp                
                    bit_embed = int(msg_bits[idx_bit : idx_bit + num_lsbs].to01(), 2) # Lấy bit nhúng
                    embed = int((item_abs>>num_lsbs<<num_lsbs) + bit_embed) # Nhúng bit
                    idx_bit = idx_bit + num_lsbs
                    block_stego[idx] = embed

            a.append(block_stego)
        i = i + 1
    b= np.array(a)
    print(b[:5])

if __name__ == "__main__":
    main()