# WH-Organization: Warehouse Management Project - SCE
Welcome to WH-Organization, a web-based warehouse management system developed as part of my studies at Sami Shamoon College of Engineering, in partnership with Eva-Maria Klassen, Ester Moiseyev, and Yarden Dali, for the Visual Communication Department. This innovative platform aims to enhance communication and logistics by streamlining the management of department equipment for both faculty and students.

## Team Members:
  &middot; Gilad Abitbul<br/>
  &middot; Eva Maria Klassen<br/>
  &middot; Ester Moiseyev<br/>
  &middot; Yarden Dali

## Key Features:
&middot; Efficient Equipment Tracking: WH-Organization allows warehouse managers to monitor inventory levels and oversee equipment loans for various users within the college.

&middot; Simplified Equipment Requests: Faculty and students can easily create, edit, and cancel equipment requests through a user-friendly interface.

&middot; Improved Communication: The system enhances communication between students, faculty, and warehouse managers, addressing issues that arise with existing platforms like Google Forms.

&middot; Real-time Equipment Management: Our solution enables the issuance of tracking numbers (barcodes) for equipment, ensuring better accountability and organization.

## Demo

Check out the demo of the project here: [WH-Organization Demo](https://youtu.be/otuYlS4nnZE)

## Installation guide:
1. Download and Extract: Download the project files and extract them from the ZIP archive into your desired directory.
   
2. Install Dependencies: Navigate to the project directory and install the necessary libraries by running:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Run the Application: Execute the main.py file to build the app and initialize the database:
   ```bash
   python main.py
   ```
   The local host address will be printed in the terminal.
   
4. User Accounts: The development_functions.py file contains base accounts for admin, teachers, and students. You can add users as needed; all other classes can be added through the website interface.
5. Database Reset: Each time you run the main.py file, the database will be reset. To avoid losing data, ensure that the database_start_over() in main.py marked as a comment

## Testing Commands:
To run the test files and generate a report, use the following commands:
  ```bash
  radon cc .
  coverage run -m unittest app_test.py        # Integration tests
  coverage run -m pytest tests/unit_test.py   # Unit tests
  coverage run -m pytest tests/unit_test2.py  # Unit tests
  coverage report
  pylint website
  ```

## Troubleshooting
If any of the commands do not work, ensure you have the required packages installed:
<br/>
&middot; For Radon:
  ```bash
  pip install radon
  ```
&middot; For Coverage:
  ```bash
  pip install coverage
  ```
&middot; For Unit Tests:
  ```bash
  pip install unittest
  ```
&middot; For Pylint:
  ```bash
  pip install pylint
  ```

## Contact
For any questions or inquiries, please contact us at 
abutbulgilad@gmail.com
evaklassen81@gmail.com
estermoiseyev@gmail.com
yarden.dali11@gmail.com
