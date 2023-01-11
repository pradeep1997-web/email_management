# Gmail Utility

## Step 1
Create credentials from google developer console and oauth concent via application dashboard

## Step 2
Clone this repository, create virtual enviroment , migrate the project and then create superuser

## Step 3
Modify dependency
Update pyparsing init file line 130 and remove trailing version
## Step 3
Download the credentials.json file from application dashboard and include it in users app folder

## Step 4
SignUp via url path /auth/register and then login via /auth/login for authentication token

## Step 5
Sync mail box via /mail/sync/ endpoint by POST method

## Step 6
For sending mail reply use /mail/send_mail/ endpoint with the {"from":"**reciepient mail address**"}
