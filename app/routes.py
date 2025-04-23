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


@main_routes.route('/manage-users')
def manageUsers():
    return render_template('manageUsers.html')


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

        valid_columns = columns[1:]

        values = [request.form.get(column) for column in valid_columns]

        insert_query = f"INSERT INTO {currentCategory} ({', '.join(valid_columns)}) VALUES ({', '.join(['%s'] * len(valid_columns))})"

        insert = execute_query(insert_query, values, operation="insert")

        if insert:
            return redirect(url_for('segmentation', category=currentCategory))
        else:
            return "Failed to add the device. Please try again."

    return render_template('segmentation.html')


@main_routes.route('/update_device', methods=['POST'])
def update_device():
    try:
        data = request.get_json()

        device_id = data.get('id')
        category = data.get('category')

        updated_data = {key: data.get(key) for key in data.keys() - {'id', 'category'}}

        set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])

        update_query = f"UPDATE {category} SET {set_clause} WHERE id = %s"

        update_data = list(updated_data.values()) + [device_id]

        update = execute_query(update_query, update_data, "update")

        if update:
            return jsonify({'success': True, 'message': 'Device updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update device'})

    except Exception as e:
        print('Exception:', str(e))
        return jsonify({'success': False, 'error': 'Invalid data format'})


@main_routes.route('/delete_device', methods=['POST'])
def delete_device():
    try:
        data = request.get_json()
        device_id = data.get('id')
        category = data.get('category')

        delete_query = f"DELETE FROM {category} WHERE id = %s"
        delete_data = (device_id,)

        delete = execute_query(delete_query, delete_data, "delete")

        if delete:
            return jsonify({'success': True, 'message': 'Device deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete device'})

    except Exception as e:
        print('Exception:', str(e))
        return jsonify({'success': False, 'error': 'Invalid data format'})


@main_routes.route('/move_to_stock', methods=['POST'])
def move_to_stock():
    try:
        data = request.get_json()

        device_info = data.get('deviceInfo', {})

        snid = device_info.get('SNID')
        model = device_info.get('Model')

        insert_query = "INSERT INTO stock (SNID, MODEL) VALUES (%s, %s)"
        insert_data = (snid, model)

        success = execute_query(insert_query, insert_data, operation="insert")

        if success:
            return jsonify({'success': True, 'message': 'Device moved to stock successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to move device to stock'})

    except Exception as e:
        print('Exception:', str(e))
        return jsonify({'success': False, 'error': 'Failed to move device to stock'})


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
