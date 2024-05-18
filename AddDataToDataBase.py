import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendance-961f2-default-rtdb.firebaseio.com/"

})

ref = db.reference('Students')

data = {
    "0405":
        {
            "name":"Trisha",
            "major":"Actress",
            "starting_year":2019,
            "total_attendance":6,
            "standing":"A",
            "year":4,
            "last_attendance_time": "2024-05-11 00:13:32"

        },

    "0905":
        {
            "name": "Vijay D",
            "major": "Actor",
            "starting_year": 2020,
            "total_attendance": 8,
            "standing": "B",
            "year": 3,
            "last_attendance_time": "2024-05-11 00:13:35"

        },
    "1207":
        {
            "name": "Harsha",
            "major": "Singer",
            "starting_year": 2023,
            "total_attendance": 7,
            "standing": "A",
            "year": 2,
            "last_attendance_time": "2024-05-11 00:13:38"

        },
   "0706":
        {
            "name": "Subhashree",
            "major": "Developer",
            "starting_year": 2023,
            "total_attendance": 0,
            "standing": "A",
            "year": 2,
            "last_attendance_time": "2024-05-11 00:17:11"

        },



}

for key, value in data.items():
    ref.child(key).set(value)