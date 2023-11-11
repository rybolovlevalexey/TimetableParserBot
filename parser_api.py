from flask import Flask
from flask_restful import Api, Resource, reqparse
from models import WebUser, GroupDirection
from parsing import week_timetable_dict

app = Flask(__name__)
api = Api()


class BaseSchedule(Resource):
    def get(self, user_name):
        db_result = WebUser.select().where(WebUser.login == user_name)
        if db_result.count() == 0:
            return {"user_name": user_name, "response": "User not found"}
        user_group = list(elem.group_name for elem in db_result)[0]
        group_url = list(elem.url for elem in GroupDirection.select().\
            where(GroupDirection.group_name == user_group))[0]
        return week_timetable_dict(group_url)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("group", type=str)
        args = parser.parse_args()

        if WebUser.select(WebUser.group_name).where(WebUser.login == args["name"]).count() == 0:
            WebUser.create(login=args["name"], group_name=args["group"])
        else:
            WebUser.update(group_name=args["group"]).where(WebUser.login == args["name"]).execute()
        return {"done": True}


api.add_resource(BaseSchedule, "/api", "/api/<string:user_name>")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=3000)
