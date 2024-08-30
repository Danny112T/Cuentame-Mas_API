
# Cuentame Más API

This repository contains the code for an API of a IA chat bot made with FastAPI and Strawberry GraphQL as the terminal project of the Computer systems engineering. 

## Requirements
- Python >=3.10
- [Astral UV](https://docs.astral.sh/uv) >=0.3.3

## Installation

To run the project in your local environment::

  1. Clone the repository::
```bash
 git clone https://github.com/Danny112T/Cuentame-Mas_API.git
 cd Cuentame-Mas_API
```
  2. Create and activate a virtual environment::
```bash
 uv venv
 source env/bin/activate
```
  3. Install requirements::
```bash
  uv sync
  uv lock
```
  4. Create a .env file in root and fill it with .env.example
  5. Run the application:
  
```bash
  uv run fastapi dev app/main.py # for development
  uv run fastapi start app/main.py # for production
```


## Usage Examples

Launch the fast api server at specified port default 8000 (open the UI at http://localhost:8000/graphql):


## Authors

- [@Danny112T](https://www.github.com/Danny112T)
- [@minheenista](https://github.com/minheenista)
- [@Mrquez](https://github.com/Mrquez)