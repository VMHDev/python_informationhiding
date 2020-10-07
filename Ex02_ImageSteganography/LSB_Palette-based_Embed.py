from bitarray import bitarray
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Lớp thông tin của các phần tử bảng màu
class ItemPalette():
    # Khai báo các thuộc tính:
    IndexPalette = -1   # Index của phần tử
    RGBPalette = np.zeros(3, dtype = np.uint8)  # Giá trị của RGB
    DistanceEuclid = 0 # Khoảng cách của phần tử đến một phần tử khác

    # Phương thức khởi tạo
    def __init__(self, _IndexPalette = -1, _RGBPalette = np.zeros(3, dtype = np.uint8), _DistanceEuclid = 0):
        self.IndexPalette = _IndexPalette
        self.RGBPalette = _RGBPalette
        self.DistanceEuclid = _DistanceEuclid

# Hàm xác định bit nhúng của pixels
def specify_bit_embed(rgb):
    if (rgb[0] + rgb[1] + rgb[2]) % 2 == 1:
        return 1
    else:
        return 0

# Hàm phân tách bảng màu thành 2 phần: Phần nhúng bit 1 và phần nhúng bit 0
# Phần nhúng bit 0 gồm những pixels có rgb sao cho (R+G+B)%2 = 0
# Phần nhúng bit 1 gồm những pixels có rgb sao cho (R+G+B)%2 = 1
def partition_palette(palette):
    lstBit0 = []
    lstBit1 = []
    for idx, rgb in enumerate(palette[0]):
        objItemPalette = ItemPalette()
        objItemPalette.IndexPalette = idx
        objItemPalette.RGBPalette = rgb        
        if specify_bit_embed(rgb) == 0:
            lstBit0.append(objItemPalette)
        else:
            lstBit1.append(objItemPalette)
    return lstBit0, lstBit1

# Hàm tính khoảng cách Euclid giữa hai numpy array
def dist_euclid(x,y):
    return np.sqrt(np.sum((x-y)**2))

# Tìm khoảng cách Euclid nhỏ nhất giữa một phần tử trong bảng màu với các phần tử khác trong bảng
# idxRGB: Chỉ số của phần tử trong bảng màu
# rgb: Giá trị RGB của phần tử
# lstBit: Danh sách các phần tử còn lại
def min_distance_euclid(idxRGB, rgb, lstBit):
    objItemPalette = ItemPalette()
    # Khởi tạo khoảng cách nhỏ nhất
    if idxRGB == 0:
        rgbX = rgb.astype(np.int)
        rgbY = lstBit[1].RGBPalette.astype(np.int)
        distMin = dist_euclid(rgbX, rgbY)
    else:
        rgbX = rgb.astype(np.int)
        rgbY = lstBit[0].RGBPalette.astype(np.int)
        distMin = dist_euclid(rgbX, rgbY)        

    # Tính khoảng cách Euclid của phần tử đến các phần tử khác => Cập nhật phần tử có khoảng cách nhỏ nhất   
    for item in lstBit:
        if idxRGB == item.IndexPalette:
            continue
        x = rgb.astype(np.int)
        y = item.RGBPalette.astype(np.int)
        dist = dist_euclid(x, y)
        if dist < distMin:
            objItemPalette.IndexPalette = item.IndexPalette
            objItemPalette.RGBPalette = item.RGBPalette
            objItemPalette.DistanceEuclid = dist
            distMin = dist

    return objItemPalette

def main():
    cover_img_file = 'lena.gif'
    msg_file = 'msg.txt'

    # Đọc cover img file
    cover_img = Image.open(cover_img_file)
    cover_pixels = np.array(cover_img)
    palette = cover_img.getpalette() # Kết quả là list các giá trị Red, Green, Blue của các màu 
                                     # trong bảng màu, 3 giá trị liên tiếp ứng với một màu
    palette = np.array(palette, dtype=np.uint8).reshape((1, -1, 3)) # Reshape lại dưới dạng ảnh RGB
    #----------------------------------------------------------------------------------------------

    # Đọc file tin mật
    with open(msg_file, 'r') as f:
        msg = f.read()

    # Chuyển đổi tin mật sang dạng tin mật
    msg_bits = bitarray()
    msg_bits.fromstring(msg)  
    num_bit_add =  cover_pixels.size - len(msg_bits)
    if num_bit_add > 0:
        msg_bits.append(True)                   # Thêm bit 1 vào  
        bit_add = [False] * (num_bit_add - 1) 
        msg_bits.extend(bit_add)                # Thêm  một list bit 0 vào
    else:
        print('Không đủ bit nhúng!')
        return

    lst_bit_0, lst_bit_1 = partition_palette(palette)

    idx_bit_Embed = 0
    stego_pixels = np.empty_like(cover_pixels)
    for idx, pixelsIdx in np.ndenumerate(cover_pixels):
        rgb = palette[0][pixelsIdx]
        if msg_bits[idx_bit_Embed]:
            obj = min_distance_euclid(pixelsIdx, rgb, lst_bit_1)
        else:
            obj = min_distance_euclid(pixelsIdx, rgb, lst_bit_0)
        stego_pixels[idx] = obj.IndexPalette
        idx_bit_Embed += 1
    print(stego_pixels)



if __name__ == "__main__":
    main()

# Xử lý ở bảng màu:
    # Hàm Tính giá trị (R+G+B)%2
    # => Chia bảng màu thành 2 phần 
        # (R+G+B)%2 = 1 
        # (R+G+B)%2 = 0
        # Mỗi phần có hai giá trị: idx của RGB và giá trị của RGB
    
    # Hàm tính khoảng cách Euclid
    # =>Input là:
        # RGB của ba màu đang xét
        # 1 trong phần của bảng màu đã chia
    # Tính khoảng cách Euclid của màu đang xét đến từng màu trong thành phần
    # => Output là idx của RGB và khoảng cách Euclid

    # Hàm tìm màu gần nhất
    # => Nhúng bit 