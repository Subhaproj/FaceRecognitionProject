import os
import pickle
import cv2
import cvzone
import face_recognition
import numpy as np

import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import storage
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendance-961f2-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-961f2.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# importing modes Images into list:
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
 # print(len(imgModeList))

 # load the encoding file
print("Loading Encode File.....")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[70:70 + 572, 835:835 + 392] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
           matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
           faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
           # print("matches", matches)
           # print("faceDis", faceDis)

           matchIndex = np.argmin(faceDis)
           # print("Match Index", matchIndex)




        if matches[matchIndex]:
            # print("Known Face Detected")
            # print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]
            if counter == 0:
                cvzone.putTextRect(imgBackground, "Loading",(275,400))
                cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(1)
                counter = 1
                modeType = 1

        if counter != 0:

            if counter == 1:
               # Get the data
               studentInfo = db.reference(f'Students/{id}').get()
               print(studentInfo)
               # get the Image from the storage
               blob = bucket.get_blob(f'Images/{id}.png')
               array = np.frombuffer(blob.download_as_string(), np.uint8)
               imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2RGB)
               # update data of attendance
               datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                               "%Y-%m-%d %H:%M:%S")
               secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
               print(secondsElapsed)
               if secondsElapsed > 30:
                  ref = db.reference(f'Students/{id}')
                  studentInfo['total_attendance'] += 1
                  ref.child('total_attendance').set(studentInfo['total_attendance'])
                  ref.child('total_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
               else:
                    modeType = 3
                    counter = 0
                    imgBackground[70:70 + 572, 835:835 + 392] = imgModeList[modeType]




            if modeType != 3:

                if 10 < counter < 20:
                   modeType = 2

                imgBackground[70:70 + 572, 835:835 + 392] = imgModeList[modeType]

                if counter <= 10:
                   cv2.putText(imgBackground, str(studentInfo['total_attendance']), (900, 120),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
                   cv2.putText(imgBackground, str(studentInfo['major']), (1040, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.55, (0, 0, 0), 2)
                   cv2.putText(imgBackground, str(studentInfo['standing']), (910, 620),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
                   cv2.putText(imgBackground, str(studentInfo['year']), (1020, 620),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
                   cv2.putText(imgBackground, str(studentInfo['starting_year']), (1110, 620),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
                   cv2.putText(imgBackground, str(id), (1030, 490),
                            cv2.FONT_HERSHEY_COMPLEX, 0.90, (0, 0, 0), 2)

                   (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                   offset = (414 - w) // 2
                   cv2.putText(imgBackground, str(studentInfo['name']), (810 + offset, 420),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

                   imgBackground[162:162 + 220, 925:925 + 220] = imgStudent

                counter += 1

                if counter >= 20:
                   counter = 0
                   modeType = 0
                   studentInfo = []
                   imgStudent = []
                   imgBackground[70:70 + 572, 835:835 + 392] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0



    # cv2.imshow("webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

