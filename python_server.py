#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
from flask import Flask, request, render_template
import json
r = redis.Redis(host="localhost", port=6379, db=0)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('form.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if r.hget(name=username, key="password") == None:
        return render_template('form.html', message="用户不存在，请注册", username=username)
    elif r.hget(name=username, key="password") == password.encode("utf-8"):
        # Kuuga Agito Ryuki Faiz Blade Hibiki Kabuto DenO kiva Decade W OOOs Fourze Wizard Gaim Drive Ghost Ex-aid Build
        user_info = r.hgetall(username)
        test_info = r.hgetall("test_name")
        print("user_info: ", user_info)
        print("test_info: ", test_info)
        user_grade_list = []

        for i in range(len(test_info.keys())):
            name = test_info["test_{0}".format(i+1).encode("utf-8")].decode("utf-8")
            score = user_info["test_{0}".format(i+1).encode("utf-8")].decode("utf-8")
            user_grade_list.append({"test_name": name, "score": score})

        return render_template('signin-ok.html',  username=username, user_grade_list = user_grade_list)
    else:
        return render_template('form.html', message='用户名或密码错误', username=username)

@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('form_signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = str(request.form['password'])
    password2 = str(request.form['password2'])
    if (password != password2):
        return render_template('form_signup.html', message="密码不一致", username=username)
    else:
        if r.exists(username) and r.hget(name=username, key="password") != None:
            return render_template('form.html', message="该用户已存在，请使用已有密码登录", username=username)
        else:
            r.hset(username, "password", password)
            return render_template('form.html')

@app.route('/radar', methods = ['POST'])
def generate_radar():
    username = request.form['UserID']
    info = r.hget("radar_info", username)
    if (info != None):
        return render_template('radar.html', obj={"name":username, "data":info})
    else:
        return render_template('radar_error.html')

# @app.route('/test', methods = ['GET'])
# def template_test():
#     user_name = "181830158"
#     user_info = r.hgetall(user_name)
#     test_info = r.hgetall("test_name")
#     print("user_info: ", user_info)
#     print("test_info: ", test_info)
#     user_grade_list = []

#     for i in range(len(test_info.keys())):
#         name = test_info["test_{0}".format(i+1).encode("utf-8")].decode("utf-8")
#         score = user_info["test_{0}".format(i+1).encode("utf-8")].decode("utf-8")
#         user_grade_list.append({"test_name": name, "score": score})
#     return render_template('signin-ok.html',  username=user_name, user_grade_list = user_grade_list)

if __name__ == '__main__':
    app.run(port=5012)