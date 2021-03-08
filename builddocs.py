import os
import shutil

os.chdir("./sphinx")
shutil.rmtree("_build")
os.system("make.bat html -o ../ .")

os.chdir("./_build/html")
os.rename("_static","static")

for file_name in os.listdir():
    if file_name.endswith(".html"):
        file = open(file_name, "r")
        data = file.read()
        file.close()
        os.remove(file_name)
        data = data.replace("_static", "static")
        file = open(file_name, "w")
        file.write(data)
        file.close()

os.system("cp -r ./* C:/Users/Asus/Desktop/python-docs")