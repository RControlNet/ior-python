import os
import shutil
import yaml

with open("config.yml","r") as file:
    config = yaml.safe_load(file)

pythonDoc = config['python']

os.chdir(pythonDoc['doc'] + "./sphinx")
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

copyPath = config['copyPath']

os.system("cp -r ./* " + copyPath['dst'] + "/docs/python")