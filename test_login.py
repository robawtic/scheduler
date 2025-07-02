import requests
import json

# Base URL of the API
base_url = "http://localhost:8080"

# CSRF token endpoint
csrf_url = f"{base_url}/csrf-token"

# Login endpoint
login_url = f"{base_url}/auth/token"

# Test credentials
username = "testuser"
password = "password"

def test_login():
    # Step 1: Get CSRF token
    print("Fetching CSRF token...")
    csrf_response = requests.get(csrf_url)

    if csrf_response.status_code != 200:
        print(f"Failed to get CSRF token. Status code: {csrf_response.status_code}")
        print(f"Response: {csrf_response.text}")
        return False

    # Get the CSRF token from cookies
    cookies = csrf_response.cookies
    csrf_token = cookies.get("csrftoken")

    if not csrf_token:
        print("CSRF token not found in cookies")
        return False

    print(f"CSRF token obtained: {csrf_token}")

    # Step 2: Login with the token
    print(f"Attempting login with username: {username}, password: {password}")

    # Prepare headers with CSRF token
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Prepare form data - must be in the format expected by OAuth2PasswordRequestForm
    # Use x-www-form-urlencoded format
    data = f"username={username}&password={password}"

    # Make login request with debug info
    print(f"Request URL: {login_url}")
    print(f"Headers: {headers}")
    print(f"Cookies: {dict(cookies)}")
    print(f"Data: {data}")

    login_response = requests.post(
        login_url, 
        data=data, 
        headers=headers, 
        cookies=cookies
    )

    # Check login result
    if login_response.status_code == 200:
        print("Login successful!")
        print(f"Response: {json.dumps(login_response.json(), indent=2)}")
        return True
    else:
        print(f"Login failed. Status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False

if __name__ == "__main__":
    print("Testing login functionality...")
    result = test_login()

    if result:
        print("\nLogin test passed. You can login with any username and password 'password'")
    else:
        print("\nLogin test failed. Please check the error messages above.")
