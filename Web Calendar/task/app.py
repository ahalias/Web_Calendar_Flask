from flask import Flask, request, make_response, jsonify, abort
import sys
from flask_restful import Api, inputs, reqparse
from flask_sqlalchemy import SQLAlchemy
import datetime



app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///name.db'

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)

db.create_all()


parser = reqparse.RequestParser()
parser.add_argument('event', type=str, help="The event name is required!", required=True)
parser.add_argument('date', type=inputs.date, help="The event date with the correct format is required! The correct format is YYYY-MM-DD!", required=True)


@app.route('/event', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        query_params = request.args
        start = query_params.get('start_time')
        end = query_params.get('end_time')
        if not start:
            events = Events.query.all()
            events_list = [{"id": e.id, "event": e.event, "date": str(e.date)} for e in events]
            return jsonify(events_list)
        else:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
            today_events = Events.query.filter(Events.date.between(start_date, end_date)).all()
        if today_events:
            events = [{"id": event.id, "event": event.event, "date": str(event.date)} for event in today_events]
            return make_response(jsonify(events), 200)
        else:
            abort(404, "The event doesn't exist!")
    if request.method == "POST":
        args = parser.parse_args()
        event = Events(event=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()
        response_body = {
    "message": "The event has been added!",
    "event": args['event'],
    "date": args['date'].strftime('%Y-%m-%d')
}
        return make_response(jsonify(response_body), 200)


@app.route('/event/today')
def today_events():
    if request.method == "GET":
        today_events = Events.query.filter(Events.date==datetime.date.today()).all()
        if today_events:
            today_events_list = [{"id": event.id, "event": event.event, "date": str(event.date)} for event in today_events]
            return make_response(jsonify(today_events_list), 200)


@app.route('/event/<int:id>', methods=["GET", "DELETE"])
def events_by_date(id):
    msg = {"message": "The event doesn't exist!"}
    if request.method == "GET":
        event = Events.query.filter(Events.id==id).first()
        if event:
            event = {"id": event.id, "event": event.event, "date": str(event.date)}
            return make_response(jsonify(event), 200)
        else:
            return make_response(jsonify(msg), 404)
    if request.method == "DELETE":
        delete_event = Events.query.filter(Events.id==id).all()
        if delete_event:
            for event in delete_event:
                db.session.delete(event)
                db.session.commit()
                response = {"message": "The event has been deleted!"}
                return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify(msg), 404)



@app.errorhandler(400)
def bad_request(e):
    return make_response(jsonify({"message": e.data['message']}), 400)




# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(host='0.0.0.0', port=3333)
