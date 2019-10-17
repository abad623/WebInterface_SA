# Project Title

CHD Mintoring User Interface

## Description

The code beling ot Flask user interface for CHD monitoring system

## Getting Started

### Dependencies

* You need to install Flask, gunicorn in viertual environment. The installed python is 3.6

### Executing program
You need to access to to EC2 instance on AWS. The instance name is "chd-sourcing-webapp" . To login to the instance you need access file.

Example :
ssh -i "chd-sourcing-assistant-azad.pem" ubuntu@ec2-54-194-34-133.eu-west-1.compute.amazonaws.com

After login to Ubuntu instance, make sure the virtual enviroment is activated. You can activae the available virtual enviromnet by exexuting :

source venve/bin/activate

The platform is written in Flask. So, you need a webserver to run the services. We used gunicorn server to run the website in the production environment.
You can start the server by running:

 gunicorn -b 0.0.0.0:8080 -w 4 index:app --name chd_web_app

 -b : ip and port of the application
 -w : the 
