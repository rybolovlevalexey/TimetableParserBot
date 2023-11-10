from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api()


class BaseSchedule(Resource):
    def get(self, user_name):
        return user_name

    def post(self, user_name, user_group):
        pass


api.add_resource(BaseSchedule, "/api/<string:user_name>")
api.add_resource(BaseSchedule, "/api/<string:user_name>/<string:user_group>")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=3000)
