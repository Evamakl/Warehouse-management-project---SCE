Warehouse management project - SCE

Students:
  Gilad Abitbul - 315402719
  Eva Maria Klassen - 323415042
  Ester Moiseyev - 318692464
  Yarden Dali - 207220013


Installation guide:
  - Download the files and extract from ZIP into desired directory.
  - Install all the necessary libraries by using: pip install -r requirements.txt
  - Run main.py file, this will build the app and restart the database.
  - The url for the website will be printed in the terminal.
  - development_functions.py file store the base admin, teacher and student accounts. If necessary, add users as you wish, all other classes can be added through the website.
  - Each time running the main.py file the database will be resetted, make sure to set the "database_start_over()" function inside a comment (''' X ''') or delete it to avoide losing data.


Testing commands:
To run the tests file and get report run these commands:
  - radon cc .
  - coverage run -m unittest app_test.py                  /* Integration tests */
  - coverage run -m pytest tests\unit_test.py             /* unittests */
  - coverage run -m pytest tests\unit_test2.py            /* unittests */
  - coverage report
  - pylint website


If one of these commands doesn't work, try pip install:
  - for radon: pip install radon
  - for coverage: pip install coverage
  - for unittests: pip install unittest
  - for pylint: pip install pylint
> > these libraries should be included in requirements.txt file


Server system requirements:
  - Python version 3.7.0 or newer.
  - PC with Standard CPU (notice that better components result in better performance).
  - PC runnig any type of web browser.


Users system requirements:
  - PC or mobile running any type of browser.
