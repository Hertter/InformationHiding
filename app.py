from pathlib import Path

from flask import Flask
from flask import render_template
from flask import request, jsonify, make_response

from DCT import DCT
from DWT import DWT
from LSB import LSB
from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity

import base64
import os
import flask
import cv2

app = Flask(__name__)


# 获取图像的psnr和ssim
def get_image_quality(format, image_path):
    gray_image = cv2.imread('./embed/' + image_path, cv2.IMREAD_GRAYSCALE)
    print('./embed/' + image_path)
    print('./embed/' + os.path.splitext(image_path)[0] + '.' + format)
    embed_image = cv2.imread('./embed/monarch_lsb.' + format, cv2.IMREAD_GRAYSCALE)

    psnr = peak_signal_noise_ratio(gray_image, embed_image)
    psnr = '{:.4f}'.format(psnr)
    ssim = structural_similarity(gray_image, embed_image)
    ssim = '{:.8f}'.format(ssim)
    print('psnr: ', psnr)
    print('ssim: ', ssim)
    return psnr, ssim


# 删除本地图像
def delete_local_image(filepath):
    del_list = os.listdir(filepath)
    for file in del_list:
        file_path = os.path.join(filepath, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# 读取文件同时获取base64编码
def open_file_and_get_base64(path):
    with open(path, 'rb') as file:
        # 图像的base64编码
        base64_data = base64.b64encode(file.read())
        # 获取编码
        data = head + base64_data.decode()
    return data


# 返回base64编码
def return_base64(format):
    global head, base64_data1, base64_data2, base64_data3, base64_data4
    if format == "jpg":
        head = 'data:image/jpeg;base64,'
    elif format == "png":
        head = 'data:image/png;base64,'

    base64_data1 = ''
    base64_data2 = ''
    base64_data3 = ''
    base64_data4 = ''

    if Path('./embed/original.' + format).exists():
        base64_data1 = open_file_and_get_base64('./embed/original.' + format)
    if Path('./embed/embed.' + format).exists():
        base64_data2 = open_file_and_get_base64('./embed/embed.' + format)
    if Path('./embed/watermark_extracted.' + format).exists():
        base64_data3 = open_file_and_get_base64('./embed/watermark.' + format)
    if Path('./embed/watermark.' + format).exists():
        base64_data4 = open_file_and_get_base64('./embed/watermark_extracted.' + format)
    return base64_data1, base64_data2, base64_data3, base64_data4


# 保存图片
def save_image(image, file_name):
    save_path = Path("./embed")
    if not save_path.exists():
        os.mkdir("embed")
    # 保存文件的目录
    file_path = r'./embed/'
    if image:
        # 地址拼接
        file_paths = os.path.join(file_path, file_name)
        # 保存文件
        image.save(file_paths)
        # 返回数据
        return file_paths


def main_function(api):
    global msg_out1, msg_out2, watermark, length, text
    print(flask.request.values)
    print(request.files)
    if api == 'lsb' or api == 'dct':
        # 文字
        text = flask.request.values.get('text')
        # 长度
        length = flask.request.values.get('length')
        print('text:', text)
        print('length:', length)
    elif api == 'dwt':
        # 水印图
        watermark = request.files['watermark']
        print('watermark:', watermark)
    # 图像
    image = request.files['image']
    # 格式
    format = flask.request.values.get('format')

    print('image:', image)
    print('format:', format)

    # 保存图片
    image_path = save_image(image, image.filename)
    # 图片处理
    image_process = None
    if api == 'lsb':
        image_process = LSB(text, format, int(length))
        msg_out1, msg_out2 = image_process.process(image_path)
    elif api == 'dct':
        image_process = DCT(text, format, int(length))
        msg_out1, msg_out2 = image_process.process(image_path)
    elif api == 'dwt':
        # 保存水印图片
        watermark_path = save_image(watermark, 'monarch_lsb.' + os.path.splitext(watermark.filename)[1])
        image_process = DWT(watermark_path, format)
        image_process.process(image_path, watermark_path)
    # 获取base64编码
    image_base64_1, image_base64_2, image_base64_3, image_base64_4 = return_base64(format)
    # 获取图像质量
    psnr, ssim = get_image_quality(format, image.filename)
    # json结果
    result = {}
    # 判断格式
    if api == 'lsb' or api == 'dct':
        if format == 'jpg':
            result = {
                'msg_out': msg_out1,
                'image_base64_1': image_base64_1,
                'image_base64_2': image_base64_2,
                'psnr': psnr,
                'ssim': ssim
            }
        elif format == 'png':
            result = {
                'msg_out': msg_out2,
                'image_base64_1': image_base64_1,
                'image_base64_2': image_base64_2,
                'psnr': psnr,
                'ssim': ssim
            }
    elif api == 'dwt':
        result = {
            'image_base64_1': image_base64_1,
            'image_base64_2': image_base64_2,
            'image_base64_3': image_base64_3,
            'image_base64_4': image_base64_4,
            'psnr': psnr,
            'ssim': ssim
        }
    # 处理跨域问题
    json_data = jsonify(result)
    res = make_response(json_data)
    res.headers['Access-Control-Allow-Origin'] = '*'
    # 删除本地图片
    delete_local_image('./embed')
    # 返回json数据
    return res


@app.route('/lsb/embed', methods=['post'])
def lsb():
    return main_function('lsb')


@app.route('/dct/embed', methods=['post'])
def dct():
    return main_function('dct')


@app.route('/dwt/embed', methods=['post'])
def dwt():
    return main_function('dwt')


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
