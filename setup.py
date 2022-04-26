from setuptools import setup,find_packages

setup(
    name = 'EasyDES',
    version = '0.2',
    author = 'seclee',
    author_email = 'seclee@126.com',
    packages = find_packages('EasyDES'),
    license='MIT',
    zip_safe=False,
    install_requires=[
    'msgpack'
]
)