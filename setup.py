import setuptools

VERSION = "2.0.2a1"
INSTALLNAME = "ior_research"


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name=INSTALLNAME,
     version=f'v{VERSION}',
     author="Mayank Shinde",
     author_email="mayank31313@gmail.com",
     description="A platform to control robots and electronic device over Internet",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/mayank31313/ior-python",
     packages=setuptools.find_packages(),
    install_requires=["requests", "pyyaml", "pycryptodome", "paho-mqtt", "marshmallow",
              "pick>=1.2.0", "ruamel.yaml>=0.17.21", "cndi>=2.1.6a"],
     # packages=['ior_research'],
     keywords=['ior','iot','network_robos', 'control_net'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         'Intended Audience :: Developers',
     ]
 )