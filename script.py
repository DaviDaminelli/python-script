import os
import json
import shutil
from subprocess import PIPE, run
import sys

#start analysing the file on the main function in the end of the file

#defines the string keyword we want the script to look at in directories to find what we want
DIRECTORY_KEYWORD = "py"
FILES_COMPILED = []

#find all the directories that contain a certain name on it, as defined previously
def get_directories_paths(source):
    directories_paths = [] ##all directories paths that has the keyword we want to get will be stored here, so we can
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if  DIRECTORY_KEYWORD in directory.lower(): #if it finds a directory that has the keyword, in uppercase or lowercase, adds it to the list of paths
                path = os.path.join(source, directory) #get the full path to this directory that has the keyword
                directories_paths.append(path) #add

        break
    return directories_paths

#get the name of all directories
def get_directories_names(paths):
    names = []
    for path in paths:
        _, directory_name = os.path.split(path)
        names.append(directory_name)

    return names

#create a directory if it doesnt exist
def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

#recursive copy operation, overwrite destination folder if it already exists
def copy_and_overwrite(source, destination):
    #if the destination folder already exists, delete it. It will be written again
    if os.path.exists(destination):
        shutil.rmtree(destination) #remove tree, recursive delete
    shutil.copytree(source, destination) #recursive copy

#make json file
def make_json_metadata_file(path, directories, files_c):
    data ={
        "folderNames": directories,
        "numberOfFolders": len(directories),
        "compiledFiles": FILES_COMPILED,
        "numberOfCompiledFiles": len(FILES_COMPILED)
    }
    #closes the file automatically, W overrides the preexisting file
    with open(path, "w") as file:
        #dumps the information into the a file
        json.dump(data, file)
        
#make compile command
def compile_c_code_command(path):
    #variable to store the file name
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".c"):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return
    else:
        #build the command that will be inserted into the terminal
        command = ["gcc"] + [code_file_name]
        print("compiling file", code_file_name)
        FILES_COMPILED.append(code_file_name)
        run_compile_c_command(command, path) #run

#compile C in terminal
def run_compile_c_command(command, path):
    #stores current working directory
    cwd = os.getcwd()
    os.chdir(path) #changes to the directory the file is in

    result = run(command, stdout = PIPE, stdin = PIPE, universal_newlines=True)#run command in terminal
    print("compile result ", result)

    os.chdir(cwd) #changes to the directory it was before, that we stored


def main(source, destination):
    cwd = os.getcwd() #get the current working directory, the directory the python file is run from
    source_path = os.path.join(cwd, source) #creates the source path that the action is going to get things
    destination_path = os.path.join(cwd, destination) #creates the destination path that the action is going to be placing things
    
    #get the directory paths of every folder the source has
    directories_paths = get_directories_paths(source_path)
    directories_names = get_directories_names(directories_paths)
    for i in directories_names:
        print("found: " + i)

    #creates the destination folder in the destination path
    create_dir(destination_path)
    print("created \"" + destination + "\" directory")

#   this for loop simply copys the content of the folder to the destination directory, however it wont transfer everything if there is more than one directory using this copy function. Its here for show purpose on only
#    for src in directories_paths:
#        copy_and_overwrite(src, destination_path)
#        print("done")
    
    #copy the content to the destination folder using for loop, because I'm using lists
    for src, dest in zip(directories_paths, directories_names): #zip joins interatable objects together in a tuple, this way, the lists of the pats of a directory and the lists of its names will be paired together and we can access both in a for loop
        #for loop uses the names of the folders to create the destination path
        destination_path = os.path.join(destination, dest)
        copy_and_overwrite(src, destination_path)
        print("copied "+ dest + " to "+destination)
        compile_c_code_command(destination_path)

    #makes the json file about the action of the script
    json_path = os.path.join(destination, "metadata.json")
    make_json_metadata_file(json_path, directories_names, FILES_COMPILED)

#this allow the code to be only excecuted if the file is being directly run; so, if it is imported, the script wont be excecuted, for example
if __name__ == "__main__":
    args = sys.argv
    #print(args)
    #the program cant run witohut a given source file and a destination file
    if len(args) != 3:
        raise Exception("you must pass a source and a target directory - only.")
    source, destination = args[1:] #strips the name of the file out of the given user input
    main(source, destination) #executes the script