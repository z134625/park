import logging
import uuid
from typing import Union, Tuple

from collections.abc import Generator

from park.utils.numpys.tools import Ndarray, array_data
from park.utils.data import DataInfo
from park.conf import Error
from park.conf.os import (
    BASE_PATH,
    join,
    isExists,
    mkdir,
    listPath,
    base,
    isType,
    splitPath,
)


Image = __import__("PIL.Image").Image
cv2 = __import__("cv2")
skimage = __import__("skimage.transform")


def video_photo(mp4, num: int = None, fps: int = 20, is_save: bool = False) -> Generator:
    """
    
    :param mp4:
    :param num:
    :param fps:
    :param is_save:
    :return:
    """
    c = 0

    n: int = fps
    if num:
        n = num
    if mp4.isOpened():
        res, frame = mp4.read()
    else:
        res = False
    while res:
        res, frame = mp4.read()
        if c % n == 0 and res:
            if is_save:
                logging.debug("当前选择下载缓存视频图片")
                path = join(BASE_PATH, 'cache/cv2/mp4/')
                if not isExists(path):
                    mkdir(path)
                try:
                    cv2.imwrite(join(path, f"{str(uuid.uuid4())}.jpg"), frame)
                except Exception as e:
                    logging.error(f"图像保存失败({e})")
                    continue
            yield frame
        c += 1


def join_features(data: Ndarray, features: Ndarray) -> Ndarray:
    return data + features


def save_data(data_, **kwargs) -> str:
    """对矩阵数据转换为图片"""
    path: Union[None, str] = kwargs.get('path', None)
    layout: str = kwargs.get("class_", "jpg")
    path_to = join(path,
                   f'{uuid.uuid4()}.'
                   f'{layout}')
    name = kwargs.get("pathName", None)
    if name:
        path_to = name
    if path_to:
        logging.debug("当前下载数据图片")
        mkdir(path)
        if not isinstance(data_, Ndarray):
            data_: Ndarray = array_data(data_)
        cv2.imwrite(path_to, data_)
        return path_to
    else:
        raise Error.DataPathError("路径未提供将无法执行命令")


def resize(frame: Ndarray, size: tuple) -> Ndarray:
    """改变图片像素"""
    return skimage.transform.resize(frame, size)


def photo_pretreatment(path: str, is_save: bool = False, class_: str = None, threshold: int = 200,
                       Grayscale: bool = False, Binary: bool = False, save_path: str = './',
                       lambda_=None) -> Union[Generator]:
    """
    图片预处理模块，支持灰度处理二值化处理，依赖于pillow模块，
    :param path: 预处理图片路径可以是文件路径也可是文件夹路径
    :param is_save:  是否保存预处理图片
    :param class_:  保存图片的后缀默认为继承图片后缀
    :param threshold:  二值化阈值默认200
    :param Grayscale: 是否灰度处理
    :param Binary:  是否二值化处理
    :param save_path:  若保存，保存路径位置，默认当前工作路径
    :param lambda_:  增加一个方法函数筛选需要处理的图片
    :return: 一个处理后图片的numpy数据的生成器
    实例：
    for i in photo_pretreatment(path="./img", is_save=True, class_='png', lambda_=lambda x: 'photo' in x):
        print(i)
    此操作类似与复制图片改变其后缀为png， 且只复制文件名包含photo的图片
    """
    threshold: int = threshold

    def pretreatment(image):
        if Grayscale:
            image = image.convert('L')
            if is_save:
                image.save(join(save_path, f'gray-{nm}.{suffix}'))
        if Binary:
            table = []
            for i in range(256):
                if i < threshold:
                    table.append(0)
                else:
                    table.append(1)
            image = image.point(table, '1')
            if is_save:
                image.save(join(save_path, f'binary-{nm}.{suffix}'))
        return image
    if is_save:
        if not isExists(save_path):
            mkdir(save_path)
    if isType(path):
        files = listPath(path)
        if lambda_:
            files = filter(lambda_, files)
        for file in files:
            nm, suffix = splitPath(file)
            if class_:
                suffix = class_
            if isType(join(path, file), form="doc") and 'jpg' in file:
                Lim = Image.open(join(path, file))
                Lim = pretreatment(Lim)
                yield DataInfo(Lim, file=join(path, file))

    elif isType(path, form="doc"):
        name = base(path)
        nm, suffix = splitPath(name)
        if class_:
            suffix = class_
        Lim = Image.open(path)
        Lim = pretreatment(Lim)
        yield DataInfo(Lim, file=path)
    else:
        raise Error.DataPathError("提供的路径错误，请检查")


def code(size: Tuple[int, int] = (128, 64),
         mode: str = 'RGB',
         bg_color: Tuple[int, int, int] = (255, 255, 255),
         draw_lines=True,
         draw_points=True,
         n_line=(1, 2),
         font_size: int = 28,
         font_type: str = "STLITI.TTF",
         fg_color: Tuple[int, int, int] = (0, 0, 255),
         point_chance: int = 1,
         **kwargs) -> Tuple[Image.Image, str]:
    """
    :param size: 生成图片大小默认 160，80 必须为元组形式
    :param mode: 图像颜色通道
    :param bg_color: 生成图片背景图颜色默认白色
    :param draw_lines: 是否画干扰线
    :param draw_points:  是否画干扰点
    :param n_line: 干扰线数量范围
    :param font_size: 字体大小
    :param font_type: 字体类型
    :param fg_color: 字体颜色
    :param point_chance: 干扰点出现概率0 - 100
    :param kwargs: 增加 is_case 是否开启大小写默认False length 验证码长度  验证码类型： （operation， number， letter， blend）
    默认为blend 字母与数字结合， operation 为公式只出现 + - *并在十以内的算数， number 为数字形式 letter 只有字母， custom 为自定义模式，
    需要传入words={'a': 1} 字典类型key为验证码， value为核验值
    :return: 图像Image 类型， result 验证标准
    使用实例：
    image, result = code()
    OSError: cannot open resource 此类错误应更换font_type
    image, result = code(font_type="")
    """
    from ._random_code import Code
    from PIL import ImageDraw, ImageFilter, ImageFont
    import random
    generator = Code(**kwargs)
    image, result = generator.generator()
    # 宽和高
    width, height = size
    # 创建图形
    img = Image.new(mode, size, bg_color)
    # 创建画笔
    draw = ImageDraw.Draw(img)

    def create_line() -> None:
        """绘制干扰线条"""
        # 干扰线条数
        line_num = random.randint(*n_line)
        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            # 结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points() -> None:
        """绘制干扰点"""
        # 大小限制在[0, 100]
        chance = min(100, max(0, int(point_chance)))
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs() -> None:
        """绘制验证码字符"""
        # 每个字符前后以空格隔开
        strs = ' %s ' % image
        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 3, (height - font_height) / 3),
                  strs, font=font, fill=fg_color)

    if draw_lines:
        create_line()
    if draw_points:
        create_points()
    create_strs()
    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    # 创建扭曲
    img = img.transform(size, Image.PERSPECTIVE, params)
    # 滤镜，边界加强（阈值更大）
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, result


__all__ = (
    'save_data',
    'resize',
    'video_photo',
    'photo_pretreatment',
    'join_features',
    'code',
)
