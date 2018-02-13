from setuptools import setup

with open('requirements.txt', 'r') as fh:
    required_packages = fh.read().splitlines()

setup(
    name='kafka_project',
    version='1.0',
    packages=['framework'], # todo change package name
    url='https://github.com/pavan538/kafka_project',
    license='MIT',
    author='pavan, himanshu, amit, dwaip',
    author_email='pavan.tummalapalli@gmail.com, sangalhimanshu08@gmail.com, amitct100@gmail.com, dwaip@yahoo.com',
    description='multi client message processor',
    install_requires=required_packages,
      include_package_data=True,
      zip_safe=False
)


