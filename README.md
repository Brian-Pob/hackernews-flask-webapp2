# CEN4090L Fall 2022 - Software Engineering Capstone

## Members

Brian Poblete - bap21k

Raviverma Chamarti - rc20d

Quan Pham - qmp20a

Ralitsa Donova - rkd19

Carlos Pantoja-Malaga - crp19b

## Project Notes

For full transparency, this project is also the project for COP4521 Parallel
Programming in Python Fall 2022. This group has received permission from the
professors of both classes to reuse part of this project.

## Setup the Project with Pipenv

0. Clone the GitHub repo. This repo should contain a few files: this README,
Pipfile, Pipfile.lock, and requires.txt. These will be used later on when
setting up the virtual environment.

1. Now install Python 3.10. This should come with pip, python's package
manager.

2. Using pip, install the package pipenv. `pip install --user pipenv`.
We want to use virtual environments for this project. Pipenv  manages the
project's virtual environment as well as the installation
of packages. Follow [this guide](https://docs.python-guide.org/dev/virtualenvs/)
to install Pipenv.

3. After install Pipenv, run `pipenv install`. Pipenv will read the contents of
Pipfile and install the packages listed there. This is the beauty of pipenv
as it allows you to more cleanly manage both your required packages and their
installations in your virtual environment.

4. This should be all that is required for the actual project folder. Other
things like Nginx need to be configured manually.

## Using the Virtual environment

0. After installing Pipenv and using it to install the required python packages
, we can now use the virtual environment it created.

1. Run `pipenv shell` to activate the virtual environment created for this 
project.

2. Your terminal instance should now be running in the venv. This will allow 
you to run your python code with the required python version and packages.

3. In the Pipfile, there should be a scripts section. I have included a few
scripts that we can execute to run the python app using gunicorn.

## Getting Started with Flask 

0. In the #References section below, you will find a link to a Digital Ocean
guide on how to create a basic Flask application with Nginx and Gunicorn. We 
will be following most of this guide.

1. Another useful resource we will be utilizing will be the [Flask Mega-Tutorial
by Miguel Grinberg.](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
He is the author of various Python packages including one
that we are using in this project.

2. We will be basing our project structure on his project structure. Reading
through the tutorial, you will see how he structures his app. He eventually
restructures the app in Chapter 15. So, our app will be based on the structure
after Chapter 15.

## Rereferences

https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04

https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

https://docs.python-guide.org/dev/virtualenvs/

Test