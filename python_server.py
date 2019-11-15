import redis
from flask import Flask, request, render_template
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
        userinfo_raw = r.hgetall(name=username)
        keys = ["First", "Second"]
        userinfo = {}
        for key in keys:
            if key.encode("utf-8") in userinfo_raw.keys():
                print("GET ", username, " attr ", key)
                rst = userinfo_raw[key.encode("utf-8")]
                print(rst)
                if (rst != None):
                    userinfo[key] = rst.decode("utf-8")
        return render_template('signin-ok.html', username=username, userinfo=userinfo)
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

if __name__ == '__main__':
    app.run(port=5012)