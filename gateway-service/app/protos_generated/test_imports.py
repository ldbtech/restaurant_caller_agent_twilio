# app/protos_generated/test_imports.py
import sys
import os

print(f"--- Running Test from: {__file__} ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Directory of this test script: {os.path.dirname(__file__)}")
print(f"Contents of 'app/protos_generated/': {os.listdir(os.path.dirname(__file__))}")
print(f"Python sys.path:")
for p in sys.path:
    print(f"  - {p}")
print("--- Attempting Import ---")

try:
    import db_service_pb2
    print("SUCCESS: 'import db_service_pb2' worked!")
    print(f"Type of db_service_pb2: {type(db_service_pb2)}")
    # Try to access something from it to be sure
    if hasattr(db_service_pb2, 'UserProfileRequest'):
        print("Found UserProfileRequest in db_service_pb2.")
    else:
        print("UserProfileRequest NOT FOUND in db_service_pb2 (this is unexpected).")
    if hasattr(db_service_pb2, 'DESCRIPTOR'):
        print("Found DESCRIPTOR in db_service_pb2.")
    else:
        print("DESCRIPTOR NOT FOUND in db_service_pb2 (this is unexpected).")

except ImportError as e:
    print(f"FAILURE: 'import db_service_pb2' FAILED.")
    print(f"ImportError: {e}")
except Exception as e_other:
    print(f"FAILURE: An unexpected error occurred during import.")
    print(f"Error: {e_other}")

print("--- Test Complete ---")