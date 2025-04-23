from .db import execute_query

column_mapping = {
    'title': 'TITLE',
    'author': 'AUTHOR',
    'subject_area': 'SUBJECT AREA',
    'edition': 'EDITION',
    'language': 'LANGUAGE',
    'binding_type': 'BINDING TYPE',
    'number_of_copies': 'NUMBER OF COPIES',
    'isbn': 'ISBN',
    'lending_status': 'LENDING STATUS',
    'availability_status': 'AVAILABILITY STATUS',
    'transaction_id': 'TRANSACTION ID',
    'transaction_type': 'TRANSACTION TYPE',
    'copy_id': 'COPY ID',
    'borrow_date': 'BORROW DATE',
    'return_date': 'RETURN DATE',
    'member_id': 'MEMBER ID',
    'employee_id': 'EMPLOYEE ID',
    'role': 'ROLE',
    'date_card_issued': 'DATE CARD ISSUED',
    'expiry_date': 'EXPIRY DATE',
    'status': 'STATUS',
    'max_books_allowed': 'MAX BOOKS ALLOWED',
    'borrow_period': 'BORROW PERIOD',
    'grace_period': 'GRACE PERIOD',
    'ssn': 'SSN',
    'address': 'ADDRESS',
    'phone_number': 'PHONE NUMBER',
    'applicant': 'Applicant',
    'book': 'Book',
    'book_copy': 'Book copy',
    'borrowing_activity': 'Borrowing activity',
    'librarian': 'Librarian',
    'member': 'Member',
    'person': 'Person',
    'professor': 'Professor'
}

def get_all_categories():
    query = "SHOW TABLES"
    result = execute_query(query)

    return [row[0] for row in result if row[0] != 'users']

def get_category_data(category):
    # Fetch columns for the selected category
    columns_query = f"SHOW COLUMNS FROM {category}"
    columns_result = execute_query(columns_query)
    columns = [row[0] for row in columns_result]

    # Fetch data for the selected category
    data_query = f"SELECT * FROM {category}"
    devices = execute_query(data_query)

    return columns, devices
