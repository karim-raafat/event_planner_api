from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
import base64

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'event_planner'
app.config['PORT'] = '3306'

mysql = MySQL(app)
CORS(app)


@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if data is None:
            return jsonify('No data provided'), 400

        email = request.json['email']
        password = request.json['password']
        name = request.json['username']

        if not email or not password:
            return jsonify('Missing required fields'), 400

        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM users WHERE UserEmail = %s"
        val = (email,)
        cursor.execute(sql, val)
        if cursor.fetchone():
            return jsonify('Email already exists'), 400

        sql = "INSERT INTO users (UserEmail,UserPassword,Username) VALUES (%s, %s,%s)"
        val = (email, password, name)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return jsonify('User created successfully'), 200

    except Exception as e:
        return jsonify('An error has occured'), 500


@app.route('/users', methods=['GET'])
def login():
    try:
        email = request.args.get('email')
        password = request.args.get('password')

        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM users WHERE UserEmail = %s"
        val = (email,)
        cursor.execute(sql, val)
        response = cursor.fetchone()

        if response is not None:
            if (password == response[3]):
                if (response[4] is not None) and (len(response[4]) > 1):
                    return jsonify(
                        {'status': 'Login Successful', 'id': response[0], 'username': response[1], 'email': response[2],
                         'password': response[3],
                         'profile picture': base64.b64encode(response[4]).decode('utf-8')}), 200
                else:
                    return jsonify(
                        {'status': 'Login Successful', 'id': response[0], 'username': response[1], 'email': response[2],
                         'password': response[3], 'profile picture': 'none'}), 200
        else:
            return jsonify('Login failed'), 400
    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/users', methods=['PATCH'])
def update_user_info():
    try:
        id = request.json['id']
        username = request.json['username']
        password = request.json['password']
        base64_image = request.json['image']
        cursor = mysql.connection.cursor()

        image = base64.b64decode(base64_image)

        sql = "UPDATE users SET Username =%s ,UserPassword = %s,ProfilePicture = %s WHERE UserID = %s"
        val = (username, password, image, id,)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return jsonify('Profile updated Successfully'), 200

    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/events', methods=['GET'])
def getAllEvents():
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM events"
        cursor.execute(sql)

        response = cursor.fetchall()
        r = []
        for data in response:
            if data[7] and len(data[7]) > 5:
                r.append({'eventID': data[0],
                          'eventHost': data[1],
                          'eventName': data[2],
                          'eventDate': data[3],
                          'eventTime': data[4],
                          'eventAddress': data[5],
                          'eventDescription': data[6],
                          'eventImage': base64.b64encode(data[7]).decode('utf8'),
                          })
            else:
                r.append({'eventID': data[0],
                          'eventHost': data[1],
                          'eventName': data[2],
                          'eventDate': data[3],
                          'eventTime': data[4],
                          'eventAddress': data[5],
                          'eventDescription': data[6],
                          })

        return jsonify(r), 200
    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/my_events', methods=['GET'])
def getMyEvents():
    try:
        user_id = request.args.get('id')
        cursor = mysql.connection.cursor()
        sql = "SELECT * FROM events WHERE EventHost = %s"
        val = (user_id,)
        cursor.execute(sql, val)
        response = cursor.fetchall()
        r = []
        for data in response:
            if data[7] and len(data[7]) > 5:
                r.append({'eventID': data[0],
                          'eventHost': data[1],
                          'eventName': data[2],
                          'eventDate': data[3],
                          'eventTime': data[4],
                          'eventAddress': data[5],
                          'eventDescription': data[6],
                          'eventImage': base64.b64encode(data[7]).decode('utf8'),
                          })
            else:
                r.append({'eventID': data[0],
                          'eventHost': data[1],
                          'eventName': data[2],
                          'eventDate': data[3],
                          'eventTime': data[4],
                          'eventAddress': data[5],
                          'eventDescription': data[6],
                          })

        return jsonify(r), 200


    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/events', methods=["POST"])
def addEvent():
    try:
        cursor = mysql.connection.cursor()

        host = request.json['host']
        name = request.json['name']
        date = request.json['date']
        time = request.json['time']
        address = request.json['address']
        description = request.json['description']
        base64_image = request.json['image']
        base64_media = request.json['media']

        image = base64.b64decode(base64_image)

        sql = "INSERT INTO events (EventHost,EventName,EventDate,EventTime,EventAddress,EventDescription,EventMainPhoto) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (host, name, date, time, address, description, image,)
        cursor.execute(sql, val)

        if len(base64_media) != 0:
            sql = "SELECT MAX(EventID) FROM events"
            cursor.execute(sql)
            event_id = cursor.fetchone()[0]
            for base64Image in base64_media:
                image = base64.b64decode(base64Image)
                cursor.execute("INSERT INTO event_media (EventID,Photo) VALUES (%s,%s)", (event_id, image,), )

        mysql.connection.commit()

        return jsonify('Event added Successfully'), 200
    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/my_events', methods=["DELETE"])
