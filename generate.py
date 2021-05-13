from PIL import Image, ImageDraw
from noise import pnoise2, snoise2
import numpy as np
import subprocess
from shutil import copyfile

def perlinNoise(width, height):
    #define perlin noise parameters
    octaves = 6
    freq = 16.0 * octaves
    y_max = 5
    x_max = 5
    imarray = [[0 for x in range(y_max)] for x in range(x_max)]

    #create noise and do math
    arr = np.zeros((width, height), dtype=np.uint8)
    y_max, x_max = arr.shape

    for y in range(y_max):
        for x in range(x_max):
            val = int(snoise2(x / freq, y / freq, octaves) * 127.0 + 128.0)
            arr[y,x] = val
    return arr

def gaussNoise(width, height):
    #define guassian noise parameters
    octaves = 6
    y_max = 5
    x_max = 5
    scale = 5.0

    #do noise calculations
    arr = np.zeros((width, height), dtype=np.uint8)
    y_max, x_max = arr.shape

    for y in range(y_max):
        for x in range(x_max):
            val = int(pnoise2(x * scale / width, y * scale / height, octaves, scale, scale) * 127.0 + 128.0)
            arr[y,x] = val
    return arr

def noNoise(width, height):
    arr = np.zeros((width, height), dtype=np.uint8)
    y_max, x_max = arr.shape

    #set all pixels to the same value, no noise on texture
    for y in range(y_max):
        for x in range(x_max):
            val = 128
            arr[y,x] = val
    return arr

#######################
#define colors
#add/remove/modify here
#######################
opaquebgs =     [#RRGGBB    name
                '#F4F6F7', 'white',
                '#A6ACAF', 'lightgray',
                '#424949', 'darkgray',
                '#1C2833', 'black',
                '#E74C3C', 'red',
                '#AF601A', 'orange',
                '#F1C40F', 'yellow',
                '#52BE80', 'green',
                '#2E86C1', 'blue',
                '#A569BD', 'indigo',
                '#4B0082', 'purple'
                ]

transbgs =      [#RRGGBBAA    name
                '#00000025', 'transparent',
                '#F4F6F725', 'white',
                '#A6ACAF25', 'lightgray',
                '#42494925', 'darkgray',
                '#1C283325', 'black',
                '#E74C3C25', 'red',
                '#AF601A25', 'orange',
                '#F1C40F25', 'yellow',
                '#52BE8025', 'green',
                '#2E86C125', 'blue',
                '#A569BD25', 'indigo',
                '#4B008225', 'purple'
                ]


bordercolors =  [#RRGGBB    name
                '#1C2833', 'black',
                '#F4F6F7', 'white'
                ]


#define variables
vtflibpath = "E:/textures/vtflib/bin/x64/VTFCmd.exe"
pngpath = "E:/textures/dev" #where texture source is saved
matdir = "E:/Program Files/Steam/steamapps/common/Team Fortress 2/tf/materials" #dir to materials folder of source game
matsubdir = "_hex" #name of folder in game/materials
texbase = "hdev" #base name of texture
#final format is `game/materials/matsubdir/texbase_noise_bgcolor_bordercolor.vtf`
width = 512 #size of image, 512 is good
height = 512
thickness = 5 #size of grid border


######
#user input to choose what type of texture to make
######
print("Select type of noise to use.\n")
print("1) Perlin (smooth)")
print("2) Gaussian (static)")
print("3) No noise (flat)")

userNoise = input("> ")

if userNoise == "1":
    texbase += "_perlin"
elif userNoise == "2":
    texbase += "_gauss"
elif userNoise == "3":
    texbase += "_smooth"
else:
    texbase += "_smooth"

print("\n\nSelect type of texture to create.\n")
print("1) Dev (opaque)")
print("2) Glass (transparent)")

userTex = input("> ")

if userTex == "1":
    bgcolors = opaquebgs
    texbase += "_opaque"
elif userTex == "2":
    bgcolors = transbgs
    texbase += "_glass"
else:
    texbase += "_glass"


#loop here for each and every texture we want to create
for i1 in range(0,int(len(bgcolors)/2)):
    background = bgcolors[i1*2]
    backgroundName = bgcolors[(((i1+1)*2)-1)]

    for i2 in range(0,int(len(bordercolors)/2)):
        border = bordercolors[i2*2]
        borderName = bordercolors[(((i2+1)*2)-1)]

        #create texure file name base name
        texname = texbase + '_' + backgroundName + '_' + borderName
        
        #create bg image
        im = Image.new("RGBA", (width,height), background)

        #call appropriate noise function
        if userNoise == "1":
            arr = perlinNoise(width, height)
        elif userNoise == "2":
            arr = gaussNoise(width, height)
        elif userNoise == "3":
            arr = noNoise(width, height)
        else:
            arr = noNoise(width, height)

        #generate noise image
        noise = Image.fromarray(arr, 'L')
        noise = noise.convert('RGBA')

        #do funny white->alpha conversions
        datas = noise.getdata()
        newData = []

        for item in datas:
            #loop through every pixel in image
            wasWhite = False
            for value in range(1,255):
                #check all possible white-gray values per pixel
                if item[0] == value and item[1] == value and item[2] == value:
                    #if rg&b are the same, swap for alpha
                    newData.append((value, value, value, (255-value)))
                    wasWhite = True
                    break
                
            if not wasWhite:
                newData.append(item)

        #create new transparent rgba noise image
        noise.putdata(newData)

        #combine noise and bg pictures
        im.paste(noise, (0,0), noise)

        #add borders
        draw = ImageDraw.Draw(im)
        draw.rectangle([(0,0), (thickness, height)], fill=border)
        draw.rectangle([(0,height-thickness), (width, height)], fill=border)
        draw.rectangle([(width-thickness, height), (width, 0)], fill=border)
        draw.rectangle([(0,0), (width, thickness)], fill=border)

        #save picture, close pictures
        #im.show()
        path = pngpath + "/" + texname + '.png'
        im.save(path, 'PNG')

        im.close()
        noise.close()

        #now convert the png we just saved into a vtf
        subprocess.call([vtflibpath, '-file', path, '-silent'])
        print(path)
        
        #create vmt
        vmt = open(pngpath + "/" + texname + ".vmt", "w")
        vmt.write("\"LightmappedGeneric\"\n")
        vmt.write("{\n")
        vmt.write("\t\"$basetexture\" \"" + matsubdir + "\\" + texname + "\"\n")
        if userTex == "2":
            vmt.write("\t\"$translucent\" \"1\"\n")
        vmt.write("}")
        vmt.close()

        #copy vtf and vmt to game path
        copyfile(pngpath + "/" + texname + ".vtf", matdir + "/" + matsubdir + "/" + texname + ".vtf")
        copyfile(pngpath + "/" + texname + ".vmt", matdir + "/" + matsubdir + "/" + texname + ".vmt")

        #done
