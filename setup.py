from setuptools import setup, find_packages
from pathlib import Path

# TODO：除了.py文件，其他格式的文件如需打包进去，都要在这里添加到list中
abs_path = Path('./')
so_path = abs_path.rglob('*.so')
yml_path = abs_path.rglob('*.yml')
txt_path = abs_path.rglob('*.txt')
jpg_path = abs_path.rglob('*.jpg')
sophgoapi_path = [str(path) for path in so_path] + [str(path) for path in yml_path] + [str(path) for path in txt_path] + [str(path) for path in jpg_path]

with open("MANIFEST.in", mode="w+") as f:
    for path in sophgoapi_path:
        f.writelines("include " + path + "\n")

with open("sophgoapi/__init__.py", mode="w+"): ...


if __name__ == '__main__':
    setup(
        name='sophgoapi',  # TODO：替换自己的包名
        version='1.0.5',
        install_requires=[
            'opencv-python==4.10.0.84',
            'shapely==2.0.6',
            'psutil'
        ],
        packages=find_packages(),
        description='sophgoapi',
        license='Apache License 2.0',
        zip_safe=False,
        include_package_data=True,
        package_data={'sophgoapi': sophgoapi_path},  # # TODO：替换自己的包名
    )
