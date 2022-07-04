import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requires.txt", "r") as stream:
    requirements = list(map(lambda dep: str(dep).strip(), stream.read().split("\n")))

setuptools.setup(
     name='ior_research',
     version='v2.0.1',
     author="Mayank Shinde",
     author_email="mayank31313@gmail.com",
     description="A platform to control robots and electronic device over Internet",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/mayank31313/ior-python",
     packages=setuptools.find_packages(),
     # packages=['ior_research'],
     install_requires = requirements,
     keywords=['ior','iot','network_robos', 'control_net'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         'Intended Audience :: Developers',
     ]
 )