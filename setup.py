from setuptools import setup, find_packages

setup(
    name='RehearsAI-client',
    version='1.0.0',
    author='Colin Bennie, Inseong Han, Kejia Wang, Ranjeet Nagarkar, Sangjun Han',
    description='AI mocker interviewer client application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/msds603-startup8/RehearsAI-client',
    packages=find_packages(),
    install_requires=[
        "pytest",
        # "jina==3.25.0"
    ],
    python_requires='==3.9.*'
)
