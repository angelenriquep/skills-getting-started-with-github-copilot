"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import os
from pymongo import MongoClient
from typing import Dict, Any

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['mergington_high']
activities_collection = db['activities']

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initial activities data
initial_activities = {
    "Chess Club": {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "name": "Basketball Club",
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "name": "Drama Club",
        "description": "Act in plays and participate in drama workshops",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Workshop": {
        "name": "Art Workshop",
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Math Club": {
        "name": "Math Club",
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Science Olympiad": {
        "name": "Science Olympiad",
        "description": "Participate in science challenges and experiments",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["jack@mergington.edu", "harper@mergington.edu"]
    }
}

# Initialize database with activities if empty
if activities_collection.count_documents({}) == 0:
    for activity in initial_activities.values():
        activities_collection.insert_one(activity)

@app.get("/")
def root():
    """Redirect to the static index.html file"""
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
def get_activities():
    """Get all activities"""
    activities = {}
    cursor = activities_collection.find({})
    for doc in cursor:
        doc.pop('_id')  # Remove MongoDB's _id field
        activities[doc['name']] = doc
    return activities

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count:
        return {"message": f"Signed up {email} for {activity_name}"}
    else:
        raise HTTPException(status_code=400, detail="Failed to sign up")

@app.post("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Find the activity
    activity = activities_collection.find_one({"name": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered")

    # Remove student
    result = activities_collection.update_one(
        {"name": activity_name},
        {"$pull": {"participants": email}}
    )
    
    if result.modified_count:
        return {"message": f"Removed {email} from {activity_name}"}
    else:
        raise HTTPException(status_code=400, detail="Failed to unregister")
