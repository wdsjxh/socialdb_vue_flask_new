'''
api
存在问题：
- 并发请求时，且前一请求正在查询会导致卡死
'''

import time
import os
from pymongo import MongoClient
from flask import Flask, request, jsonify, redirect, url_for
from flask_restful import Api, Resource, reqparse
from conf.config import MongoDBConfig

app = Flask(__name__)
# client = MongoClient(MongoDBConfig.g_server_ip, MongoDBConfig.g_server_port)
# db = client[MongoDBConfig.g_db_name]


if os.environ.get('MONGODB_URI'):
    MONGODB_URI = os.environ.get('MONGODB_URI')
else:
    MONGODB_URI = 'mongodb://' + MongoDBConfig.g_server_ip + ':' + str(MongoDBConfig.g_server_port)

client = MongoClient(MONGODB_URI, connect=False)
db = client[MongoDBConfig.g_db_name]


def response_cors(data=None, datacnts=None, status=None):
    '''为返回的json格式进行跨域请求'''
    if data:
        resp = jsonify({"status": status, "data": data, "datacounts": datacnts})
    else:
        resp = jsonify({"status": status})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


class Person(Resource):
    '''人员类'''

    def get(self, user=None, email=None, password=None, passwordHash=None, source=None, xtime=None):
        # 该处可能存在安全问题，做出限制会更好
        # print(user)
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, help='Show [limitn] datas in one page')
        parser.add_argument('skip', type=int, help='Skip [skipn] datas')
        args = parser.parse_args()
        limitn = 10 if args['limit'] is None else args['limit']
        skipn = 0 if args['skip'] is None else args['skip']

        # data用于存储获取到的信息
        data = []
        datacnts = 0

        # 待改进
        if user:
            persons_info = db.person.find({"user": {"$regex": user, "$options": "$i"}}, {"_id": 0}).limit(limitn).skip(
                skipn)
            datacnts = db.person.find({"user": {"$regex": user, "$options": "$i"}}, {"_id": 0}).count()

        elif email:
            persons_info = db.person.find({"email": {"$regex": email, "$options": "$i"}}, {"_id": 0}).limit(
                limitn).skip(skipn)
            datacnts = db.person.find({"email": {"$regex": email, "$options": "$i"}}, {"_id": 0}).count()

        elif password:
            persons_info = db.person.find({"password": {"$regex": password, "$options": "$i"}}, {"_id": 0}).limit(
                limitn).skip(skipn)
            datacnts = db.person.find({"password": {"$regex": password, "$options": "$i"}}, {"_id": 0}).count()

        elif passwordHash:
            persons_info = db.person.find({"passwordHash": {"$regex": passwordHash, "$options": "$i"}},
                                          {"_id": 0}).limit(limitn).skip(skipn)
            datacnts = db.person.find({"passwordHash": {"$regex": passwordHash, "$options": "$i"}}, {"_id": 0}).count()

        # elif source:
        #     persons_info = db.person.find({"source": {"$regex": source, "$options":"$i"}}, {"_id": 0}).limit(limitn).skip(skipn)

        # elif xtime:
        #     persons_info = db.person.find({"xtime": {"$regex": xtime, "$options":"$i"}}, {"_id": 0}).limit(limitn).skip(skipn)

        else:
            # 限制只能查询10个
            persons_info = db.person.find({}, {"_id": 0, "update_time": 0}).limit(10)

        for person in persons_info:
            data.append(person)

        # 判断有无数据返回
        if data:
            return response_cors(data, datacnts, "ok")
        else:
            return response_cors(data, datacnts, "not found")

    def post(self):
        '''
        以json格式进行提交文档
        '''
        data = request.get_json()
        if not data:
            return {"response": "ERROR DATA"}
        else:
            user = data.get('user')
            email = data.get('email')

            if user and email:
                if db.person.find_one({"user": user, "email": email}, {"_id": 0}):
                    return {"response": "{{} {} already exists.".format(user, email)}
                else:
                    data.create_time = time.strftime('%Y%m%d', time.localtime(time.time()))
                    db.person.insert(data)
            else:
                return redirect(url_for("person"))

    # 暂时关闭高危操作
    # def put(self, user, email):
    #     '''
    #     根据user和email进行定位更新数据
    #     '''
    #     data = request.get_json()
    #     db.person.update({'user': user, 'email': email},{'$set': data},)
    #     return redirect(url_for("person"))

    # def delete(self, email):
    #     '''
    #     email作为唯一值, 对其进行删除
    #     '''
    #     db.person.remove({'email': email})
    #     return redirect(url_for("person"))


