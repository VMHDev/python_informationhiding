import constants
from huffman import Huffman 
import jpeg_decoder

import struct 
import numpy as np
from scipy import fftpack
from PIL import Image
from bitarray import bitarray
import matplotlib.pyplot as plt

def main():
    stego_img_file = 'correct_stego.jpg'

    # Trong quá trình giải nén stego img file, lấy các hệ số quantized dct và bảng quatization
    quant_dct_coefs, quant_table = jpeg_decoder.get_quant_dct_coefs_and_quant_table(stego_img_file)
    #print(quant_dct_coefs.shape, type(quant_dct_coefs)) # (262144,) <class 'numpy.ndarray'>
    #print(quant_table.shape, type(quant_table)) # print (8, 8) <class 'numpy.ndarray'>
    #print(quant_dct_coefs[:64]) #p print [16  0  0  0  0 -1 -6  6  1  0  0 -5  3  3 -3  0  0  0 -2  3]
    #print(quant_table)  #[[ 16  11  10  16   1   1   1   1]
                        # [ 12  12  14   1   1   1   1  55]
                        # [ 14  13   1   1   1   1  69  56]
                        # [ 14   1   1   1   1  87  80  62]
                        # [  1   1   1   1  68 109 103  77]
                        # [  1   1   1  64  81 104 113  92]
                        # [  1   1  78  87 103 121 120 101]
                        # [  1  92  95  98 112 100 103  99]]
    table_factor_reshape = quant_dct_coefs.reshape(-1,8,8)
    #print(a)
            #[[[16  0  0  0  0 -1 -6  6]
            #  [ 1  0  0 -5  3  3 -3  0]
            #  [ 0  0 -2  3 -2  1  0  0]
            #  [ 0  0  3  1 -2  0  0  0]
            #  [-2 -1  0 -2  0  0  0  0]
            #  [ 0  1 -2  0  0  0  0  0]
            #  [-1  0  0  0  0  0  0  0]
            #  [ 1  0  0  0  0  0  0  0]]
            #
            # [[16  2  0  0 -8  9  2 -8]
            #  [ 1  0  0  7 -4  2  6  0]
            #  [ 0  0 -1 -4  0 -2  0  0]
            #  [ 0 -2  0  0  3  0  0  0]
            #  [ 2  1  1  0  0  0  0  0]
            #  [ 0  1 -2  0  0  0  0  0]
            #  [-3  0  0  0  0  0  0  0]
            #  [ 2  0  0  0  0  0  0  0]]]
    #print(table_factor_reshape[0])

    # Lấy danh sách index ChangChenChung của bảng quatization
    lst_idxCCC_quant = list()
    for idx, item in np.ndenumerate(quant_table):
        if item == 1:
            lst_idxCCC_quant.append(idx)
    np_idxCCC_quant = np.array(lst_idxCCC_quant)

    num_lsbs = 1
    extr_msg_bits = bitarray()
    for block_8x8 in table_factor_reshape: # Duyệt từng block 8x8
        for idx, item in np.ndenumerate(block_8x8): # Duyệt từng phần tử trong block 8x8
            if (idx == np_idxCCC_quant).all(1).any(): # Nếu phần tử có index nằm trong danh sách index ChangChenChung của bảng quatization thì xét tiếp
                extr_msg_bits.extend((np.binary_repr(abs(item) & (2**num_lsbs-1), num_lsbs))) # Lấy bit nhúng

    # Cắt đuôi '100...' ra khỏi msg bits
    extr_msg_bits = extr_msg_bits[:extr_msg_bits.to01().rfind('1')]
    print(extr_msg_bits[:16])

    # Chuyển msg bits thành msg
    extr_msg = extr_msg_bits.tostring()
    print(extr_msg)

if __name__ == "__main__":
    main()