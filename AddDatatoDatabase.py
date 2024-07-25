import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attd-track-default-rtdb.firebaseio.com/"
})

ref = db.reference('Employees')

# Adding the data
data = {
    'E001':
        {
            "Username": "Abhinandana Polepally",
            "Designation": "SE",
            "Department": "Developer",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E002':
        {
            "Username": "Sri Harshini Gumpula",
            "Designation": "DS",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E003':
        {
            "Username": "Varsha Peddi",
            "Designation": "ML",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E004':
        {
            "Username": "Sampelly Shirisha",
            "Designation": "AI",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E005':
        {
            "Username": "Dheeraj Manchala",
            "Designation": "Developer",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E006':
        {
            "Username": "Sravani Varanganti",
            "Designation": "DE",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E007':
        {
            "Username": "Neha Myneni",
            "Designation": "Trainee",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        },
    'E008':
        {
            "Username": "Nihanth Keesara",
            "Designation": "Senior SE",
            "Department": "CSE-AI&ML",
            "no_of_clients_visited": 0,
            "Last Client Visit Time": "2024-04-12 00:50:48"
        }
}

# Adds data to the real-time database
for key,value in data.items():
    ref.child(key).set(value)
