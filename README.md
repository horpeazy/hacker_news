# Hacker News

# Introduction
Hackerr News is a web application that makes it easier to navigate the news from the [Hacker New API](https://hackernews.api-docs.io). The applications serves web pages using the Flask Frmework and also exposes an API that allows users to consume it's resources.
It synchronizes the database with the published news on the Hacker News API every few minutes to make sure users are up to date with the latest news. There are several categories of news and the user can filter them both on the frontend and when making API calls to to the database.

You should feel free to expand on the project in any way you can.

All backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/).

## Getting Started

### Pre-requisites and Local Development 
Developers using this project should already have Python3 and pip installed on their local machines.

#### Running project locally
From the project directory run `pip install requirements.txt`. All required packages are included in the requirements file. 
The project folder contains a .env file where environment variables are be stored. The environment variables are used to store database information, optionally the FLASK_APP and FLASK_ENV variables can be stored there also.

To run the application run the following commands if FLASK_APP and FLASK_ENV are not set in the .env file:
 
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```
else, you should run the command:
```
flask run
```

These commands put the application in development and directs our application to use the `app.py` file in our project directory. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the [Flask documentation](http://flask.pocoo.org/docs/1.0/tutorial/factory/).

The application is run on `http://127.0.0.1:5000/` by default.

#### Database Setup
The application will automatically fetch the latest hundred news on the initial start up and then synchronize the database afterwards

#### Tests
In order to run tests navigate to the project directory and run the following command: 
set DEBUG = True do avoid errors while running test

```
python test_app.py
```

All tests are kept in that file and should be maintained as updates are made to app functionality. 

## API Reference

### Getting Started
- Base URL: At present this api can only be run locally and is not hosted as a base URL. The api can be accessed at the default, `http://127.0.0.1:5000/api/v1`.

### Base Model

```
    id: int - id of the news items (required)
    hacker_news_id: int - id of the news item in the HN database (optional)
    type: string - type of news item (required)
    time_posted: datetiem - to the news as posted (optional)
    author: string - author of news item (optional)
    deleted: boolean - to indicate if item has been deleted (optional)
    dead: boolean - to indicate if item is dead(optional)
    text: string - text content (optional)
    url: string - url to the news (optional)
    title: string - title of the news item (optional)
    parent: int - parent of the news items(e.g comment or post) (optional)
    parts: list - parts of the news item(for polls)  (optional)
    descedants: descedants of item(e.g comments of comment)(optional)
    score: int - score rating (optional)
    kids: list - children of a news item (e.g comment on story) (optional)
```

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 
- 405: Method Not Allowed
- 500: Internal Server Error

### Endpoints 

#### GET '/api/v1/items?page=${integer}'
- Fetches a list of news items and returns a dictionary with a key items and value corresponding to the list of the new items. The result is paginated by 100
and there's an optibnal page parameter to get by page
- Request Arguments: page - integer
- Returns: An object with a single key, items that points to the list of items. 
```
{"items": [
                { 
                    "by":"mtsr",
                    "id":2,"parent":32948443,
                    "text":"Modern engines also do a lot of streaming data to VRAM",
                    "time":"Fri, 23 Sep 2022 08:41:43 GMT",
                    "type":"comment"
                },
                {
                    "by":"rootsudo",
                    "id":3,"parent":32946371,
                    "text":"I was thinking what was the gold",
                    "time":"Fri, 23 Sep 2022 08:42:20 GMT",
                    "type":"comment"
                }, .....
            ]
}
```

#### GET '/api/v1/item/${item_id}'
- Fetches a news item with the specified id (e.g comment, story )
- Request Arguments: item_id - integer
- Returns: An object representation of the resource
```
{
    "by":"s5300",
    "id":1,"kids":[32948997,32948783,32948830],
    "parent":32948754
    text":"What do you think will happen to the bulk of the population in this time?",
    "time":"Fri, 23 Sep 2022 08:41:11 GMT",
    "type":"comment"
}
```

#### PATCH '/api/v1/item/${item_id}'
- Updates a resource using the id of the resource 
- Request Arguments: item_id - integer
- Returns: An object with the resource id
```
{
    'success: True,
    'id': 20
}
```

#### DELETE '/api/v1/item/${item_id}'
- Deletes a resource using the id of the resource
- Request Arguments: item_id - integer
- Returns: the id of the object deleted
```
{
    'success: True,
    'id': 20
}
```


#### POST '/api/v1/item'
- Sends a post request in order to create a news not present in the hacker news database
- Request Body: The fields of the news (see base model)
- Returns: the id of the object created 
```
{
    'success': True,
    'id': 34
}
```

## Author
[Iyamu Hope Nosa](https://linkedin.com/in/iyamuhope)
