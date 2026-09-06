import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("EMAIL_ADDRESS", "").strip()
password = os.getenv("EMAIL_APP_PASSWORD", "").replace(" ", "").strip()

print("Email loaded:", email)
print("Password length:", len(password))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email, password)

    print("SUCCESS: Gmail SMTP authentication works!")

except Exception as e:
    print("FAILED: Gmail SMTP authentication does not work.")
    print(e)