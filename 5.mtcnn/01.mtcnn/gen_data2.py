import os
from PIL import Image, ImageFilter
import numpy as np
from tool import utils
import traceback
import random


anno_src = r"D:\celeba_1w.txt"
img_dir = r"D:\celeba_1w"


def gen_sample(save_path, face_size, stop_value):
    print("gen size:{} image".format(face_size))
    # 样本图片存储路径
    positive_image_dir = os.path.join(save_path, str(face_size), "positive")
    negative_image_dir = os.path.join(save_path, str(face_size), "negative")
    part_image_dir = os.path.join(save_path, str(face_size), "part")

    # 造出三种路径下的9个文件夹，// 12,24,48
    for dir_path in [positive_image_dir, negative_image_dir, part_image_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # 样本标签存储路径
    positive_anno_filename = os.path.join(save_path, str(face_size), "positive.txt")
    negative_anno_filename = os.path.join(save_path, str(face_size), "negative.txt")
    part_anno_filename = os.path.join(save_path, str(face_size), "part.txt")

    # 样本的统计数
    positive_count = 0
    negative_count = 0
    part_count = 0

    try:
        positive_anno_file = open(positive_anno_filename, "w")
        negative_anno_file = open(negative_anno_filename, "w")
        part_anno_file = open(part_anno_filename, "w")

        for i, line in enumerate(open(anno_src)):
            if i < 2:
                continue
            try:
                # 切割非空值元素
                strs = line.split()
                # print(strs)

                image_filename = strs[0].strip()
                print(image_filename)
                image_file = os.path.join(img_dir, image_filename)

                with Image.open(image_file) as img:
                    img_w, img_h = img.size
                    x1 = float(strs[1].strip())
                    y1 = float(strs[2].strip())
                    w = float(strs[3].strip())
                    h = float(strs[4].strip())

                    # 如果坐标或边长为负数，或者人脸框面积和最大边长正方形面积比(IOU)低于0.7(无法生成正样本)，则丢弃
                    if x1 < 0 or y1 < 0 or w < 0 or h < 0 or (w * h) / (max(w, h) * max(w, h)) <= 0.7:
                        # if x1 < 0 or y1 < 0 or w < 0 or h < 0 or (min(w,h)*min(w,h)) / (w*h) <= 0.7:
                        continue

                    x2 = float(x1 + w)
                    y2 = float(y1 + h)

                    px1 = 0  # float(strs[5].strip())
                    py1 = 0  # float(strs[6].strip())
                    px2 = 0  # float(strs[7].strip())
                    py2 = 0  # float(strs[8].strip())
                    px3 = 0  # float(strs[9].strip())
                    py3 = 0  # float(strs[10].strip())
                    px4 = 0  # float(strs[11].strip())
                    py4 = 0  # float(strs[12].strip())
                    px5 = 0  # float(strs[13].strip())
                    py5 = 0  # float(strs[14].strip())

                    boxes = [[x1, y1, x2, y2]]

                    # 计算出人脸中心点位置
                    cx = x1 + w / 2
                    cy = y1 + h / 2

                    side_len = random.choice([w, h])  # 随机选一个边，（正方形）

                    # 一张图片生成的样本统计数
                    single_img_pos = 0
                    single_img_part = 0
                    single_img_neg = 0
                    while True:

                        if single_img_pos < 3:
                            _side_len = side_len + side_len * random.uniform(-0.2, 0.2) + 1
                            _cx = cx + cx * random.uniform(-0.2, 0.2) + 1
                            _cy = cy + cy * random.uniform(-0.2, 0.2) + 1

                        elif single_img_part < 3:
                            _side_len = side_len + side_len * random.uniform(-1, 1) + 1
                            _cx = cx + cx * random.uniform(-1, 1) + 1
                            _cy = cy + cy * random.uniform(-1, 1) + 1

                        elif single_img_neg < 9:
                            _side_len = side_len + side_len * random.uniform(-2, 2) + 1
                            _cx = cx + cx * random.uniform(-2, 2) + 1
                            _cy = cy + cy * random.uniform(-2, 2) + 1

                        _x1 = _cx - _side_len / 2  # 偏移后的中心点换算回偏移后起始点X,Y
                        _y1 = _cy - _side_len / 2
                        _x2 = _x1 + _side_len  # 获得偏移后的X2,Y2
                        _y2 = _y1 + _side_len
                        # 偏移后的的坐标点对应的是正方形
                        # 判断偏移超出整张图片的就跳过,不截图
                        if _x1 < 0 or _y1 < 0 or _x2 > img_w or _y2 > img_h or _side_len < face_size:
                            continue

                        offset_x1 = (x1 - _x1) / _side_len  # 获得换算后的偏移率
                        offset_y1 = (y1 - _y1) / _side_len
                        offset_x2 = (x2 - _x2) / _side_len
                        offset_y2 = (y2 - _y2) / _side_len

                        offset_px1 = 0  # (px1 - x1_) / side_len
                        offset_py1 = 0  # (py1 - y1_) / side_len
                        offset_px2 = 0  # (px2 - x1_) / side_len
                        offset_py2 = 0  # (py2 - y1_) / side_len
                        offset_px3 = 0  # (px3 - x1_) / side_len
                        offset_py3 = 0  # (py3 - y1_) / side_len
                        offset_px4 = 0  # (px4 - x1_) / side_len
                        offset_py4 = 0  # (py4 - y1_) / side_len
                        offset_px5 = 0  # (px5 - x1_) / side_len
                        offset_py5 = 0  # (py5 - y1_) / side_len

                        # 剪切下图片，并进行大小缩放
                        crop_box = [_x1, _y1, _x2, _y2]  # 获得需要截取图片样本的坐标
                        face_crop = img.crop(crop_box)
                        face_resize = face_crop.resize((face_size, face_size))

                        iou = utils.iou(crop_box, np.array(boxes))[0]

                        if iou > 0.7 and single_img_pos < 3:  # 正样本
                            positive_anno_file.write(
                                "positive/{0}.jpg {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15}\n".format(
                                    positive_count, 1, offset_x1, offset_y1,
                                    offset_x2, offset_y2, offset_px1, offset_py1, offset_px2, offset_py2, offset_px3,
                                    offset_py3, offset_px4, offset_py4, offset_px5, offset_py5))
                            positive_anno_file.flush()
                            face_resize.save(os.path.join(positive_image_dir, "{0}.jpg".format(positive_count)))
                            single_img_pos += 1
                            positive_count += 1

                        elif 0.7 > iou > 0.3 and single_img_part < 3:  # 部分样本
                            part_anno_file.write(
                                "part/{0}.jpg {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14} {15}\n".format(
                                    part_count, 2, offset_x1, offset_y1, offset_x2,
                                    offset_y2, offset_px1, offset_py1, offset_px2, offset_py2, offset_px3,
                                    offset_py3, offset_px4, offset_py4, offset_px5, offset_py5))
                            part_anno_file.flush()
                            face_resize.save(os.path.join(part_image_dir, "{0}.jpg".format(part_count)))
                            single_img_part += 1
                            part_count += 1

                        elif iou < 0.1 and single_img_neg < 9:  # 负样本
                            negative_anno_file.write(
                                "negative/{0}.jpg {1} 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n".format(negative_count, 0))
                            negative_anno_file.flush()
                            face_resize.save(os.path.join(negative_image_dir, "{0}.jpg".format(negative_count)))
                            single_img_neg += 1
                            negative_count += 1

                        # 统计每张图片被生成各类样本的次数,当一张原始图像按照3:3:9的比例生成的数量达到15张时，换下一张图像
                        if single_img_pos + single_img_part + single_img_neg >= 15:
                            break

                # 统计总样本数
                count = positive_count + part_count + negative_count
                # 判断总样本数据是否到要求
                if count >= stop_value:
                    break

            except:
                traceback.print_exc()
    except:
        traceback.print_exc()

    # finally:
    #     positive_anno_file.close()
    #     negative_anno_file.close()
    #     part_anno_file.close()


if __name__ == '__main__':
    # save_path = r"E:\datasets\train"
    # save_path = r"E:\datasets\validate"
    save_path = r"D:\test"
    gen_sample(save_path, 12, 3000)
    gen_sample(save_path, 24, 3000)
    gen_sample(save_path, 48, 3000)
