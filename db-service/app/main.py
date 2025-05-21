from firestore.client import FirestoreClient
from models import UserProfile, UserSettings, Event, EventResource, AiSuggestion
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def main():
    try:
        # Initialize Firestore client
        print("Initializing Firestore client...")
        client = FirestoreClient()

        # Example: Add a user profile
        print("\nAdding user profile...")
        user_profile = UserProfile(
            id="user123",
            displayName="Ali Student",
            email="ali.student@example.com",
            role="student",
            school="University of Example",
            preferences={"notification_method": "email", "study_hours": "9am-5pm"},
            avatarUrl=None  # Set to None to avoid HttpUrl validation
        )
        user_id = client.add("users", user_profile)
        print(f"User profile added with ID: {user_id}")

        # Example: Add user settings
        print("\nAdding user settings...")
        user_settings = UserSettings(
            studyMode="focus",
            academicYear="2023-2024",
            notificationPreferences={"email": True, "sms": False, "push": True}
        )
        settings_id = client.add("user_settings", user_settings, document_id=user_id)
        print(f"User settings added with ID: {settings_id}")

        # Example: Add an event
        print("\nAdding event...")
        event_resource = EventResource(
            aiRecommended=True,
            category="lecture",
            location="Room 101"
        )
        event = Event(
            id="event123",
            userId=user_id,
            title="Introduction to AI",
            start=datetime.utcnow(),
            end=datetime.utcnow() + timedelta(hours=2),
            resource=event_resource
        )
        event_id = client.add("events", event)
        print(f"Event added with ID: {event_id}")

        # Example: Add an AI suggestion
        print("\nAdding AI suggestion...")
        ai_suggestion = AiSuggestion(
            id="suggestion123",
            userId=user_id,
            description="Consider scheduling a study group for AI lecture",
            context="exam prep",
            priority=3
        )
        suggestion_id = client.add("ai_suggestions", ai_suggestion)
        print(f"AI suggestion added with ID: {suggestion_id}")

        print("\nAll data added successfully!")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
