# FastAPI Skeleton with Google Auth and DynamoDB

A minimal FastAPI skeleton application with Google OAuth authentication and DynamoDB integration for user management.

## Features

- Google OAuth authentication
- DynamoDB for user storage
- JWT token-based session management
- Responsive UI with simple dashboard
- Ready-to-use project structure

## Project Structure

```
skel/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── utils.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── dynamodb.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   └── templates/
│       ├── login.html
│       └── dashboard.html
├── static/
│   └── css/
│       └── styles.css
├── config.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set up Google OAuth

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Set up the OAuth consent screen if prompted
6. Select "Web application" as the application type
7. Add "http://localhost:8000/auth/callback/google" as an authorized redirect URI
8. Note your Client ID and Client Secret

### 4. Set up DynamoDB

#### Option 1: Use AWS DynamoDB

1. Create an AWS account if you don't have one
2. Create a DynamoDB table named "users" with primary key "id" (string)
3. Create a global secondary index named "email-index" with partition key "email"
4. Create an IAM user with DynamoDB access and note the access key and secret

#### Option 2: Use Local DynamoDB for Development

1. Install [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
2. Run DynamoDB locally: 
   ```powershell
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   ```
3. Set `DYNAMODB_ENDPOINT_URL` to "http://localhost:8000" in your .env file

### 5. Create a .env file

Create a `.env` file in the root directory with the following variables:

```
DEBUG=True
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/google
SECRET_KEY=your_secret_key_change_in_production
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
DYNAMODB_TABLE_USERS=users
# For local DynamoDB development:
# DYNAMODB_ENDPOINT_URL=http://localhost:8000
```

## Running the Application

Start the FastAPI server:

```powershell
cd skel
uvicorn app.main:app --reload
```

Visit http://localhost:8000 in your browser to see the login page.

## Using as a Template for New Projects

To use this skeleton as a template for a new project:

1. Copy the entire `skel` directory to your new project location
2. Update the project name, configuration, and dependencies as needed
3. Add your specific application logic to the existing structure

## API Documentation

FastAPI automatically generates API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