def delete_event():
    try:
        event_id = request.args.get('id')
        cursor = mysql.connection.cursor()

        sql = "DELETE FROM events WHERE EventID = %s"
        val = (event_id,)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return jsonify('Event Deleted Successfully'), 200

    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/events', methods=['PATCH'])
def update_event():
    try:
        cursor = mysql.connection.cursor()
        id = request.json['id']
        name = request.json['name']
        date = request.json['date']
        time = request.json['time']
        address = request.json['address']
        description = request.json['description']
        base64_image = request.json['image']
        media = request.json['media']

        image = base64.b64decode(base64_image)

        sql = "UPDATE events SET EventName = %s, EventDate = %s, EventTime = %s, EventAddress = %s, EventDescription = %s, EventMainPhoto = %s WHERE EventID = %s"
        val = (name, date, time, address, description, image, id,)
        cursor.execute(sql, val)
        if len(media) != 0:
            for image in media:
                cursor.execute("SELECT photo FROM event_media WHERE photo = %s AND EventID = %s", (image, id,))
                response = cursor.fetchone()
                if response:
                    cursor.execute("UPDATE event_media SET photo = %s, WHERE ImageID = %s", (image, response[0],))
                else:
                    cursor.execute("INSERT INTO event_media (EventID,Photo) VALUES (%s,%s)", (id, image,))

        mysql.connection.commit()

        return jsonify('Event updated Successfully'), 200

    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/guests', methods=['POST'])
def addGuests():
    try:
        user_id = request.json['userID']
        event_id = request.json['eventID']
        status = request.json['status']
        kidsNo = request.json['kidsNo']
        adultsNo = request.json['adultsNo']
        cursor = mysql.connection.cursor()

        sql = "SELECT * FROM guests WHERE UserID = %s AND EventID = %s"
        val = (user_id, event_id,)
        cursor.execute(sql, val)
        if cursor.fetchone():
            sql = "UPDATE guests SET KidsNo=%s,AdultsNo=%s,GuestStatus=%s WHERE UserID = %s AND EventID = %s"
            val = (kidsNo, adultsNo, status, user_id, event_id,)
            cursor.execute(sql, val)

        else:
            sql = "INSERT INTO guests (UserId, EventID, KidsNo,AdultsNo, GuestStatus) VALUES (%s,%s,%s,%s,%s)"
            val = (user_id, event_id, kidsNo, adultsNo, status,)
            cursor.execute(sql, val)

        mysql.connection.commit()
        return jsonify("RSVP updated successfully"), 200

    except Exception as e:
        print(e)
        return jsonify('An error has occurred'), 500


@app.route('/guests', methods=['GET'])
def get_guest_info():
    try:
        cursor = mysql.connection.cursor()
        userID = request.args.get('userID')
        eventID = request.args.get('eventID')

        sql = "SELECT GuestStatus,KidsNo,AdultsNo FROM guests WHERE UserID = %s AND EventID = %s "
        val = (userID, eventID,)
        cursor.execute(sql, val)
        response = cursor.fetchone()
        if (response):
            return jsonify({'status': response[0], 'kidsNo': response[1], 'adultsNo': response[2]}), 200
        else:
            return jsonify({'status': 'Going', 'kidsNo': 0, 'adultsNo': 0})



    except Exception as e:
        print(e)
        return jsonify('An error has occurred'), 500


@app.route('/host', methods=['GET'])
def get_host():
    try:
        id = request.args.get('id')
        cursor = mysql.connection.cursor()

        sql = "SELECT * FROM users WHERE UserID = %s"
        val = (id,)
        cursor.execute(sql, val)
        response = cursor.fetchone()
        return jsonify(response), 200

    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/event_media', methods=['GET'])
def get_event_media():
    try:
        event_id = request.args.get('id')
        cursor = mysql.connection.cursor()

        sql = "SELECT Photo FROM event_media WHERE EventID = %s"
        val = (event_id,)
        cursor.execute(sql, val)
        response = cursor.fetchall()
        r = []
        for base64_image in response:
            r.append(base64.b64encode(base64_image[0]).decode('utf8'))

        return jsonify(r), 200

    except Exception as e:
        return jsonify('An error has occurred'), 500


@app.route('/event_guests', methods=['GET'])
def getAllGuests():
    try:
        cursor = mysql.connection.cursor()

        eventID = request.args.get('eventID')

        sql = "SELECT * FROM guests G, users U WHERE G.EventID = %s AND G.UserID = U.UserID"
        val = (eventID,)

        cursor.execute(sql, val)
        response = cursor.fetchall()
        r= []
        for data in response:
            if data[9]:
                r.append({'userID': data[0],
                          'eventID': data[1],
                          'guestStatus': data[2],
                          'kidsNo': data[3],
                          'adultsNo': data[4],
                          'username': data[6],
                          'userImage': base64.b64encode(data[9]).decode('utf8'),
                          })
            else:
                r.append({'userID': data[0],
                          'eventID': data[1],
                          'guestStatus': data[2],
                          'kidsNo': data[3],
                          'adultsNo': data[4],
                          'username': data[6],
                          })

        return jsonify(r),200

    except Exception as e:
        print(e)
        return jsonify('An error has occurred'), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
