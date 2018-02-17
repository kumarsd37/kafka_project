from setuptools import setup, find_packages

with open('requirements.txt', 'r') as fh:
    required_packages = fh.read().splitlines()

setup(
    name='kafka_project',
    version='1.0',
    packages=find_packages(), # todo change package name
    url='https://github.com/pavan538/kafka_project',
    license='MIT',
    author='pavan, himanshu, amit, dwaip',
    author_email='pavan.tummalapalli@gmail.com, sangalhimanshu08@gmail.com, amitct100@gmail.com, dwaip@yahoo.com',
    description='multi client message processor',
    install_requires=required_packages,
      include_package_data=True,
      zip_safe=False
)


