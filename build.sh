#! /bin/bash

build_dir=build/sophgoapi  # TODO：所有sophgoapi替换成自己的包名
mkdir -p ${build_dir}
cp -r object_detection release.py setup.py ${build_dir}  # TODO: 拷贝待加密文件或文件夹到build目录下
cd ${build_dir}

python3 release.py -p $(pwd) && mv setup.py release.py ../ && cd ../  # 加密
python3 setup.py sdist bdist_wheel || true  # 打包
mv dist/sophgoapi-1.0.5-py3-none-any.whl ../ && cd ../  # 移动加密后的包到上一级目录

