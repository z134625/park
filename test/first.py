from park.conf.setting import Cache, make_dir_or_doc, setting


if __name__ == '__main__':
    # Cache(class_=["D:/Desktop/test/ParkTorch/build", "D:/Desktop/test/ParkTorch/Park.egg-info"], all_=True)
    # cache = Cache(class_=None, ignore_warning=False, name=["q12", "dee"])
    # print(cache.error)
    # path = 'D:/Desktop/parks2'
    # make_dir_or_doc(path, suffix='xls')
    # f = open(path, 'w')
    # f.close()
    setting.load('D:/Desktop/test/ParkTorch/park/conf/_Global_setting.py')
    print(setting.DATABASE_POOL)
