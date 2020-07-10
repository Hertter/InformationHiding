from flask import Flask
from flask import render_template
from flask import request, jsonify, make_response
from Embed import Embed

import base64
import os
import flask

app = Flask(__name__)


# 返回base64编码
def return_base64():
    head = 'data:image/jpeg;base64,'
    with open('./embed/original.jpg', 'rb') as file:
        # 图像的base64编码
        base64_data = base64.b64encode(file.read())
        # 获取编码
        base64_data1 = head + base64_data.decode()
    with open('./embed/embed.jpg', 'rb') as file:
        # 图像的base64编码
        base64_data = base64.b64encode(file.read())
        # 获取编码
        base64_data2 = head + base64_data.decode()
    return base64_data1, base64_data2


# 保存图片
def save_image(image):
    # 保存文件的目录
    file_path = r'./embed/'
    # 图片的名字
    file_name = image.filename
    if image:
        # 地址拼接
        file_paths = os.path.join(file_path, file_name)
        # 保存文件
        image.save(file_paths)
        # 返回数据
        return file_paths


@app.route('/lsb/embed', methods=['post'])
def embed():
    print(flask.request.values)
    # 文字
    text = flask.request.values.get('text')
    # 图像
    image = request.files['image']
    # 长度
    length = flask.request.values.get('length')
    # 格式
    format = flask.request.values.get('format')

    print('text:', text)
    print('image:', image)
    print('length:', length)
    print('format:', format)

    # 保存图片
    image_path = save_image(image)
    # 图片处理
    image_process = Embed(text, format, int(length))
    msg_out1, msg_out2 = image_process.process(image_path)
    # 获取base64编码
    image_base64_1, image_base64_2 = return_base64()
    # json结果
    result = {}
    # 判断格式
    if format == 'jpg':
        result = {
            'msg_out': msg_out1,
            'image_base64_1': image_base64_1,
            'image_base64_2': image_base64_2
        }
    elif format == 'png':
        result = {
            'msg_out': msg_out2,
            'image_base64_1': image_base64_1,
            'image_base64_2': image_base64_2
        }
    # 处理跨域问题
    json_data = jsonify(result)
    res = make_response(json_data)
    res.headers['Access-Control-Allow-Origin'] = '*'
    # 返回json数据
    return res


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()