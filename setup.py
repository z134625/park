from setuptools import setup, find_packages

setup(
    name="Park",
    version="2.0.0",
    author="ZLY-PARK",
    author_email="584934293@qq.com",
    packages=find_packages(),
    install_requires=["numpy~=1.22.4", "pynvml~=11.4.1", "openpyxl~=3.0.10", "httpx~=0.23.0", "pymysql~=1.0.2",
                      "requests~=2.28.0", "websockets~=10.3", "psutil~=5.9.1"],
    extras_require={
        "pytorch": ["torch>=1.9.0", "torch"],
        "tensorflow": ["tensorflow>=2.6.2", "tensorflow"],
        "nvidia-ml-py": ["nvidia-ml-py~=11.515.48", "nvidia-ml-py"],
        "scikit-image": ["scikit-image~=0.19.3", "scikit-image"],
        "pillow": ["pillow~=9.1.1", "pillow"],
        "xlrd": ["xlrd==2.0.1", "xlrd"],
        "xlwt": ["xlwt~=1.3.0", "xlwt"],
        "opencv-python": ["opencv-python~=4.6.0.66",  "opencv-python"],
    },
    python_require='>=3.10',
)
