import os
import pickle
import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime, timedelta
import pandas as pd

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://attd-track-default-rtdb.firebaseio.com/",
    "storageBucket": "attd-track.appspot.com"
})

bucket = storage.bucket()

# Function to fetch data from Firebase
def fetch_data_from_firebase():
    try:
        employees_ref = db.reference('Employees')
        employees_data = employees_ref.get()

        if employees_data:
            return employees_data
        else:
            print("No data found in Firebase.")
            return None

    except Exception as e:
        print(f"Error fetching data from Firebase: {e}")
        return None

# Function to write scanned employees data to Excel
def write_scanned_employees_to_excel(excel_file_path, scanned_employees):
    try:
        # Convert scanned_employees list to DataFrame
        new_data = pd.DataFrame(scanned_employees)

        # Check if the Excel file already exists
        if os.path.exists(excel_file_path):
            existing_data = pd.read_excel(excel_file_path)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = new_data

        # Write updated data to Excel file
        updated_data.to_excel(excel_file_path, index=False)
        print(f"Scanned employees data successfully written to {excel_file_path}")

    except Exception as e:
        print(f"Error writing scanned employees data to Excel: {e}")

# Path to your Excel file for scanned employees
excel_file_path = 'C:\\Users\\shiri\\OneDrive\\Desktop\\fs.xlsx'

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Could not open video device")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Load images and other resources
imgBackground = cv2.imread('C:\\Users\\shiri\\OneDrive\\Desktop\\Attendance\\Resources\\bg_visiotrack.png')
folderModePath = 'C:\\Users\\shiri\\OneDrive\\Desktop\\Attendance\\Resources\\modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]
imgModeList[1] = cv2.resize(imgModeList[1], (429, 583))
imgModeList[2] = cv2.resize(imgModeList[2], (429, 583))

# Load the encoding file
print("Loading encode file...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, employeeIds = encodeListKnownWithIds
print("Encode file loaded!")

modeType = 0
counter = 0
id = -1
imgEmployee = None  # Initialize imgEmployee to None initially

# List to store scanned employees data
scanned_employees = []

# Fetch employee data from Firebase
employees_data = fetch_data_from_firebase()

last_detection = {}

# Cooldown period in seconds
cooldown_period = 60

while True:
    # Capture the frame
    ret, img = cap.read()

    # Check if the image was successfully captured
    if not ret or img is None:
        print("Failed to capture image, retrying...")
        continue

    if imgBackground is None:
        print("Failed to load background image.")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[220:220 + 480, 55:55 + 640] = cv2.resize(img, (640, 480))
    imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]

    if employees_data:  # Check if employees_data is not None
        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = employeeIds[matchIndex]

                    # Check if employee is scanned and marked


                # Update UI or modeType based on your application logic here
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Visio Track", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                employeeInfo = employees_data.get(id)
                if employeeInfo:
                    current_time = datetime.now()
                    last_detected_time = last_detection.get(id, current_time - timedelta(seconds=cooldown_period))
                    time_diff = (current_time - last_detected_time).total_seconds()

                    if time_diff >= cooldown_period:
                        # Update attendance details
                        ref = db.reference(f'Employees/{id}')
                        #employees_data[id]['no_of_clients_visited'] += 1
                        employees_data[id]['last_client_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

                        # Update Firebase with both fields
                        ref.update({
                            #'no_of_clients_visited': employees_data[id]['no_of_clients_visited'],
                            'Last Client Visit Time': employees_data[id]['last_client_time'],
                            'scanned': True
                        })

                        # Append scanned employee data (updated)
                        scanned_employees.append({
                            'EmpID': id,
                            'Username': employees_data[id]['Username'],
                            'Designation': employees_data[id]['Designation'],
                            'Department': employees_data[id]['Department'],
                            #'no_of_clients_visited': employees_data[id]['no_of_clients_visited'],
                            'Last Client Visit Time': employees_data[id]['last_client_time']
                            # Use current_time if needed
                        })
                        last_detection[id] = current_time

                    blob = bucket.get_blob(f'Images/{id}.jpg')
                    if blob:
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgEmployee = cv2.imdecode(array, cv2.IMREAD_COLOR)
                        if imgEmployee is not None:
                            imgEmployee = cv2.resize(imgEmployee, (200, 160))
                        else:
                            print(f"Failed to decode image for employee ID: {id}")
                            continue

                        secondsElapsed = (datetime.now() - datetime.strptime(employeeInfo['Last Client Visit Time'], "%Y-%m-%d %H:%M:%S")).total_seconds()
                        if secondsElapsed > 30:
                            ref = db.reference(f'Employees/{id}')
                            #employeeInfo['no_of_clients_visited'] += 1
                            #ref.child('no_of_clients_visited').set(employeeInfo['no_of_clients_visited'])
                            ref.child('Last Client Visit Time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            modeType = 3
                            counter = 0
                            imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2

                imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]

                if counter <= 10 and employeeInfo:
                    #cv2.putText(imgBackground, str(employeeInfo['no_of_clients_visited']), (870, 177),
                               #cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)

                    cv2.putText(imgBackground, str(employeeInfo['Designation']), (1036, 555),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)

                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)

                    cv2.putText(imgBackground, str(employeeInfo['Department']), (1138, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)

                    (w, h), _ = cv2.getTextSize(employeeInfo['Username'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(employeeInfo['Username']), (867 + offset, 455),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 1)

            counter += 1

    cv2.imshow("Visio Track", imgBackground)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Write scanned employees data to Excel file
write_scanned_employees_to_excel(excel_file_path, scanned_employees)

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
