from setuptools import setup
import os

# python setup.py bdist_wheel
# python setup.py sdist
# twine upload dist/*


module_name = 'epyt'
data = list()
packages = list()
pack_path = os.path.join(os.getcwd(), module_name)
for root, dirs, files in os.walk(pack_path):
    p = '/'
    if root == pack_path:
        packages = dirs
        p = ''
    for file in files:
        data.append(f"{root[len(pack_path) + 1:]}{p}{file}")

packages = [f"{module_name}.{x}" for x in packages]
packages.append(module_name)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=module_name,
    version="1.0.3",
    author="KIOS CoE",
    author_email="kiriakou.marios@ucy.ac.cy",
    description='A Python module for EPANET water distribution simulation libraries. The EPyT is inspired by the '
                'EPANET-Matlab Toolkit.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/OpenWaterAnalytics/EPyT',
    project_urls={
        "Bug Tracker": 'https://github.com/OpenWaterAnalytics/EPyT/issues',
    },
    packages=packages,
    keywords='epanet, water, networks, hydraulics, quality, simulations, emt, epanet matlab toolkit',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python',
        'License :: OSI Approved :: European Union Public Licence 1.2 '
        '(EUPL 1.2)',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.7",
    package_data={f'{module_name}': data},
    install_requires=['numpy', 'matplotlib', 'pandas'],
    include_package_data=True
)
