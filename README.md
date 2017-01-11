# aasaan
Aasaan is a back office management application intended to centralize maintenance of contacts, program schedules and integrated communication.

This was written with an NGO setup in mind, tracking volunteer information and sending them communications from one place.

Setting this up is straightforward.

Install postgres. Clone the repo. Add a config.py under settings (same place where base.py is located). This is intended for confidential settings like your django secret key, postgres password and anything else you want to put in here.

Optionally create a virtual environment. 

pip install -r requirements.txt
python manage.py migrate
and finally
python manage.py runserver

If you want to run this on docker, see deploy folder - rebuild_aasaan.sh
