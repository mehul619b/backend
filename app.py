######IMPORTS######
from flask import Flask,request,jsonify,render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json,jwt
from flask_cors import cross_origin
from functools import wraps
import datetime,os



#####APP CONFIGS#######
app=Flask(__name__,template_folder="build/",static_folder="build/static")
app.config["SECRET_KEY"]="INSPEKTLAB_SECRET_KEY"
#app.config["TEMPLATE_FOLDER"]=f"../frontend/build"
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

#######UTILS#############
def token_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        token= request.args.get('token')
        if not token:
            return jsonify({'message':'THE TOKEN WAS MISSING!!'})
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'NOT A VALID TOKEN'})
        return f(*args,**kwargs)
    return wrapper 


#######ROUTES##########
@app.route("/get_file_name",methods=["POST"])
@cross_origin()
def get_file_name():
    if request.method=="POST":
        if "file" in request.files:
            return request.files["file"].filename
        else:
            return "no file Recieved"
    return "you made a get request"

@app.route("/",methods=['GET'])
def home():
    return render_template("index.html")



@app.route("/api/login",methods=["POST"])
def login():
    req_data=request.get_json()
    if req_data['user']=="admin" and req_data['password']=="test":
        token=jwt.encode({"user":"admin",'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config["SECRET_KEY"])
        return jsonify({'token':token.decode("UTF-8")})
    return jsonify({'message':'USERNAME OR PASSWORD INVALID'})

@app.route('/api/protected',methods=['GET'])
@token_required
@limiter.limit("3/minute")
def protected():
    return jsonify({'message':'THIS IS A PROTECTED METHOD'})


if __name__=="__main__":
    app.run(port=5000,debug=True)
