# Data Engineer - Technical Assesment

## Statatement
An external system / supplier is sending patient data to our platform using the FHIR standard. Our analytics teams find this format difficult to work with when creating dashboards and visualizations. You are required to tranform these FHIR messages into a more workable format preferably in a tabular format. Include any documentation / commentary you deem necessary.

## The Solution
The proposed solution for this project was to use automation with **python** commands mainly.

For this, a cron job was created to allow the manipulation of the data coming from the external system / supplier to be stored in a relational database using PostgreSQL.

To handle transactions with the database safely, **SQLAlchemy** was used as the main library and its ORM to manage SQL queries. Most of the queries in this project take into account the use of inserts or updates in the DB and DDL commands to create tables for example.

Since a patient has an ID, it is easy to determine if some data has changed for a particular patient, so that records can also be updated in the database. The same does not apply to things like names or addresses where the strategy for updating the information needs to be discussed.

For the preparation of this project, it was assumed that the information could potentially change and that the provider would include those changes in the same **json** format. All the json files are processed at once with the execution of the application's main command (**main.py**).

The cron job specifies running the application's main command every minute, but this can be configured based on how often the system sends the FHIR information.

For the development of unit tests, **pytest** was used to be able to manage fixtures in a simple way and at the same time the pytest-coverage tool was used to get an idea of ​​the areas not covered by the unit or integration tests.

Finally, to manage the development environment, **Docker** was used in order to have an application that could be ready to be easily deployed, through a tool that allows CI/CD, which provides greater robustness to the development cycle.

## Development setup
All the setup is handled by Docker and docker-compose file, but if you still want to have a virtual environment installed in your machine for this project, you can follow these steps:

1. Open a terminal window.
2. Change the directory where the app (repo) is located (see **Project Requirements** section bellow if you don't know how to clone the repo).
3. run: `python3 -m install venv .pyenv` to install a virtual environment called **.pyenv**. You can called them as you want but don't forget to check if the name is included in the **.gitignore** file, otherwise you need to include this name on this file.
4. run: `source .pyenv/bin/activate` to activate your virtual environment (you can replace **.pyenv** with the name of the virtual environment you used in the step before).
5. run: `pip install -r requirements/local.txt` to install the necessary dependencies for this project.

### Project Requirements

- To have this repo on your local machine you can use the **git clone** command. Clone this repo on any directory of your machine running the command `git clone git@github.com:cgarcia286/exa-data-eng.git` in your terminal.
- It is recommended to use WSL if you are a **Windows** user. Follow the step described on this link: [How to install Linux on Windows with WSL](https://learn.microsoft.com/en-us/windows/wsl/install) to enable WSL in your local machine. Next, you will need to install Ubuntu or any of your preferred Linux distributions. You can find Ubuntu on the Windows Store.
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) if you are using **Windows or Mac** (Linux user can skip this step because Docker is native to the OS).
- Install a database management tool which accept Postgres connections, i.e. [DBeaver](https://dbeaver.io).
- Copy the environment variables guide to a new file used by the application running `cp .env.example .env`.
- It is recommended to use **make commands** to make easier the interaction with Docker. If you are a **Mac** user and you never before used **make commands**, then is is probable you will need to install the **XCode command line tools**. If that is the case, please follow these steps:

1. Open a terminal window in your Mac.
2. run: `xcode-select --install` to install the XCode CLI tools.
3. run: `xcode-select -p` to configure the access path.

**NOTE:** If you get the correct path (for example, /Library/Developer/CommandLineTools), that means the tools are configured correctly. If not, you can configure them using the following command:

`sudo xcode-select -switch /Library/Developer/CommandLineTools`

Now you should be able to run make commands in your machine. If you still have trouble running your app, the **Makefile** file contains all the **Docker / docker-compose** commands used on this project to run and test this application.

## How to run the app
- Open a terminal window on your PC.
- run: `make build` to build a Docker image for the application.
- run: `make start` to spin up a container and run your application. This will run a cron job in the container and you will be able to check the Database for the results. Also, you will find the log register located in the logs folder.
**NOTE:** Everytime you make a change on your environment variables (**.env** file) or in the docker-compose or Dockerfile, you must need to rebuild your app usin the `make build` command.

### Useful commands

- **`make one-run`**: runs the **main.py** one time only without the cron job and keep alive the container to check the DB results.
- **`make stop`** stops the application and other containers that might be started as a result of other processes..
- **`make shell`** spins up a container and load the shell.


## How to check results in DB

To check the results in the DB, you will need to configure a connection with the Database management tool of your preference.

The parameters for the DB connection are specified in the **.env.example** file, but here we specified the values to configured the connection as well:

- Host: localhost
- Port: 5432
- Database: exa-data
- Username: exa-data
- Password: exa-data

Then after, you have to run **make start** or **make one-run** command to spin up a container and grant access connection to the DB.

**NOTE:** This values are used for local environment only. The values for the production DB connection are provided in the specific .env file for production and never have to be commited. Other solution is to provide this values as part of the workflow variables and stored them in the Github environment variables for example if GitHub is used for deployments.

## How to run tests
For your convenience, there is a command to run the test suite for the application wich already include the project coverage. If you want to run the test suite, use the `make run-tests` commands. If you want to run specific tests, the you can follow this steps:

1. run: `make start-bg` to run a container in the background.
2. run: `make shell` to get access to your container.
3. run the command you want to run your specific tests using **pytest**, i.e. `pytest src/`.

## Next steps aka TODO / pending:

Due to the short time to complete this POC and taking into account that it was a project to evaluate the skills of each candidate for the Data Engineer position, it was not considered to include migrations in this stage. So it is recommended to include alembic in this project to keep track on schemas changes.

After integrate alembic in the project it will be nice to have a way to restore the Database for development environment. So the plan is to create a **Makefile** command to restore the DB to the initial state where is posible.

Other thing that has to be consider is the fact of change the schemas to update models to map FHIR resources properly found at [FHIR Resource Types](https://www.hl7.org/fhir/resourcelist.html).
