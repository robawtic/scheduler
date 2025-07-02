# Manual Testing Guide for User Registration and Authentication

This guide provides step-by-step instructions for manually testing the user registration and authentication functionality in the Scheduler application.

## Prerequisites

1. The Scheduler backend server is running on `http://localhost:8080`
2. The Scheduler frontend is running on `http://localhost:5176`
3. You have access to a web browser with developer tools (Chrome, Firefox, etc.)

## 1. User Registration Flow

### 1.1 Valid Registration

1. Open your browser and navigate to `http://localhost:5176/register`
2. Fill in the registration form with valid data:
   - Username: `testuser` (at least 3 alphanumeric characters)
   - Email: `test@example.com` (valid email format)
   - Password: `password123` (at least 8 characters)
   - Confirm Password: `password123` (must match password)
3. Click the "Register" button
4. Expected result:
   - You should see a success message: "Registration successful! Please check your email to verify your account."
   - After a few seconds, you should be redirected to the login page

### 1.2 Invalid Registration - Duplicate Username

1. Navigate to `http://localhost:5176/register`
2. Fill in the registration form with the same username as before:
   - Username: `testuser` (already registered)
   - Email: `another@example.com` (different email)
   - Password: `password123`
   - Confirm Password: `password123`
3. Click the "Register" button
4. Expected result:
   - You should see an error message: "Username already registered" or "Username is already taken"

### 1.3 Invalid Registration - Duplicate Email

1. Navigate to `http://localhost:5176/register`
2. Fill in the registration form with the same email as before:
   - Username: `anotheruser` (different username)
   - Email: `test@example.com` (already registered)
   - Password: `password123`
   - Confirm Password: `password123`
3. Click the "Register" button
4. Expected result:
   - You should see an error message: "Email already registered" or "Email is already taken"

### 1.4 Invalid Registration - Validation Errors

1. Navigate to `http://localhost:5176/register`
2. Test each of the following validation scenarios:

   a. Short Username:
   - Username: `ab` (less than 3 characters)
   - Email: `valid@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
   - Expected error: "Username must be at least 3 characters"

   b. Invalid Email:
   - Username: `validuser`
   - Email: `invalid-email` (not a valid email format)
   - Password: `password123`
   - Confirm Password: `password123`
   - Expected error: "Email is invalid"

   c. Short Password:
   - Username: `validuser`
   - Email: `valid@example.com`
   - Password: `short` (less than 8 characters)
   - Confirm Password: `short`
   - Expected error: "Password must be at least 8 characters"

   d. Mismatched Passwords:
   - Username: `validuser`
   - Email: `valid@example.com`
   - Password: `password123`
   - Confirm Password: `different123`
   - Expected error: "Passwords do not match"

   e. Non-Alphanumeric Username:
   - Username: `user@name` (contains special characters)
   - Email: `valid@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
   - Expected error: "Username must be alphanumeric"

## 2. Login Flow

### 2.1 Valid Login

1. Navigate to `http://localhost:5176/login`
2. Enter the credentials for the user you registered in step 1.1:
   - Username: `testuser`
   - Password: `password123`
3. Click the "Sign In" button
4. Expected result:
   - You should be redirected to the main application page (e.g., `/schedules`)
   - The application should display content that requires authentication

### 2.2 Invalid Login - Wrong Password

1. Navigate to `http://localhost:5176/login`
2. Enter:
   - Username: `testuser`
   - Password: `wrongpassword`
3. Click the "Sign In" button
4. Expected result:
   - You should see an error message: "Invalid username or password"
   - You should remain on the login page

### 2.3 Invalid Login - Non-existent User

1. Navigate to `http://localhost:5176/login`
2. Enter:
   - Username: `nonexistentuser`
   - Password: `password123`
3. Click the "Sign In" button
4. Expected result:
   - You should see an error message: "Invalid username or password"
   - You should remain on the login page

## 3. Token Refresh

To test token refresh, you'll need to use the browser's developer tools:

1. Login successfully as described in step 2.1
2. Open the browser's developer tools (F12 or right-click and select "Inspect")
3. Go to the "Application" tab (Chrome) or "Storage" tab (Firefox)
4. Look for "Local Storage" and find the items for your application
5. Note the value of the `access_token` item
6. Wait for the token to expire (default is 30 minutes, but you can modify the code to use a shorter expiration for testing)
7. Perform an action in the application that requires authentication
8. Expected result:
   - The application should automatically refresh the token
   - Check the Local Storage again - the `access_token` value should have changed
   - The application should continue to function without requiring you to log in again

## 4. CORS Testing

### 4.1 Testing from Allowed Origin

1. Ensure the frontend is running on an allowed origin (e.g., `http://localhost:5176`)
2. Follow the steps for registration and login as described above
3. Expected result:
   - All requests should work correctly without CORS errors

### 4.2 Testing from Disallowed Origin

This test requires modifying the frontend to run on a different port:

1. Modify the frontend development server to run on a port that is not in the allowed origins list (e.g., `http://localhost:5177`)
2. Try to access the application and perform registration or login
3. Expected result:
   - You should see CORS errors in the browser's developer console
   - The requests should be blocked by the browser's same-origin policy

## 5. CSRF Protection

### 5.1 Testing CSRF Protection

1. Login successfully as described in step 2.1
2. Open the browser's developer tools
3. Go to the "Network" tab
4. Perform an action that requires CSRF protection (e.g., creating a new schedule)
5. Find the request in the Network tab and examine its headers
6. Expected result:
   - The request should include an `X-CSRF-Token` header
   - The request should be processed successfully

### 5.2 Testing Without CSRF Token

This test requires using a tool like Postman or writing a custom script:

1. Login successfully and get a valid authentication token
2. Use Postman or a similar tool to send a POST request to a protected endpoint (e.g., `/api/v1/schedules`)
3. Include the authentication token but do not include the CSRF token
4. Expected result:
   - The request should be rejected with a 403 Forbidden error
   - The response should indicate that a CSRF token is required

## 6. Reporting Issues

If you encounter any issues during manual testing, please document them with the following information:

1. Test case name and number
2. Steps to reproduce
3. Expected result
4. Actual result
5. Screenshots (if applicable)
6. Browser and version
7. Any error messages from the browser console

Submit this information to the development team for investigation.