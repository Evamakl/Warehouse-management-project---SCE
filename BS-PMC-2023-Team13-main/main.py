"""
Main module for running the application.
"""
from website import app
from development_functions import database_start_over

if __name__ == '__main__':
    if input("Start over database? [Y/N]") in ['Y', 'y']:
        database_start_over()
    app.run(debug=True)
