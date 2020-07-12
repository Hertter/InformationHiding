import cv2
import numpy as np
import matplotlib.pyplot as plt
import random


# 使用dct算法处理图像嵌入
class DCT:
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

        return bytes(str.astype(np.int8)).decode()

    @staticmethod
    def get_bit(num, bit_idx=8):
        return (num & (1 << (8 - bit_idx))) >> (8 - bit_idx)

    def dct_embed(self, img_gray, msg, seed=2020):
        if len(img_gray.shape) > 2:
            print("Parameter img should be of grayscale")
            return img_gray

        # Step 1: check embedding capacity
        msg2embed = self.str_2_bit_seq(msg)
        len_msg = len(msg2embed)
        # print(len_msg, msg2embed)

        # EC: embedding capacity
        # 1 bit is hided in each N by N block
        N = 8
        height, width = img_gray.shape
        EC = np.int((height) * (width) / N / N)
        if EC < len_msg:
            print('Embedding Capacity {} not enough'.format(EC))
            return img_gray

        # encrypted msg2embed
        random.seed(seed)
        s = [random.randint(0, 1) for i in range(len_msg)]
        bits2embed = np.bitwise_xor(msg2embed, np.uint8(s))
        # print('To embed:', bits2embed)

        # Step 2 data embedding via pair-wise DCT ordering
        # Embeddeding starts from the bottom-right corner
        img_marked = img_gray.copy()
        height, width = img_marked.shape
        cnt = 0
        delta = 10
        r0, c0 = 2, 3
        for row in np.arange(0, height - N, N):
            if cnt >= len_msg:
                break

            for col in np.arange(0, width - N, N):
                if cnt >= len_msg:
                    break

                # embedding one bit in 1 pair of DCT coefficients
                block = np.array(img_marked[row:(row + N), col:(col + N)], np.float32)
                block_dct = cv2.dct(block)
                a, b = (block_dct[r0, c0], block_dct[c0, r0]) if block_dct[r0, c0] > block_dct[c0, r0] else (
                    block_dct[c0, r0], block_dct[r0, c0])
                a += delta
                b -= delta
                block_dct[r0, c0] = (a if bits2embed[cnt] == 1 else b)
                block_dct[c0, r0] = (b if bits2embed[cnt] == 1 else a)

                cnt += 1
                img_marked[row:(row + N), col:(col + N)] = np.array(cv2.idct(block_dct), np.uint8)

        return img_marked, len_msg

    def dct_extract(self, img_marked, len_msg, seed=2020):
        if len(img_marked.shape) > 2:
            print("Parameter img should be of grayscale")
            return img_marked

        N = 8
        height, width = img_marked.shape
        msg_embedded = ''
        cnt = 0
        r0, c0 = 2, 3
        for row in np.arange(0, height - N, N):
            if cnt >= len_msg:
                break

            for col in np.arange(0, width - N, N):
                if cnt >= len_msg:
                    break

                # embedding one bit in 1 pair of DCT coefficients
                block = np.array(img_marked[row:(row + N), col:(col + N)], np.float32)
                block_dct = cv2.dct(block)
                msg_embedded += ('1' if block_dct[r0, c0] > block_dct[c0, r0] else '0')
                cnt += 1

        bits_extracted = [np.uint8(c) for c in msg_embedded]
        # print('Extracted:', bits_extracted)

        random.seed(seed)
        s = [random.randint(0, 1) for i in range(len_msg)]
        msgbits = np.bitwise_xor(bits_extracted, np.uint8(s))
        msg = self.bit_seq_2_str(msgbits)

        return msg

    def process(self, img_file):
        img_gray = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
        msg = ''
        for _ in np.arange(self.count):
            msg += self.str
        img_marked, len_msg = self.dct_embed(img_gray, msg, 20200417)

        cv2.imwrite(self.monarch_lsb_jpg, img_marked, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        cv2.imwrite(self.monarch_lsb_png, img_marked, [int(cv2.IMWRITE_JPEG_QUALITY), 80])

        img_stego_jpg = cv2.imread(self.monarch_lsb_jpg, cv2.IMREAD_GRAYSCALE)
        img_stego_png = cv2.imread(self.monarch_lsb_png, cv2.IMREAD_GRAYSCALE)
        msg_out1 = self.dct_extract(img_stego_jpg, len_msg, 20200417)
        msg_out2 = self.dct_extract(img_stego_png, len_msg, 20200417)

        print('嵌入的信息为：', msg)
        print('提取的信息1为：', msg_out1)
        print('提取的信息2为：', msg_out2)
        print(img_marked.shape, type(img_marked), type(img_marked[0, 0]))

        self.save_img(img_gray, 'Grayscale Image', 'original.' + self.format)
        if self.format == 'jpg':
            self.save_img(img_stego_jpg, 'Embed Image', 'embed.jpg')
        elif self.format == 'png':
            self.save_img(img_stego_png, 'Embed Image', 'embed.png')
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
