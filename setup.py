from setuptools import setup, find_packages
setup(
    name="gitoriouslib",
    version="0.1",
    packages=find_packages(),
    install_requires=['httplib2>=0.7.2'],
    entry_points={
        'console_scripts': [
            'glcreate = gitoriouslib.cmd:create_repo',
            'gldelete = gitoriouslib.cmd:delete_repo',
        ]
    },
)
