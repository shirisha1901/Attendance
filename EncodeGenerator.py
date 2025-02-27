import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attd-track-default-rtdb.firebaseio.com/",
    "storageBucket":"attd-track.appspot.com"
})

# Importing the employee images into list.
folderPath = 'C:\\Users\\shiri\\pycharm\\viscotrack\\face-recognition\\Images'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
employeeIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    employeeIds.append(os.path.splitext(path)[0])

    # Uploading images to Firebase Storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(employeeIds)

def findEncodings(imagesList):
    encodeList=[]
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds=[encodeListKnown,employeeIds]
print("Encoding Complete")

# Generating pickle file
file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")
