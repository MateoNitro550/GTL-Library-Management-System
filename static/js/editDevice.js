document.addEventListener('DOMContentLoaded', function () {
  const editDeviceButton = document.getElementById('editDeviceButton');
  const deleteDeviceButton = document.getElementById('deleteDeviceButton');
  const saveChangesButton = document.getElementById('saveChangesButton');
  const rows = document.querySelectorAll('table tbody tr');
  const devicePopup = document.getElementById('deviceInfoPopup');

  let editModeActive = false;
  let selectedRow = null;

  const column_mapping = {
    'ssn': 'SSN',
    'first_name': 'First Name',
    'last_name': 'Last Name',
    'phone_number': 'Phone Number',
    'mailing_address': 'Mailing Address',
    'member_id': 'Member ID',
    'membership_expires_date': 'Membership Expires Date',
    'current_books_checked_out': 'Current Books Checked Out',
    'subject_name': 'Subject Name',
    'subject_description': 'Subject Description',
    'isbn': 'ISBN',
    'title': 'Title',
    'edition': 'Edition',
    'description': 'Description',
    'barcode_number': 'Barcode Number',
    'loan_id': 'Loan ID',
    'date_borrowed': 'Date Borrowed',
    'due_date': 'Due Date',
    'date_returned': 'Date Returned'
  };

  editDeviceButton.addEventListener('click', () => {
    editModeActive = !editModeActive;

    if (editModeActive) {
      editDeviceButton.classList.add('edit-mode');
      rows.forEach((row) => {
        row.classList.add('edit-mode');
      });
      devicePopup.style.display = 'none';
    } else {
      editDeviceButton.classList.remove('edit-mode');
      rows.forEach((row) => {
        row.classList.remove('edit-mode');
      });
      devicePopup.style.display = 'none';
    }
  });

  rows.forEach((row) => {
    row.addEventListener('click', () => {
      if (editModeActive) {
        const deviceId = row.getAttribute('data-device-id');

        const currentCategory = window.location.pathname.split('/').pop();

        fetch(`/get_columns/${currentCategory}`)
          .then(response => response.json())
          .then(data => {
            const deviceInfo = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());

            const formFields = data.columns.map((column, index) => {
              const columnName = column_mapping[column] || column;
              const columnValue = deviceInfo[index];
              return `
                <label for="${columnName}">${columnName}:</label>
                <input type="text" id="${columnName}" name="${columnName}" value="${columnValue}" required>
                <br>
              `;
            }).join('');

            const buttonsHtml = `
              <button type="submit" id="saveChangesButton">Save Changes</button>
              <button type="button" id="deleteDeviceButton">Delete Device</button>
            `;

            document.getElementById("editDeviceForm").innerHTML = formFields + buttonsHtml;

            selectedRow = row;
            devicePopup.style.display = 'block';
          })
          .catch(error => console.error('Error fetching data:', error));
      }
    });
  });

  document.getElementById('editDeviceForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const updatedDevice = {
      id: selectedRow.getAttribute('data-device-id'),
      category: window.location.pathname.split('/').pop(),
    };

    const columns = document.getElementById("editDeviceForm").querySelectorAll('input[type="text"]');
    columns.forEach(column => {
      const columnName = column.getAttribute('name');
      const originalColumnName = Object.keys(column_mapping).find(key => column_mapping[key] === columnName);
      updatedDevice[originalColumnName || columnName] = column.value;
    });

    fetch('/update_device', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedDevice),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        devicePopup.style.display = 'none';
        location.reload();
      } else {
        console.error(data.error);
        alert('Failed to save changes. Please try again.');
      }
    })
    .catch(error => console.error('Error:', error));
  });

  document.getElementById('editDeviceForm').addEventListener('click', (event) => {
    const target = event.target;

    if (target.matches('#deleteDeviceButton')) {
      const confirmDelete = confirm('Are you sure you want to delete this device?');
      if (confirmDelete) {
        const deviceId = selectedRow.getAttribute('data-device-id');
        const category = window.location.pathname.split('/').pop();
        deleteDevice(deviceId, category);
      }
    }
  });

  function deleteDevice(deviceId, category) {
    const dataToDelete = {
      id: deviceId,
      category: category,
    };

    fetch('/delete_device', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dataToDelete),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else {
        console.error(data.error);
        alert('Failed to delete the device. Please try again.');
      }
    })
    .catch(error => console.error('Error:', error));
  }

  closeDeviceInfoPopup.addEventListener('click', () => {
    devicePopup.style.display = 'none';
  });

  window.addEventListener('click', (event) => {
    if (event.target === devicePopup) {
      devicePopup.style.display = 'none';
    }
  });
});