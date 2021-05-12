# coding:utf-8
import os
import time
from multiprocessing import Pool
# 可配置的进程池大小、数据字段列表、小文件拆分行数标准
from conf.config_multiprocess import PROCESS_POOL, INSERT_MANY_COUNT, COLUMNS, SPLIT_LINES, SPLIT_FLAG
# 自定义的MongoDB连接类
from mongo_client import DBManager


class BigFileToMongoDB(object):
    # 初始化指定大文件路径及拆分结果目录，默认拆分至当前路径下的split_directory文件夹下
    def __init__(self, filepath, splitpath="./split_directory"):
        self.filepath = filepath
        self.splitpath = splitpath

    # 将大型文件转换为生成器，每次返回一行数据
    def __gen_file(self):
        """将大型文件转化为生成器对象，每次返回一行"""
        with open(self.filepath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                yield line

    def __mk_sp_dir(self):
        """创建拆分文件存放目录，split_directory"""
        if not os.path.exists(self.splitpath):
            os.mkdir(self.splitpath)

    # 将大文件按指定行数切分为多个小文件
    def split_file(self, sp_nm=1000000):
        """读取大文件生成器，默认每100w行拆分一个新的文件写入"""
        if SPLIT_LINES is not None:
            sp_nm = SPLIT_LINES

        (filepath, tempfilename) = os.path.split(self.filepath)
        print(tempfilename)
        # (my_filename, my_extension) = os.path.splitext(tempfilename)
        base_path = tempfilename.replace(".", "_{}.")
        gen = self.__gen_file()
        self.__mk_sp_dir()
        flag = 1
        while True:
            split_name = base_path.format(str(flag))
            try:
                with open("%s/%s" % (self.splitpath, split_name), "w", encoding="utf8") as f:
                    for i in range(sp_nm):
                        line = next(gen)
                        f.write(line)
                flag += 1
            except StopIteration:
                break
        print("Finished! Split into %s files in total." % flag)

    @staticmethod
    def spfile_generator(sp_filepath):
        """将拆分后的文件转换为字典生成器
        针对不同格式文件需要不同的处理函数
        """
        with open(sp_filepath, "r", encoding="utf-8") as f:
            while True:
                line = f.readline()
                line = str(line).replace("\n", "")
                line_list = line.split(SPLIT_FLAG)
                # line_list = line.split(";")[:-1]
                # print(line_list)
                dic = {i: j for i, j in zip(COLUMNS, line_list)}
                if not line:
                    break
                yield dic

    @property
    def sp_file_lists(self):
        """获取所有拆分文件绝对路径列表"""
        abspath = os.path.abspath(self.splitpath) + "/"
        sp_filepath_list = list(map(lambda x: abspath + x, os.listdir(self.splitpath)))
        return sp_filepath_list

    @staticmethod
    def insert_mongo(filepath):
        sp_gen = BigFileToMongoDB.spfile_generator(filepath)
        db = DBManager()
        coll = db.get_collection("test_coll")

        while True:
            docs = []
            try:
                # update_one 方法 使用upsert参数，方便替换和添加
                # for i in range(INSERT_MANY_COUNT):
                #     doc = next(sp_gen)
                #     temp_result = coll.update_one(filter={"phonenumber": int(doc["phonenumber"])},
                #                                   update={"$set": {"qq": int(doc["qq"])}},
                #                                   upsert=True)
                # insert_many方法，直接批量插入使用
                for i in range(INSERT_MANY_COUNT):
                    doc = next(sp_gen)
                    docs.append(doc)
                coll.insert_many(docs)
            except StopIteration:
                break
        print("生成器元素已写入MongoDB")

    def clean_split_dir(self):
        for split_file in self.sp_file_lists:
            os.remove(split_file)
        print("清理完成")


def run_insert_pool(file_path):
    start = time.time()
    handler = BigFileToMongoDB(file_path)
    print("开始切分源文件")
    handler.split_file()
    sp_filepath_list = handler.sp_file_lists
    p = Pool(PROCESS_POOL)
    for file in sp_filepath_list:
        p.apply_async(handler.insert_mongo, (file,))

    print("----start----")
    p.close()
    p.join()
    end = time.time()
    print("Finish to MongoDB spend:{}s".format(end - start))
    handler.clean_split_dir()


if __name__ == '__main__':
    file_path = "E:\megadownload\QBang_F_8e_1105更新\总库0.txt"
    # filename = "F:\mega_download\QBang_F_8e_1105更新\QBang_F_8e_1105更新\QBang_F_8e\总库0.txt"
    run_insert_pool(file_path)
