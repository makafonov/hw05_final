# hw05_final

Социальная сеть для публикации личных дневников с группами, подпиской на авторов, лентой избранных авторов. 

## Running this project
This project requires Python version 3.8.

Install the project dependencies with
```
pip install -r requirements.txt
```

Synchronize the database state with the current set of models and migrations. 
```
python manage.py migrate
```

Now you can run the project with this command
```
python manage.py runserver
```