class Info(Resource):
    '''个人信息类'''

    def get(self, id=None, name=None, sex=None, qq=None, phonenumber=None):
        # 该处可能存在安全问题，做出限制会更好
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, help='Show [limitn] datas in one page')
        parser.add_argument('skip', type=int, help='Skip [skipn] datas')
        args = parser.parse_args()
        limitn = 10 if args['limit'] is None else args['limit']
        skipn = 0 if args['skip'] is None else args['skip']

        # data用于存储获取到的信息
        data = []
        datacnts = 0

        # 待改进
        if id:
            my_info = db.info.find({"id": id}, {"_id": 0}).limit(limitn).skip(
                skipn)
            datacnts = db.info.find({"id": id}, {"_id": 0}).count()

        elif name:
            my_info = db.info.find({"name": {"$regex": name, "$options": "$i"}}, {"_id": 0}).limit(
                limitn).skip(skipn)
            datacnts = db.info.find({"name": {"$regex": name, "$options": "$i"}}, {"_id": 0}).count()

        elif sex:
            my_info = db.info.find({"sex": {"$regex": sex, "$options": "$i"}}, {"_id": 0}).limit(
                limitn).skip(skipn)
            datacnts = db.info.find({"sex": {"$regex": sex, "$options": "$i"}}, {"_id": 0}).count()

        elif qq:
            my_info = db.info.find({"qq": qq},
                                   {"_id": 0}).limit(limitn).skip(skipn)
            datacnts = db.info.find({"qq": qq}, {"_id": 0}).count()

        elif phonenumber:
            my_info = db.info.find({"phonenumber": phonenumber},
                                   {"_id": 0}).limit(limitn).skip(skipn)
            datacnts = db.info.find({"phonenumber": phonenumber}, {"_id": 0}).count()

        else:
            # 限制只能查询10个
            my_info = db.info.find({}, {"_id": 0, "update_time": 0}).limit(10)

        for person in my_info:
            data.append(person)

        # 判断有无数据返回
        if data:
            return response_cors(data, datacnts, "ok")
        else:
            return response_cors(data, datacnts, "not found")

    def post(self):
        '''
        以json格式进行提交文档
        '''
        data = request.get_json()
        if not data:
            return {"response": "ERROR DATA"}
        else:
            user = data.get('user')
            email = data.get('email')

            if user and email:
                if db.person.find_one({"user": user, "email": email}, {"_id": 0}):
                    return {"response": "{{} {} already exists.".format(user, email)}
                else:
                    data.create_time = time.strftime('%Y%m%d', time.localtime(time.time()))
                    db.person.insert(data)
            else:
                return redirect(url_for("person"))

    # 暂时关闭高危操作
    # def put(self, user, email):
    #     '''
    #     根据user和email进行定位更新数据
    #     '''
    #     data = request.get_json()
    #     db.person.update({'user': user, 'email': email},{'$set': data},)
    #     return redirect(url_for("person"))

    # def delete(self, email):
    #     '''
    #     email作为唯一值, 对其进行删除
    #     '''
    #     db.person.remove({'email': email})
    #     return redirect(url_for("person"))


class Analysis(Resource):
    '''
    分析功能
    '''

    def get(self, type_analyze):
        '''
        type为分析类型，包括邮箱后缀、泄漏来源、泄漏时间
        type: [suffix_email, source, xtime, create_time]
        '''
        if type_analyze in ["source", "xtime", "suffix_email", "create_time"]:
            pipeline = [{"$group": {"_id": '$' + type_analyze, "sum": {"$sum": 1}}}]
            return response_cors(list(db.person.aggregate(pipeline)), None, "ok")

        else:
            return response_cors("use /api/analysis/[source, xtime, suffix_email] to get analysis data.", None, "error")


class Getselector(Resource):
    '''
    获取级联数据功能
    '''

    def get(self):
        '''
        type为分析类型，包括邮箱后缀、泄漏来源、泄漏时间
        type: [suffix_email, source, xtime, create_time]
        '''
        subject = [
            {
                "id": 1,
                "name": "账密",
                "select": "find",
                "obj": [
                    {
                        "id": 3,
                        "name": "用户名",
                        "select": "user"
                    },
                    {
                        "id": 4,
                        "name": "密码",
                        "select": "password"
                    },
                    {
                        "id": 5,
                        "name": "邮箱",
                        "select": "email"
                    },
                    {
                        "id": 6,
                        "name": "哈希密码",
                        "select": "passwordHash"
                    }
                ]
            },
            {
                "id": 2,
                "name": "身份信息",
                "select": "info",
                "obj": [
                    {
                        "id": 7,
                        "name": "手机号",
                        "select": "phonenumber"
                    },
                    {
                        "id": 8,
                        "name": "QQ",
                        "select": "qq"
                    },
                    {
                        "id": 9,
                        "name": "身份证",
                        "select": "id"
                    },
                    {
                        "id": 10,
                        "name": "姓名",
                        "select": "name"
                    }
                ]
            }
        ]
        return response_cors(subject, None, "ok")


# 添加api资源
api = Api(app)
api.add_resource(Person, "/api/find")
api.add_resource(Person, "/api/find/user/<string:user>", endpoint="user")
api.add_resource(Person, "/api/find/email/<string:email>", endpoint="email")
api.add_resource(Person, "/api/find/password/<string:password>", endpoint="password")
api.add_resource(Person, "/api/find/passwordHash/<string:passwordHash>", endpoint="passwordHash")
api.add_resource(Person, "/api/find/source/<string:source>", endpoint="source")
api.add_resource(Person, "/api/find/time/<string:xtime>", endpoint="xtime")
api.add_resource(Info, "/api/info")
api.add_resource(Info, "/api/info/id/<int:id>", endpoint="id")
api.add_resource(Info, "/api/info/name/<string:name>", endpoint="name")
api.add_resource(Info, "/api/info/sex/<string:sex>", endpoint="sex")
api.add_resource(Info, "/api/info/qq/<int:qq>", endpoint="qq")
api.add_resource(Info, "/api/info/phonenumber/<int:phonenumber>", endpoint="phonenumber")
api.add_resource(Analysis, "/api/analysis/<string:type_analyze>", endpoint="type_analyze")
api.add_resource(Getselector, "/api/get_selector")
#
# app.debug = False
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
