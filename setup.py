from setuptools import setup, find_packages

setup(
    name='ordinal_comparator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'certifi>=2023.0.0',
        'charset-normalizer>=3.0.0',
        'deepdiff>=8.0.0',
        'gevent>=23.0.0',
        'greenlet>=3.0.0',
        'idna>=3.0',
        'jsonpath-ng>=1.5.0',
        'orderly-set>=5.0.0',
        'ply>=3.11',
        'requests>=2.28.0',
        'setuptools>=65.0.0',
        'tqdm>=4.65.0',
        'urllib3>=1.26.0',
        'zope.event>=4.5',
        'zope.interface>=5.0',
    ],
    entry_points={
        'console_scripts': [
            'ordinal-comparator=ordinal_comparator.cli:main',
        ],
    },
    author='wanyvic',
    author_email='q873040807@gmail.com',
    description='A tool for comparing ordinal indexer implementations',
    keywords='bitcoin, ordinals, brc20, indexer, comparator',
    python_requires='>=3.8',
)
