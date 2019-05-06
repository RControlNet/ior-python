import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='ior_research',  
     version='0.1',
     scripts=['IOTClient.py'] ,
     author="Mayank Shinde",
     author_email="mayank31313@gmail.com",
     description="A platform to control robots over Internet",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://iorresearch.ml/IOT",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "LICENSE :: OSI APPROVED :: MIT License",
         "Operating System :: OS Independent",
     ],
 )