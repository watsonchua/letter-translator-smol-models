from services.client import jigsaw_client


text = """
- Step 1: Log in to the app and select "Profile."
- Step 2: On the "Profile" page, verify contact details or tap options to update:
  - "Edit" for mailing address
  - "Change mobile number"
  - "Change User ID/Email address" 
"""
result = jigsaw_client.translate({"text": text, "target_language":"zh", "current_language":"en" })
print(result)

