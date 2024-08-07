#!/usr/bin/python3

import os
import sys
import shutil
import zipfile
import urllib.request

# Recursivly copy all files of a given extension from src to dest folders.
# If a dict named "replace" is passed in, key:value pairs will be replaced on both the target filenames and file contents.
def copyFiles(src, dest, filetypes, replace={}):
    for item in os.listdir(src):
        if os.path.isdir(src + os.sep + item):
            copyFiles(src + os.sep + item, dest + os.sep + item, filetypes, replace=replace)
        else:
            if item.split(".")[-1].lower() in filetypes:
                os.makedirs(dest, exist_ok=True)
                targetFile = dest + os.sep + item
                shutil.copy(src + os.sep + item, targetFile)
                
                with open(targetFile, encoding="utf-8", errors="ignore") as targetFileHandle:
                    targetFileContents = targetFileHandle.read()
                
                for findValue in replace.keys():
                    targetFileContents = targetFileContents.replace(findValue, replace[findValue])
                
                with open(targetFile, "w", encoding="utf-8") as targetFileHandle:
                    targetFileHandle.write(targetFileContents)
                
                for findValue in replace.keys():
                    if findValue in targetFile:
                        os.rename(targetFile, targetFile.replace(findValue, replace[findValue]))

# Print a message for the user if they haven't specified any parameters.
outputFolder = ""
if len(sys.argv) < 2:
  print("Generates a Jekyll-compatible template from the GOV.UK Design System frontend.")
  print("Usage: python3 package.py outputFolder")
  sys.exit(0)
  
outputFolder = sys.argv[1]

print("Downloading govuk-frontend archive...")
zipArchive = open("main.zip", "wb")
zipArchive.write(urllib.request.urlopen("https://github.com/alphagov/govuk-frontend/archive/main.zip").read())
zipArchive.close()
zipfile.ZipFile("main.zip", "r").extractall("main")
os.remove("main.zip")

versionHandle = open("main/govuk-frontend-main/dist/VERSION.txt")
govukFrontendVersion = versionHandle.read().strip()
versionHandle.close()

print("Version obtained: " + govukFrontendVersion)

os.makedirs(outputFolder, exist_ok=True)
os.makedirs(outputFolder + os.sep + "_sass", exist_ok=True)
os.makedirs(outputFolder + os.sep + "_includes", exist_ok=True)
os.makedirs(outputFolder + os.sep + "_layouts", exist_ok=True)
os.makedirs(outputFolder + os.sep + "_plugins", exist_ok=True)
os.makedirs(outputFolder + os.sep + "assets", exist_ok=True)
os.makedirs(outputFolder + os.sep + "javascript", exist_ok=True)
os.makedirs(outputFolder + os.sep + "stylesheets", exist_ok=True)

print("Copying files...")

# Copy over the SCSS files from govuk-frontend
copyFiles("main" + os.sep + "govuk-frontend-main" + os.sep + "packages" + os.sep + "govuk-frontend", outputFolder + os.sep + "_sass", ["scss"])

# Copy over compiled / minified Javascript files from govuk-frontend.
copyFiles("main" + os.sep + "govuk-frontend-main" + os.sep + "dist", outputFolder + os.sep + "javascript", ["js"])

# Copy over static assets (fonts, icons, images) from govuk-frontend.
copyFiles("main" + os.sep + "govuk-frontend-main" + os.sep + "dist" + os.sep + "assets", outputFolder + os.sep + "assets", ["woff","woff2","eot","ico","png","svg"])

# Remove the govuk-frontend folder.
shutil.rmtree("main")

# Copy over our stylesheets folder, replacing version numbers along the way.
copyFiles("stylesheets", outputFolder + os.sep + "stylesheets", ["scss"], replace={"versionGoesHere":govukFrontendVersion})

# Copy over our includes folder.
copyFiles("_includes", outputFolder + os.sep + "_includes", ["html"])

# Copy over our layouts folder.
copyFiles("_layouts", outputFolder + os.sep + "_layouts", ["html"])

# Copy over our plugins folder.
copyFiles("_plugins", outputFolder + os.sep + "_plugins", ["rb"])

print("Done.")
