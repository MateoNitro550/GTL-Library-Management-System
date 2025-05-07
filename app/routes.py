from flask import Blueprint, session, redirect, url_for, render_template, jsonify, request, Response
from .utils import get_all_categories, column_mapping, get_category_data
from .db import execute_query

main_routes = Blueprint('main', __name__)

@main_routes.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    categories = get_all_categories()

    total_count_query = "SELECT SUM(cnt) FROM ("
    for category in categories:
        total_count_query += f"SELECT COUNT(*) as cnt FROM {category} UNION ALL "
    total_count_query = total_count_query[:-10] + ") as total"
    total_count_result = execute_query(total_count_query)
    total_count = total_count_result[0][0] if total_count_result else 0

    if session['role'] == 'admin':
        return render_template('dashboard.html', categories=categories, column_mapping=column_mapping, total_count=total_count, is_admin=True)
    else:
        return render_template('dashboard.html', categories=categories, column_mapping=column_mapping, total_count=total_count, is_admin=False)


@main_routes.route('/get_columns/<category>')
def get_columns_endpoint(category):
    columns, _ = get_category_data(category)
    return jsonify({'columns': columns})
    return columns, devices


@main_routes.route('/get_total_count_data')
def get_total_count_data():
    tables_query = "SHOW TABLES"
    tables_result = execute_query(tables_query)
    tables = [table[0] for table in tables_result if table[0] != 'users']

    table_counts = []

    for table in tables:
        count_query = f"SELECT COUNT(*) FROM {table}"
        count_result = execute_query(count_query)
        count = count_result[0][0]
        table_counts.append((column_mapping.get(table, table), table, count))

    labels_mapped, labels_original, counts = zip(*table_counts)

    return jsonify({'labels_mapped': labels_mapped, 'labels_original': labels_original, 'values': counts})


@main_routes.route('/segmentation/<category>')
def segmentation(category):
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    columns, devices = get_category_data(category)

    if session['role'] == 'admin':
        return render_template('segmentation.html', category=category, column_mapping=column_mapping, columns=columns,
                               devices=devices, is_admin=True, table_name=column_mapping.get(category, category))
    else:
        return render_template('segmentation.html', category=category, column_mapping=column_mapping, columns=columns,
                               devices=devices, is_admin=False, table_name=column_mapping.get(category, category))


@main_routes.route('/add_device', methods=['POST'])
def add_device():
    if not session.get('logged_in') or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        currentCategory = request.form.get('category')

        columns, _ = get_category_data(currentCategory)

        values = [request.form.get(column) for column in columns]

        insert_query = f"INSERT INTO {currentCategory} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

        insert = execute_query(insert_query, values, operation="insert")

        if insert:
            return redirect(url_for('main.segmentation', category=currentCategory))
        else:
            return "Failed to add the device. Please try again."

    return render_template('segmentation.html')


@main_routes.route('/update_device', methods=['POST'])
def update_device():
    try:
        data = request.get_json()

        category = data.get('category')
        primary_key = data.get('id')

        # Ensure category and identifier are provided
        if not category or not primary_key:
            return jsonify({'success': False, 'error': 'Category and primary key are required'})

        updated_data = {key: data.get(key) for key in data.keys() if key not in {'id', 'category'}}

        if not updated_data:
            return jsonify({'success': False, 'error': 'No fields to update'})

        if category == 'person':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE person SET {set_clause} WHERE ssn = %s"
            update_data = list(updated_data.values()) + [primary_key]

        elif category == 'library_member':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE library_member SET {set_clause} WHERE member_id = %s"
            update_data = list(updated_data.values()) + [primary_key]

        elif category == 'subject_area':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE subject_area SET {set_clause} WHERE subject_name = %s"
            update_data = list(updated_data.values()) + [primary_key]

        elif category == 'book':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE book SET {set_clause} WHERE isbn = %s"
            update_data = list(updated_data.values()) + [primary_key]

        elif category == 'volume':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE volume SET {set_clause} WHERE barcode_number = %s"
            update_data = list(updated_data.values()) + [primary_key]

        elif category == 'book_loan':
            set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
            update_query = f"UPDATE book_loan SET {set_clause} WHERE loan_id = %s"
            update_data = list(updated_data.values()) + [primary_key]

        else:
            return jsonify({'success': False, 'error': 'Invalid category provided'})

        update = execute_query(update_query, update_data, "update")

        if update:
            return jsonify({'success': True, 'message': f'{category.capitalize()} updated successfully'})
        else:
            return jsonify({'success': False, 'error': f'Failed to update {category}'})

    except Exception as e:
        print('Exception:', str(e))
        return jsonify({'success': False, 'error': 'Invalid data format'})


@main_routes.route('/delete_device', methods=['POST'])
def delete_device():
    try:
        data = request.get_json()

        category = data.get('category')
        primary_key = data.get('id')

        if not category or not primary_key:
            return jsonify({'success': False, 'error': 'Category and primary key are required'})

        if category == 'person':
            delete_query = f"DELETE FROM person WHERE ssn = %s"
            delete_data = (primary_key,)

        elif category == 'library_member':
            delete_query = f"DELETE FROM library_member WHERE member_id = %s"
            delete_data = (primary_key,)

        elif category == 'subject_area':
            delete_query = f"DELETE FROM subject_area WHERE subject_name = %s"
            delete_data = (primary_key,)

        elif category == 'book':
            delete_query = f"DELETE FROM book WHERE isbn = %s"
            delete_data = (primary_key,)

        elif category == 'volume':
            delete_query = f"DELETE FROM volume WHERE barcode_number = %s"
            delete_data = (primary_key,)

        elif category == 'book_loan':
            delete_query = f"DELETE FROM book_loan WHERE loan_id = %s"
            delete_data = (primary_key,)

        else:
            return jsonify({'success': False, 'error': 'Invalid category provided'})

        delete = execute_query(delete_query, delete_data, "delete")

        if delete:
            return jsonify({'success': True, 'message': f'{category.capitalize()} deleted successfully'})
        else:
            return jsonify({'success': False, 'error': f'Failed to delete {category}'})

    except Exception as e:
        print('Exception:', str(e))
        return jsonify({'success': False, 'error': 'Invalid data format'})


@main_routes.route('/report/<category>')
def download_csv(category):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    columns, devices = get_category_data(category)

    csv_data = ','.join([column_mapping.get(column, column) for column in columns[1:]]) + '\n'
    csv_data += '\n'.join([','.join(map(str, device[1:])) for device in devices])

    response = Response(csv_data, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={category}_report.csv'

    return response
