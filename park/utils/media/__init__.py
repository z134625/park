__doc__ = """
媒体数据处理模块
ImageData = (
    'save_data',: 保存numpy 数据的图片必须为三维必填参数data_， 可选参数path下载文件路径,
                                                class_ 文件后缀名默认jpg,
                                                pathName 文件完整路径需提供名
    'resize', : 改变像素
    'MP4_OR_PHOTO', ： mp4 文件转换成图片配置文件save_video=True 将保存 返回一个生成器
    'Mp4Write', ：mp4文件处理 
    'photo_Pretreatment', ：图片预处理
    'imresize' ：改变像素
)

"""

from collections.abc import Generator
from park.utils.numpys.tools import Ndarray
from park.conf.os import (
    BASE_PATH,
    join,
    isAbs,
    getSize,
)
from park.conf.setting import ProgressPark, install_module

if __name__ == "park.utils.media":
    if install_module("cv2", "opencv-python~=4.6.0.66") != 0:
        raise SystemError("模块opencv-python下载失败")
    if install_module("PIL", "pillow~=9.1.1") != 0:
        raise SystemError("模块pillow下载失败")
    if install_module("skimage", "scikit-image~=0.19.3") != 0:
        raise SystemError("模块scikit-image下载失败")

from .tools import video_photo, resize, join_features, cv2


class Mp4Write:

    def __init__(self, file, fps: int = 2, out_video_name: str = "Park"):
        self.name = out_video_name
        if isAbs(file):
            path = file
        else:
            path = join(BASE_PATH, file)
        mp4 = cv2.VideoCapture(path)
        self.size = getSize(file)
        self.weight = mp4.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = mp4.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = mp4.get(cv2.CAP_PROP_FPS)
        self.fps_total = mp4.get(cv2.CAP_PROP_FRAME_COUNT)
        self.photo_generator = video_photo(mp4=mp4, num=fps)
        self.fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')
        self.video_data = []
        self.select = self.video_data.append

    def self_adaption(self, size: tuple) -> Generator:
        """自适应模型宽高"""
        for item in self.photo_generator:
            data = resize(item, size)
            yield data, item

    def recovery(self, data: Ndarray) -> Ndarray:
        """恢复视频原始宽高"""
        return resize(data, (int(self.height), int(self.weight)))

    @staticmethod
    def write_features(data: Ndarray, features: Ndarray) -> Ndarray:
        """将特征写入到图片中"""
        return join_features(data, features)

    def collect(self, data: Ndarray) -> None:
        self.select(data)
        return

    def merge(self) -> None:
        """将每张ndarray数据合并为一视频"""
        video = cv2.VideoWriter(self.name, self.fourcc, self.fps / 2, (int(self.weight), int(self.height)))
        with ProgressPark(len(self.video_data)) as park:
            for i, item in enumerate(self.video_data):
                park()
                video.write(item)
            video.release()
        return


__all__ = (
    'Mp4Write',
)
