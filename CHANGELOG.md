# CHANGELOG

## v0.15.0 - 21.11.2020

### Added

* Docker compose file for production

## v0.14.0 - 21.11.2020

### Added

 * Nginx config for project

## v0.13.0 - 21.11.2020

### Added

* Connection between statistics service and main app
* New endpoints to send data to statistics service

## v0.12.2. - 17.11.2020

### Added

* Default version for postgres in docker compose file

## v0.12.1 - 17.11.2020

### Added

* Credentials for aws manually for client in boto3

## v0.12.0 - 16.11.2020

### Added

* S3 to project
* Utils for resize and upload files

## v0.11.0 - 08.11.2020

### Added

* Elasticsearch to project
* Mixin for adding and deleting indexes
* Search route for polls

## v0.10.1 - 04.11.2020

### Added

* Template for password forget email

## v0.10.0 - 04.11.2020

### Added

* Celery and celery beat services to docker-compose

## v0.9.0 - 04.11.2020

### Added

* Forget and reset password logic

## v0.8.0 - 02.11.2020

### Added

* Places number query param for options

## v0.7.1 - 01.11.2020

### Added

* Cascade delete option
* Ordering for options

## v0.7.0 - 31.10.2020

### Added

* User poll models
* Logic for create user poll

## v0.6.0 - 26.10.2020

### Added

* Option model
* CRUD for options

## v0.5.0 - 23.10.2020

### Added

* Cors origins variable to settings
* Current user profile endpoint
* My polls endpoint

## v0.4.0 - 22.10.2020

### Changed

* Logic for clear database after each test, not it uses transaction rollback

## v0.3.0 - 22.10.2020

### Added

* Polls models, schemas
* Polls CRUD functionality

### Changed

* Orm and migrations to `sqlalchemy` and `alembic`

## v0.2.0 - 06.10.2020

### Changed

* Package manager to `poetry`

## v0.1.0 - 04.10.2020

### Added

* Authorization and authentication process