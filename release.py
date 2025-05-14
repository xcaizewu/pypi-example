# -*- coding: utf-8 -*-
# cython: skip

import argparse
import glob
import re
import shutil
import os
from distutils.core import setup
from multiprocessing import Process
from pathlib import Path
from typing import Iterable
from Cython.Build import cythonize

BASE_DIR = Path(__file__).resolve().parent


class ReleaseBase:
    def __init__(self, base_dir: Path, escapes):
        self.base_dir = base_dir
        self.escapes = escapes
        self.errors = []  # 编译错误文件

    def clear_files(self, pattern: str):
        files = self.base_dir.rglob(pattern)

        for file in files:
            if any(i in file for i in self.escapes) or file == __file__:
                print(f'{file} 跳过清除')
                pass
            else:
                os.remove(file)

    def clear_so_files(self):
        self.clear_files('*.so')

    def clear_py_files(self):
        self.clear_files('*.py')

    def python_files(self):
        files = self.base_dir.rglob('*.py')
        for file in files:

            s_file = str(file)

            if "yml" in s_file:
                continue
            if self.is_skip(s_file):
                print(f'跳过文件: {s_file}')
                continue

            yield s_file

    def build(self, delete_so, delete_py):
        if delete_so:
            self.clear_so_files()

        for file in self.python_files():
            print(f'编译: {file}')
            try:
                setup(
                    ext_modules=cythonize(file, compiler_directives={'language_level': "3"}),
                    script_args=['build_ext']
                )
                filepath = "/".join(file.split('/')[:-1])
                filename = file.split('/')[-1:][0][0:-3]
                self.move_so_file('./build', filepath, filename)
                if delete_py:
                    os.remove(file)
            except Exception as e:
                print(f'编译文件 {file} 错误: {e}')
                self.errors.append(file)

        for error_file in self.errors:
            print(f'文件 {error_file} 编译错误')

    @staticmethod
    def clear():
        b = BASE_DIR / 'build'
        if b.exists():
            shutil.rmtree(b)

    def is_skip(self, file: str):
        if any(i in file for i in self.escapes) or file == __file__:
            return True

        with open(file) as f:
            for i in range(10):
                regex = f'# *cython *: *skip'
                if re.match(regex, f.readline()):
                    return True
        return False

    @staticmethod
    def move_so_file(build, filepath, filename):
        if filepath == "":
            return
        if os.path.exists(build):
            for so_file in glob.glob(f'{build}/**', recursive=True):
                if so_file[-3:] == ".so":
                    new_file = f"{filepath}/{filename}.so"
                    if filename in so_file:
                        shutil.copy(so_file, new_file)
                        print(f'输出SO文件 {so_file} -> {new_file}')
                        os.remove(so_file)
                        c_file = f"{filepath}/{filename}.c"
                        if os.path.isfile(c_file):
                            os.remove(f"{filepath}/{filename}.c")


class Release:
    @classmethod
    def start(cls, dirs, escapes=None, delete_so=False, delete_py=True):
        """
        发布加密代码。想要跳过的部分只需要再文件头部添加 # cython: skip 即可
        :param dirs: 发布包位置集合，不填写默认从当前文件夹开始编译
        :param escapes: 关键字跳过，默认跳过
        :param delete_so: 是否先删除原来的so文件
        :param delete_py: 是否删除源文件
        :return: None
        """
        if escapes is None:
            escapes = ['__init__.py', 'test.py', 'setup.py']

        assert isinstance(dirs, Iterable)
        assert isinstance(escapes, Iterable)

        ps = []
        for d in dirs:
            print(f'从 {d} 开始打包 python 文件')
            p = Process(target=ReleaseBase(d, escapes).build, args=(delete_so, delete_py))
            ps.append(p)

        for p in ps:
            p.start()
        for p in ps:
            p.join()

        ReleaseBase.clear()

    @classmethod
    def clear_py(cls, dirs, escapes=None):
        if escapes is None:
            escapes = ['__init__.py', 'test.py']

        for d in dirs:
            print(f'{d} 清除所有 .py 文件')
            ReleaseBase(d, escapes).clear_files('*.py')

    @classmethod
    def clear_so(cls, dirs, escapes=None):
        if escapes is None:
            escapes = []

        for d in dirs:
            print(f'{d} 清除所有 .so 文件')
            ReleaseBase(d, escapes).clear_files('*.so')


if __name__ == '__main__':
    desc = '编译发布工具: python release.py -p microservice/device -b 0 -dso 1 -dpy 0'
    PARSER = argparse.ArgumentParser(description=desc)
    PARSER.add_argument('-dso', '--delete_so', default=0, type=int, required=False,
                        help="是否删除so文件: 0不删除，1删除")
    PARSER.add_argument('-dpy', '--delete_py', default=1, type=int, required=False,
                        help="是否删除py文件: 0不删除，1删除")
    PARSER.add_argument('-b', '--build', default=1, type=int, required=False,
                        help="是否删除py文件: 0不编译，1编译")
    PARSER.add_argument('-p', '--path', default='', required=False, help="请输入待编译的路径名称[可输入多个]",
                        nargs='*')

    ARGS = PARSER.parse_args()
    dso = True if ARGS.delete_so == 1 else False
    dpy = True if ARGS.delete_py == 1 else False
    is_build = True if ARGS.build == 1 else False

    path_list = []
    if ARGS.path:
        for path in ARGS.path:
            abs_path = Path(path).absolute()
            if abs_path.exists():
                path_list.append(abs_path)

    if is_build:
        print(f'开始编译代码: path_list={path_list}')
        Release.start(dirs=path_list, delete_py=dpy, delete_so=dso)
    else:
        if dso:
            Release.clear_so(path_list)
        if dpy:
            Release.clear_py(path_list)
