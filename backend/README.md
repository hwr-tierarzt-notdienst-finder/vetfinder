# Where to start?

If you are a German speaker or have the time to use translation tools 
then the sequence diagram [`docs/de_sequence_diagram.puml`](../docs/de_sequence_diagram.puml)
provides a good overview the main backend logic and interactions with frontend services.

Another good place to look are the [end-to-end-tests](tests/test_end_to_end.py). 
Trying to understand and break them may provide you with some insights.

Once you have [started a local development server](#environment-setup) you will be able to locally
access the API-Dokumentation at `http://127.0.0.1/docs`. Reading this documentation and
trying to manually send requests may be helpful.

Of course, you can also dive straight into reading the source code. We have tried to order
the following list of modules in order of importance for understanding core functionality.
Working through the list somewhat chronologically me be a good way to start.


# Modules
| name              | description                                                                                                                                                                                                                                                                                                                                                       |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| vet_management    | Groups business logic for creating/overwriting/deleting vet data and marking vet data as valid or invalid (i.e. deciding whether it should be displayed to the app user) and authorizing from-website and content management users access to preform these operations                                                                                             |
| api               | Implements API-endpoints using FastAPI                                                                                                                                                                                                                                                                                                                            |
| models            | Pydantic models. Currently mainly used to represent vet data in a form that is compatible with database documents, API-requests and responses                                                                                                                                                                                                                     |
| config            | Provides access to global configuration. `config.get()` returns a nested configuration singleton. Configuration for various parts of the system can be accessed through attributes, e.g. `config.get().email.smtp_server_username`                                                                                                                                |
| normalization     | Normalization functionality                                                                                                                                                                                                                                                                                                                                       |
| normalization.vet | Normalization functionality for vet models                                                                                                                                                                                                                                                                                                                        |
| email_            | Sends emails using an external SMTP-server. The contents of the emails are defined in json template files -> see `email_/templates`                                                                                                                                                                                                                               |
| availability      | Can ingest `AvailabilityCondition` models and use them to calculated a list of non-overlapping timespans between a lower and upper bound. The techniques used here are very similar to boolean logic                                                                                                                                                              |
| auth              | Base logic for authenticating and authorizing access based on JWTs                                                                                                                                                                                                                                                                                                |
| vet_visibility    | The system groups database collections by independent "visibilities". Currently there are 2 visibilities: `public` and `test`. This module creates the file `backend/vet_visibility_tokens.txt` containing JWTs for each visibility. These tokens are stored as environment variables in the frontend and form-website services and used some requests to the API |
| db                | Provides a data abstraction layer for managing MongoDB documents and collections. Currently only manages vet data. All other data is currently ephemeral -> caches and JWTs                                                                                                                                                                                       |
| paths             | Provides access to globally important filesystem paths                                                                                                                                                                                                                                                                                                            |
| env               | Utilities for determining which environment the backend is running in. Currently `prod`, `dev` or `test`                                                                                                                                                                                                                                                          |
| types_            | Custom global types                                                                                                                                                                                                                                                                                                                                               |
| constants         | Custom global constants                                                                                                                                                                                                                                                                                                                                           |
| utils             | General utilities that are not tied to any system specific implementation details                                                                                                                                                                                                                                                                                 |
| logs              | Utilities for creating loggers and log messages that will be saved in files in `/backend/logs`. Currently heavily underutilized                                                                                                                                                                                                                                   |


# Development

## Environment Setup

Prerequisites:
- You are able to use a bash shell in your development environment

---

1. Install the newest python version as specified by `.python-version-match` and make sure the executable
   `python<major version number>` can be executed by your shell
2. [Install docker](https://docs.docker.com/engine/install/) and make sure it is accessible on your shell
3. Run `./bin/setup-env.sh` in the `backend` directory. This should create and activate a python virtual environment 
   and install the requirements listed in `backend/requirements.txt` and `backend/dev-requirements.txt`
4. Run `./bin/mongo-create-dev-container.sh`. This should create a database container running MongoDB.
   Confirm the container is running with `docker ps`. You should see something similar to
   ```
   CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                           NAMES
   26aa50764160   mongo:4.2.22   "docker-entrypoint.s…"   38 seconds ago   Up 38 seconds   0.0.0.0:27018->27017/tcp, :::27018->27017/tcp   tierarzt_notdienst_mongo_dev
   ```
5. Run `./bin/start-dev.sh`. Now the API should be running at `http://127.0.0.1:8000` (visit `http://127.0.0.1:8000/docs`)

Because of permission problems you many need to remove and recreate the development database container
between runs using `./bin/mongo-remove-dev-container.sh` and `./bin/mongo-create-dev-container.sh`.

## Testing

Run `./bin/test.sh`

## Managing python dependencies

Add/update/remove dependencies that will be used by the production server during runtime in `backend/requirements.in`
and add/update/remove dependencies that are only used during development or testing in `backend/dev-requirements.in`.

Now running `./bin/requirements-compile.sh` will update the 
`backend/requirements.txt` and `backend/dev-requirements.txt` files with pinned versions of all the
dependencies that you added/updated and pinned versions of their sub-dependencies
(This should keep your environment reproducible and try to 
resolve conflicting sub-dependency version incompatibilities).

Finally, run `./bin/requirements-install.sh` to install the newly updated dependencies in your virtual environment.


# Production

## Server Setup

Prerequisites:
- Credentials for an SMTP-connection to an external email-provider of your choice
- A domain and knowledge of how to set up a reverse proxy (such as [nginx](https://www.digitalocean.com/community/tutorials/how-to-configure-nginx-as-a-reverse-proxy-on-ubuntu-22-04))

---

1. Ask the old repository maintainers for permissions or fork the repo
2. Choose a linux system of your choice (cloud, self-hosted, etc.) to run the server on
3. [Install docker](https://docs.docker.com/engine/install/)
4. Set up a [self-hosted github runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)
   named `prod-server` and make sure the user running the runner script has access to the docker service
5. Delete the old `prod-server` runner in the repository and replace it with your new one
6. Fully rerun the latest `deploy-backend` github workflow. This will fail, that's expected don't panic!
7. On the production server, change directory to `repo/vetfinder/backend` from where the github runner script
   was started. Copy `.env.secret.template` to `.env.secret` values for the environment variables in the dotenv file
8. Retry running the deployment workflow. If everything goes well, it should succeed 
   - The output of `docker ps` should be similar to
     ```
     CONTAINER ID   IMAGE                             COMMAND                  CREATED        STATUS        PORTS                                           NAMES
     13519f7aeceb   tierarzt_notdienst_app_prod       "/bin/sh -c 'ENV=pro…"   4 days ago     Up 4 days                                                     tierarzt_notdienst_app_prod
     adb475f9deb1   mongo:4.2.22                      "docker-entrypoint.s…"   4 days ago     Up 4 days     0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   tierarzt_notdienst_mongo_prod
     ```
9. The API should be accessible over port 80 (try `http://<Server IP>/docs` or `http://<Server IP>:80/docs` if you have configured a different default HTTP-Port). 
   Use a reverse proxy of your choice to set expose the API from your domain and set up HTTPs (e.g. using [certbot](https://certbot.eff.org/))
10. Change the `PROD_DOMAIN` in `.env` and in also change the domain in the frontend services
11. Time for a drink, integration hell is over 🥳🍻

## Accessing Visibility Tokens

A visibility Token is used by the frontend flutter app for requesting vet information
and by the form-website for requesting the initial registration email to be sent a veterinarian. 

Run the following command on the production server to obtain these tokens:
`docker exec -t tierarzt_notdienst_app_prod cat ./vet_visibility_tokens.txt`

You should find tokens for the `test` and `public` visibilities. `public` should be used for 
by customer-facing builds of the flutter-app and form-website. `test` should only be used by developers.