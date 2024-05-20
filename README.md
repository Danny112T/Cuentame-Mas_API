
# Cuentame Más API

This repository contains the code for an API of a IA chat bot made with FastAPI and Strawberry GraphQL as the terminal project of the Computer systems engineering. 


## Installation

To run the project in your local environment::

  1. Clone the repository::
```
  $ git clone https://github.com/Danny112T/Cuentame-Mas_API.git
  $ cd Cuentame-Mas_API
```
  2. Create and activate a virtual environment::
```
  $ virtualenv env -p python3
  $ source env/bin/activate
```
  3. Install requirements::
```
  $ pip install -r requirements.txt
```
  4. Create a .env file in root and fill it with .env.example
  5. Run the application::
```
  $ uvicorn  main:app --reload
```


## Usage Examples

Launch the fast api server at specified port default 8000 (open the UI at http://localhost:8000/graphql):

```
    $ uvicorn main:app --reload
```


## Authors

- [@Danny112T](https://www.github.com/Danny112T)
- [@minheenista](https://github.com/minheenista)
- [@Mrquez](https://github.com/Mrquez)