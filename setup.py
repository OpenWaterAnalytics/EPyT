from setuptools import setup
import os


# python setup.py bdist_wheel
# python setup.py sdist
# twine upload dist/* --config-file .pypirc

def read_version_from_init(file_path="epyt/__init__.py"):
    version_line = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version_line = line
                break
    if version_line:
        version_str = version_line.split("=")[1].strip().strip('"').strip("'")
        return version_str
    else:
        raise RuntimeError("Unable to find version string.")


__version__ = read_version_from_init()
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
    version=f"{__version__}",
    author="Marios S. Kyriakou",
    author_email="kiriakou.marios@ucy.ac.cy",
    description='EPyT: An EPANET-Python Toolkit for Smart Water Network Simulations. The EPyT is inspired by the '
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python',
        'License :: OSI Approved :: European Union Public Licence 1.2 '
        '(EUPL 1.2)',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.8",
    package_data={f'{module_name}': data},
    install_requires=['numpy', 'matplotlib', 'pandas', 'xlsxwriter', 'setuptools'],
    include_package_data=True
)
