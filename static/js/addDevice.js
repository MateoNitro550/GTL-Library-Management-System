// JavaScript to handle the add device function
const addDeviceButton = document.getElementById("addDeviceButton");
const addDevicePopup = document.getElementById("addDevicePopup");
const closeAddDevicePopup = document.getElementById("closeAddDevicePopup");

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

addDeviceButton.addEventListener("click", () => {
    const currentCategory = window.location.pathname.split('/').pop();

    fetch(`/get_columns/${currentCategory}`)
        .then(response => response.json())
        .then(data => {
            const formFields = data.columns.map(column => {
                return `
                    <label for="${column}">${column_mapping[column] || column}:</label>
                    <input type="text" id="${column}" name="${column}" required>
                    <br>
                `;
            }).join('');

            const submitButton = '<button type="submit">Add Device</button>';

            document.getElementById("addDeviceForm").innerHTML = formFields + submitButton;

            document.getElementById("addDeviceForm").innerHTML += `<input type="hidden" name="category" value="${currentCategory}">`;

            addDevicePopup.style.display = "block";
        });
});

closeAddDevicePopup.addEventListener("click", () => {
    addDevicePopup.style.display = "none";
});

window.addEventListener("click", (event) => {
    if (event.target === addDevicePopup) {
        addDevicePopup.style.display = "none";
    }
});
