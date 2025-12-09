import json
import threading



from flask import Flask,make_response,request,jsonify,abort
from activity import Chaoxing_activity,SharedData,Chaoxing_transcript

class Backend_web:
    """后端服务器类"""
    def __init__(self,shared_data) -> None:
        self.app = Flask(__name__)
        self._register_routes()
        self.shared_data = shared_data
    def cors_headers(self,response) ->dict:
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return response
    
    def _register_routes(self) -> None:
        @self.app.after_request
        def after_request(response:dict)->dict:
            """在每个请求后自动添加 CORS 头部"""
            return self.cors_headers(response)


        @self.app.route('/')
        def home():
            return "Hello?"


        @self.app.route('/status')
        def ret_status():
            if self.shared_data.get_status() == "Done":
                status = {"status":"complete",
                          "complete":True,
                          "session":self.shared_data.get_session()}
            else:
                status = {"status":"working",
                          "current_work":self.shared_data.get_current_work(),
                          "current_quantity":self.shared_data.get_current_quantity(),
                          "quantity":self.shared_data.get_quantity(),
                          "complete":False,
                          "session":self.shared_data.get_session()}
            return jsonify(json.dumps(status))

        @self.app.route('/data', methods=['GET', 'OPTIONS'])
        def data():
            status_code = 202
            if request.method == "OPTIONS":
                headers =  self.cors_headers(make_response())
                return headers
            
            if self.shared_data.get_status() == "Done":
                status_code = 200
            activity_list = self.shared_data.get_data_json()

            response = {"code":status_code,
                        "data":activity_list,
                        "session":self.shared_data.get_session()
                        }
            return jsonify(json.dumps(response))
        
        @self.app.route('/service',methods=['POST'])
        def service():
            code = 500
            data = request.get_data(as_text=True)
            json_text = json.loads(data)
            need_service = json_text['use']
            if need_service == "get_activity":
                self.shared_data.reload()
                self.shared_data.set_session("get_activity")
                data_threading = threading.Thread(target=activity_exam.run_request)
                data_threading.start()
                code = 200
            elif need_service == "transcript":
                self.shared_data.reload()
                self.shared_data.set_session("transcript")
                data_threading = threading.Thread(target=activity_Transcript.run_request)
                data_threading.start()
                code = 200
            else:
                abort(400)

            return jsonify(json.dumps({'code':code}))
            

    def run_app(self):
        self.app.run(port=5000)


if __name__ == "__main__":
    running_code = 1
    shared_data = SharedData()

    activity_exam = Chaoxing_activity(shared_data)
    activity_Transcript = Chaoxing_transcript(shared_data)
    if running_code:
        backend_exam = Backend_web(shared_data)
        web_threading = threading.Thread(target=backend_exam.run_app)

        # TIPS:flask需要为主线程才能debug
        web_threading.run()
    else:
        activity_exam.run_request()

