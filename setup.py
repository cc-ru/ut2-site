from setuptools import setup

setup(
    name='ut2_site',
    packages=['ut2_site'],
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-WTF',
        'Flask-Uploads',
        'pymongo'
    ])
