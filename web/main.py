from flask import Flask,render_template
import configparser,os

filePath=''
config=configparser.ConfigParser()
config.read(filePath)

app=Flask(__name__)

if __name__ == '__main__':
    pass