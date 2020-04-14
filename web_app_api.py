from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
import hashlib
import binascii
import datetime
import sqlite3
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cyan_web_app_db.sqlite3")


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    password_hex = binascii.hexlify(password_hash)
    password_salted = (salt + password_hex).decode('ascii')
    return password_salted


def test_password(password_0, password_1):
    salt = password_0[:64]
    password_1_hash = hashlib.pbkdf2_hmac('sha512', password_1.encode('utf-8'), salt.encode('ascii'), 100000)
    password_1_hex = binascii.hexlify(password_1_hash).decode('ascii')
    return password_0[64:] == password_1_hex


def query_database(query, values):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute(query, values)
    except sqlite3.Error:
        conn.close()
        return {"error": "Error accessing database"}
    results = c.fetchall()
    conn.commit()
    conn.close()
    return results


@csrf_exempt
def register_user(request):
    if request.POST:
        post = request.POST.dict()
    else:
        post = json.loads(request.body.decode('utf-8'))
    try:
        user = post['user']
        email = post['email']
        password = post['password']
    except KeyError:
        return JsonResponse({"error": "Invalid key in request"}, status=200)
    query = 'SELECT * FROM User WHERE username = ?'
    values = (user,)
    users = query_database(query, values)
    if len(users) != 0:
        return JsonResponse({"error": "Username already exists"}, status=200)
    else:
        date = datetime.date.today().isoformat()
        password_salted = hash_password(password)
        query = 'INSERT INTO User(username, email, password, created, last_visit) VALUES (?, ?, ?, ?, ?)'
        values = (user, email, password_salted, date, date,)
        register = query_database(query, values)
        return JsonResponse({"status": "success", "username": user, "email": email}, status=200)


@csrf_exempt
def login_user(request):
    post = json.loads(request.body.decode('utf-8'))
    try:
        user = post['user']
        password = post['password']
    except KeyError:
        return JsonResponse({"error": "Invalid key in request"}, status=200)
    query = 'SELECT username, email, password, created FROM User WHERE username = ?'
    values = (user,)
    users = query_database(query, values)
    if len(users) == 0:
        return JsonResponse({"error": "Invalid user credentials."}, status=200)
    elif type(users) is dict:
        if "error" in users.keys():
            return JsonResponse(users, status=200)
        else:
            return HttpResponse(status=200)
    else:
        date = users[0][3]
        if not test_password(users[0][2], password):
            return JsonResponse({"error": "Invalid password"}, status=200)
        query = 'SELECT * FROM Location WHERE owner = ?'
        values = (user,)
        locations = query_database(query, values)
        data = []
        try:
            users = users[0]
            user_data = {
                "username": users[0],
                "email": users[1]
            }
            for location in locations:
                loc_data = {
                    "owner": location[0],
                    "id": location[1],
                    "name": location[2],
                    "latitude": location[3],
                    "longitude": location[4],
                    "marked": location[5],
                    "notes": location[6]
                }
                data.append(loc_data)
            return JsonResponse({'user': user_data, 'locations': data})
        except KeyError:
            return JsonResponse({"error": "Invalid key in database data"}, status=200)


@csrf_exempt
@require_POST
def add_location(request):
    post = json.loads(request.body.decode('utf-8'))
    try:
        user = post['owner']
        _id = post['id']
        name = post['name']
        latitude = post['latitude']
        longitude = post['longitude']
        marked = post['marked']
        notes = post['notes']               # array of strings in json format
    except KeyError:
        return JsonResponse({"error": "Invalid key in request"}, status=200)
    query = 'INSERT INTO Location(owner, id, name, latitude, longitude, marked, notes) VALUES (?, ?, ?, ?, ?, ?, ?)'
    values = (user, _id, name, latitude, longitude, marked, notes,)
    location = query_database(query, values)
    if type(location) is dict:
        if "error" in location.keys():
            return JsonResponse({"error": "Specified location for this user already exists"}, status=200)
        else:
            return HttpResponse(status=201)
    else:
        return HttpResponse(status=201)


@require_GET
def delete_location(request, user='', _id=''):
    query = 'DELETE FROM Location WHERE id = ? AND owner = ?'
    values = (_id, user,)
    delete = query_database(query, values)
    if type(delete) is dict:
        if "error" in delete.keys():
            return JsonResponse({"error": "Error accessing database"}, status=200)
        else:
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=200)


@csrf_exempt
@require_POST
def edit_location(request):
    post = json.loads(request.body.decode('utf-8'))
    try:
        user = post['owner']
        _id = post['id']
        name = post['name']
        marked = post['marked']
        notes = post['notes']               # array of strings in json format
    except KeyError:
        return JsonResponse({"error": "Invalid key in request"}, status=200)
    query = 'UPDATE Location SET name = ?, marked = ?, notes = ? WHERE owner = ? AND id = ?'
    values = (name, marked, notes, user, _id,)
    location = query_database(query, values)
    return HttpResponse(status=200)
