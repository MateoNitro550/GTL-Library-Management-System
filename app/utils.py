from .db import execute_query

column_mapping = {
    'book': 'Book',
    'book_loan': 'Book Loan',
    'library_member': 'Library Member',
    'person': 'Person',
    'subject_area': 'Subject Area',
    'volume': 'Volume',

    # Columns from 'person'
    'ssn': 'SSN',
    'first_name': 'FIRST NAME',
    'last_name': 'LAST NAME',
    'phone_number': 'PHONE NUMBER',
    'mailing_address': 'MAILING ADDRESS',

    # Columns from 'library_member'
    'member_id': 'MEMBER ID',
    'membership_expires_date': 'MEMBERSHIP EXPIRES DATE',
    'current_books_checked_out': 'CURRENT BOOKS CHECKED OUT',

    # Columns from 'subject_area'
    'subject_name': 'SUBJECT NAME',
    'subject_description': 'SUBJECT DESCRIPTION',

    # Columns from 'book'
    'isbn': 'ISBN',
    'title': 'TITLE',
    'edition': 'EDITION',
    'description': 'DESCRIPTION',

    # Columns from 'volume'
    'barcode_number': 'BARCODE NUMBER',

    # Columns from 'book_loan'
    'loan_id': 'LOAN ID',
    'date_borrowed': 'DATE BORROWED',
    'due_date': 'DUE DATE',
    'date_returned': 'DATE RETURNED'
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
