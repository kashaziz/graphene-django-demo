# Graphene-Django demo

### Objective:

To create a Django application using graphene-django, connected with MySQL database. The application will act as a scheduling system that allows the authenticated users to create reservable appointment slots that others can view and book.

### Entities:

- User

- Slot

- Appointment



### Workflow:

- Users can create a schedule of available dates and times and select their desired meeting intervals : (15 min / 30 min / 45 min) 

- Users can performe CRUD operations ( create / read / update / delete ) on slots

- Non-users can view all available slots for a specific user

- Non-users can reserve a specific time by providing their full name and email for the meeting



### Validations:

- User can not create duplicate slots. This means that two slots with same start time and slot interval can not exist.

- Reserved slots can not be edited.

- Expired slots (start time older than current time) can not be edited.

- User can edit or delete  own slot.

- Non-user can’t reserve a time that has  already been reserved 

## Setup

- Create and activate virtual environment `python -m venv venv-demo`

- Clone repo

- Install packages from requirements.txt `pip install - requirements.txt

- In settings.py, update database name, user Id and password

- Run migrations: `python manage.py migrate`

- Create superuser: `python manage.py createsuperuser`

- Run django server: `python manage.py runserver 8010

- For API evaluation purposes, Import JSON collection into Postman .

 

### API Flow:

- Create User

- Get Token (Login)

- Create Slot

- Update Slot

- Delete Slot

- Get a user with available slots

- Create Appointment





**Note:**

- For authenticated calls, token is passed in header in the foramt:
`Authorization JWT token-string`

  
   



  