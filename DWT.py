import cv2
import pywt
import numpy as np
import matplotlib.pyplot as plt
import random


# 使用dwt算法处理图像嵌入
class DWT:
    # jpg图像位置
    monarch_lsb_jpg = './embed/monarch_lsb.jpg'
    # png图像位置
    monarch_lsb_png = './embed/monarch_lsb.png'
    # 水印图像位置
    watermark_path = ''
    # 输出的图像格式
    format = ''

    def __init__(self, w, f):
        self.format = f
        self.watermark_path = w

    @staticmethod
    def dwt_embed(img_gray, img_watermark):
        if len(img_gray.shape) > 2 or len(img_watermark.shape) > 2:
            print("Parameter img should be of grayscale")
            return img_gray

        # Step 1: DWT in level 2 Haar coefficients ch_l2 and cv_l2
        ca_l1, (ch_l1, cv_l1, cd_l1) = pywt.dwt2(img_gray.astype(np.float32), 'haar')
        ca_l2, (ch_l2, cv_l2, cd_l2) = pywt.dwt2(ca_l1, 'haar')

        # Step 2: Embed
        height, width = img_gray.shape
        img_watermark = cv2.resize(img_watermark, (width >> 2, height >> 2))
        img_watermark = img_watermark.astype(np.float32)

        # change 0 to -1
        # img_watermark[img_watermark<1] = -1
        alpha = 3  # The strength of watermark
        ch_l2 = alpha * img_watermark
        cv_l2 = alpha * img_watermark

        # Step 3: IDWT
        ca_l1 = pywt.idwt2((ca_l2, (ch_l2, cv_l2, cd_l2)), 'haar')
        img_marked = pywt.idwt2((ca_l1, (ch_l1, cv_l1, cd_l1)), 'haar')

        return img_marked.astype(np.uint8)

    @staticmethod
    def dwt_extract(img_marked, img_watermark):
        if len(img_marked.shape) > 2:
            print("Parameter img should be of grayscale")
            return img_marked

        # Step 1: DWT in level 2 Haar coefficients ch_l2 and cv_l2
        ca_l1, (ch_l1, cv_l1, cd_l1) = pywt.dwt2(img_marked.astype(np.float32), 'haar')
        ca_l2, (ch_l2, cv_l2, cd_l2) = pywt.dwt2(ca_l1, 'haar')

        # Step 2: Extract
        height, width = img_marked.shape
        img_watermark = cv2.resize(img_watermark, (width >> 2, height >> 2))
        img_watermark = img_watermark.astype(np.float32)
        # img_watermark[img_watermark<1] = -1
        alpha = 3
        img_watermark_extracted = ch_l2 * img_watermark + cv_l2 * img_watermark
        img_watermark_extracted = 255 * img_watermark_extracted / np.max(img_watermark_extracted)
        img_watermark_extracted[img_watermark_extracted < alpha] = 0
        img_watermark_extracted[img_watermark_extracted >= alpha] = 255
        return img_watermark_extracted.astype(np.uint8)

    def process(self, img_file, watermark_file):
        img_gray = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)

        img_watermark = cv2.imread(watermark_file, cv2.IMREAD_GRAYSCALE)
        _, img_watermark = cv2.threshold(img_watermark, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_marked = self.dwt_embed(img_gray, img_watermark)

        cv2.imwrite('./embed/monarch_lsb.' + self.format, img_marked)

        # print(img_marked.shape, type(img_marked), type(img_marked[0,0]))
        img_stego = cv2.imread('./embed/monarch_lsb.' + self.format, cv2.IMREAD_GRAYSCALE)
        img_watermark = cv2.imread(watermark_file, cv2.IMREAD_GRAYSCALE)
        _, img_watermark = cv2.threshold(img_watermark, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img_watermark_extracted = self.dwt_extract(img_stego, img_watermark)

        self.save_img(img_gray, 'Grayscale Image', 'original.' + self.format)
        self.save_img(img_marked, 'Embed Image', 'embed.' + self.format)
        self.save_img(img_watermark, 'Watermark', 'watermark.' + self.format)
        self.save_img(img_watermark_extracted, 'Watermark Extracted', 'watermark_extracted.' + self.format, 'hot')

    @staticmethod
    def save_img(img, title, save_name, cmap='gray'):
        plt.figure(0)
        plt.subplot(111)
        plt.imshow(img, cmap)
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('./embed/' + save_name)
        plt.close(0)
