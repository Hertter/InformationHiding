import cv2
import numpy as np
import matplotlib.pyplot as plt


# 使用lsb算法处理图像嵌入
class LSB:
    # jpg图像位置
    monarch_lsb_jpg = './embed/monarch_lsb.jpg'
    # png图像位置
    monarch_lsb_png = './embed/monarch_lsb.png'
    # 水印字符串
    str = ''
    # 输出的图像格式
    format = ''
    # 文字的数量
    count = 0

    def __init__(self, s, f, c):
        self.str = s
        self.count = c
        self.format = f

    @staticmethod
    def get_bit(num, bit_idx=8):
        return (num & (1 << (8 - bit_idx))) >> (8 - bit_idx)

    def set_bit(self, num, bit, bit_idx=8):
        num -= self.get_bit(num, bit_idx) << (8 - bit_idx)
        num += (bit << (8 - bit_idx))
        return num

    @staticmethod
    def str_2_bit_seq(s, width=8):
        bin_str = ''.join([(bin(c).replace('0b', '')).zfill(width) for c in s.encode(encoding="utf-8")])
        bit_seq = [np.uint8(c) for c in bin_str]

        return bit_seq

    @staticmethod
    def bit_seq_2_str(msg_bits):
        bin_str = ''.join([bin(b & 1).strip('0b').zfill(1) for b in msg_bits])
        str = np.zeros(np.int(len(msg_bits) / 8)).astype(np.int)
        for i in range(0, len(str)):
            str[i] = int('0b' + bin_str[(8 * i):(8 * (i + 1))], 2)

        return bytes(str.astype(np.int8)).decode(errors='ignore')

    def process(self, img_file):
        img_cover = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
        img_gray = np.copy(img_cover)

        msg = ''
        for _ in np.arange(self.count):
            msg += self.str

        bin_s0 = self.str_2_bit_seq(msg)
        height, width = img_gray.shape

        cnt = 0
        for i in np.arange(height):
            if cnt > len(bin_s0):
                break
            for j in np.arange(width):
                if cnt >= len(bin_s0):
                    break
                bit = bin_s0[cnt]
                cnt += 1
                img_gray[i, j] = self.set_bit(img_gray[i, j], bit, 8)

        cv2.imwrite(self.monarch_lsb_jpg, img_gray)
        cv2.imwrite(self.monarch_lsb_png, img_gray)

        img_marked_jpg = cv2.imread(self.monarch_lsb_jpg, cv2.IMREAD_GRAYSCALE)
        img_marked_png = cv2.imread(self.monarch_lsb_png, cv2.IMREAD_GRAYSCALE)
        bin_s1 = []
        bin_s2 = []

        cnt = 0
        for i in np.arange(height):
            if cnt > len(bin_s0):
                break

            for j in np.arange(width):
                if cnt >= len(bin_s0):
                    break

                bin_s1.append(self.get_bit(img_marked_jpg[i, j], 8))
                bin_s2.append(self.get_bit(img_marked_png[i, j], 8))
                cnt += 1

        msg_out1 = self.bit_seq_2_str(bin_s1)
        msg_out2 = self.bit_seq_2_str(bin_s2)

        print("原文字: ", msg)
        print("JPG: ", msg_out1)
        print("PNG: ", msg_out2)

        self.save_img(img_gray, 'Grayscale Image', 'original.' + self.format)
        if self.format == 'jpg':
            self.save_img(img_marked_jpg, 'Embed Image', 'embed.jpg')
        elif self.format == 'png':
            self.save_img(img_marked_png, 'Embed Image', 'embed.png')

        return msg_out1, msg_out2

    @staticmethod
    def save_img(img_gray, title, save_name):
        plt.figure(0)
        plt.subplot(111)
        plt.imshow(img_gray, cmap='gray')
        plt.title(title)
        plt.tight_layout()
        plt.savefig('./embed/' + save_name)
        plt.close(0)
