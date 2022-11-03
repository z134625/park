import subprocess
import os

import imageio
from io import BytesIO

from PIL import Image
from ..tools import ParkLY, Paras, monitor, get_size


class ImageParas(Paras):

    @staticmethod
    def init():
        _attrs = {
            'message': {},
            '_return': False,
            '_clearSize': 5000,
        }
        _clear = True
        return locals()


class ImageApp(ParkLY):
    _name = 'image'
    _inherit = 'monitor'
    paras = ImageParas()

    def clear(self):
        if self._return > self._clearSize:
            self.message.clear()

    @monitor('clear')
    def note(self):
        info = self._return
        if self._funcName in self.message:
            self.message[self._funcName].append(info)
        else:
            self.message[self._funcName] = [info]
        return get_size(self.message)

    @monitor('note')
    def video2mp3(self, file_name):
        outfile_name = file_name.split('.')[0] + '.mp3'
        try:
            subprocess.call('ffmpeg -i ' + file_name
                            + ' -f mp3 ' + outfile_name, shell=True)
            msg = 'success'
        except Exception as e:
            msg = e
        return msg

    @monitor('note')
    def video_add_mp3(self, file_name, mp3_file):
        """
         视频添加音频
        :param file_name: 传入视频文件的路径
        :param mp3_file: 传入音频文件的路径
        :return:
        """
        outfile_name = file_name.split('.')[0] + '-txt.mp4'
        try:
            subprocess.call('ffmpeg -i ' + file_name
                            + ' -i ' + mp3_file + ' -strict -2 -f mp4 '
                            + outfile_name, shell=True)
            msg = 'success'
        except Exception as e:
            msg = e
        return msg

    @monitor('note')
    def compose_gif(self, file_path):
        """
         将静态图片转为gif动图
         :param file_path: 传入图片的目录的路径
         :return:
        """
        try:
            img_paths = sorted([int(p[3:-4]) for p in os.listdir(file_path) if os.path.splitext(p)[1] == ".gif"])
            img_paths = img_paths[:int(len(img_paths) / 3.6)]
            gif_images = []
            for path in img_paths:
                gif_images.append(imageio.imread('{0}/out{1}.png'.format(file_path, path)))
            imageio.mimsave("test.gif", gif_images, fps=30)
            msg = 'success'
        except Exception as e:
            msg = e
        return msg

    @monitor('note')
    def compress_png(self, file_path):
        """
         将gif动图转为每张静态图片
         :param file_path: 传入gif文件的路径
         :return:
        """
        img_paths = [p for p in os.listdir(file_path) if os.path.splitext(p)[1] == ".png"]
        try:
            for filename in img_paths:
                with Image.open('{0}/{1}'.format(file_path, filename)) as im:
                    width, height = im.size
                    new_width = 150
                    new_height = int(new_width * height * 1.0 / width)
                    resized_im = im.resize((new_width, new_height))
                    output_filename = filename
                    resized_im.save('{0}/{1}'.format(file_path, output_filename))
            msg = 'success'
        except Exception as e:
            msg = e
        return msg

    def __del__(self):
        self.message.clear()
