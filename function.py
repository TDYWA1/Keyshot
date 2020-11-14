import os
import re
import json

def getModelFile(path):#获取所有文件的路径
    try:
        if os.path.isfile(path):
            #print(path)
            #return filelist
            yield path
        elif os.path.isdir(path):
            for s in os.listdir(path):
                newpath = os.path.join(path,s)
                for p in getModelFile(newpath):
                    yield p
    except PermissionError:
        print(path+"\t无法访问")
    except Exception as e:
        print(repr(e))



def filterFileList(file_list,ext_list):#过滤文件列表
    for file in file_list:
        filename,extname = os.path.splitext(file)
        filename=os.path.split(filename)[1]
        if extname.lower() in ext_list and re.match("~\$",filename)==None:
            yield file



def getMaterialName(matpath):
    with open(matpath, "r", encoding="utf8") as f:
        # f.readline()
        while True:
            try:
                content = f.readline()
            except UnicodeDecodeError:
                continue
            if content == '':
                break
            else:
                if re.match("#define material", content) != None:
                    n = re.search(r'"(.*)"', content)
                    if n!=None:
                        #print(n.group(1))
                        return n.group(1),matpath
                    else:
                        return False

    return False

def InitMaterials(dirpath):
    mtl_dict = {}
    for i in filterFileList(getModelFile(dirpath),[".mtl"]):
        #print(i)
        status = getMaterialName(i)
        #print(status)
        if not status==False:
            k,v = status
            mtl_dict[k]=v

    print(mtl_dict)

def retmatdiv(dir):
    divlist={}
    for f in os.listdir(dir):
        path = os.path.join(dir,f)
        # print(path)
        if os.path.isdir(path):
            divlist[f]="dir"
        elif os.path.splitext(path)[1]==".mtl":
            #print(path)
            s=getMaterialName(path)
            if not s==False:
                k,v=s
                divlist[k]="mtl"
        else:
            continue
    return divlist

def loadJson(path):
    with open(path,'r',encoding="utf-8") as f:
        obj = json.load(f)
    return obj

from subprocess import  Popen,PIPE
#重定向输出


if __name__ == '__main__':
    cwd = "E:/F"
    process=Popen(['keyshot','-script',os.getcwd()+'\\startkeyshot.py'],shell=True,stdout=PIPE,stderr=PIPE,cwd=cwd,encoding="utf-8")


