# 📚 Courses.io

### A university course registration system
---


##   🔩 Tech Stack

* Django
* Tailwind CSS
* Cleopatra Dashboard

## 👩🏻‍🏫 Jargon Table 

| JARGON                   |                                                  DESCRIPTION |
| ------------------------ | -----------------------------------------------------------: |
| Department               | University Majors e.g Computer Science, Software Engineering e.tc. |
| Course                   |            Courses to be offered e.g CSC 1101, MTH 1101 et.c |
| Adviser                  | A pseudo-admin user responsible for operations in a department |
| Lecturer                 |          User responsible for accepting course registrations |
| Student                  |             User who typically requests course registrations |
| Admin                    |                                         System Administrator |
| Level                    | A student's year in the university e.g 100 Level, 200 Level, etc. |
| Student Class            | A unique combination of Level and Department e.g Computer Science 200 Level |
| Prerequisite(s)          | A course's prerequisites are courses a students must have a grade of least an 'E' in previous Acadmemic Timelines in order to be able to register the said course |
| Carryover                |               A course in which a student has a grade of 'F' |
| Course Registration      | A record of a student's desire to offer a course in a particular Academic Timeline and the approval of the Management(Lecturer or Adviser) |
| Academic Timeline        | Unique Combination of Academic Session and Semester e.g '2020/2021 First Semester' Timeline |
| Course Registration Form | A collection of a student's course registrations for an academic timeline |
| Units                    |                                       The weight of a course |
| Max Units                | The maximum units a Student in a Student Class can register in an Academic Timeline |
| Semester Allocation      | Courses a Student Class is to offer in a particular Academic Timeline |
|                          |                                                              |

## 🎢 Features

* Students can request course registration
* Students must pass a course's prerequisite courses before they are allowed to register a course.
* Students cannot register over the max units
* Student must register carryover courses before the semester allocation
* Lecturer can reject or accept course registrations
* Adviser can set the status of Course Registrations without any of the restrictions above
* Adviser can set Semester Allocation
* Adviser can initialize Course Registration
* Adviser can promote Students to the next Student Class
* Adviser can edit Course information
* Admin can close course registration Portal
* Admin can progress the whole system to the next Academic Timeline

## 🎭 Demo

[Courses.io Demo](https://courses-io.herokuapp.com/)

### 🎎 Dummy Data For Demo

**Adivser User**

**username**: adviser

**password**: adviser123

---
**Lecturer User**

**username**: lecturer

**password**: lecturer123

---

**Student User**

**username**: student

**password**: student123

---

**Admin User**

👀

---

## Cloning the repo

Create a virtual environment
```
virtualenv venv
.\venv\scripts\activate
```
Clone
```console

git clone https://github.com/femiayotubosun/courses-io.git
cd courses-io
```
Install requirements
```console
pip install -r requirements.txt
```
Create a .env file in root directory
Add the following and set accordingly

```smalltalk

DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
SECRET_KEY=
MAILJET_API_KEY=
MAILJET_SECRET_KEY=
DEFAULT_MAIL=
EMAIL_BACKEND=anymail.backends.mailjet.EmailBackend

```
The database is configured to work with Postgres, you can of course replace with any database setup you want. Edit DATABASES in settings.py accordingly.

Next, apply migrations
```console
python manage.py migrate
```
Run the server
```console
python manage.py runserver
```







