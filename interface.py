import sys
import socket
from multiprocessing.connection import answer_challenge

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
    QDialog,
    QDialogButtonBox,
    QInputDialog,
    QFormLayout,
    QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QPainter, QColor

clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_to_server(message):
    try:
        clientSock.sendall(message.encode())
        response = clientSock.recv(1024)
        return response.decode()
    except Exception as e:
        print(f"Error communicating with server: {e}")

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = {}

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events:
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(rect.topLeft() + QPoint(3, 3), 3, 3)

    def setEvent(self, date, event):
        if date not in self.events:
            self.events[date] = []
        self.events[date].append(event)
        self.updateCell(date)

    def getEvents(self, date):
        return self.events.get(date, [])

    def removeEvent(self, date, event):
        if date in self.events:
            self.events[date].remove(event)
            if not self.events[date]:
                del self.events[date]
            self.updateCell(date)

def check_sql_injection(to_check, what_to_check):
    for i in to_check:
        if what_to_check == 'login' and not (i.isalnum() or i == '_'):
            return True
        elif what_to_check == 'password' and not(i.isalnum() or i in '!#$%&()*+-:;<=>?@[]^_{|}~'):
            return True

current_login = None
current_password = None

class LoginWindow(QWidget):
    def __init__(self, switch_to_register, switch_to_main):
        super().__init__()
        self.switch_to_register = switch_to_register
        self.switch_to_main = switch_to_main
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')

        self.label_username = QLabel('Username:', self)
        self.entry_username = QLineEdit(self)
        self.label_password = QLabel('Password:', self)
        self.entry_password = QLineEdit(self)
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login', self)
        self.register_button = QPushButton('Sign up', self)

        self.login_button.clicked.connect(self.login_user)
        self.register_button.clicked.connect(self.switch_to_register)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

    def login_user(self):
        global current_login, current_password
        username = self.entry_username.text()
        password = self.entry_password.text()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Fill all fields')
            return

        if len(username) > 32:
            QMessageBox.warning(self, 'Login error', 'Username is too long\nMax - 32')
            return
        if len(password) > 32:
            QMessageBox.warning(self, 'Password error', 'Password is too long\nMax - 32')
            return

        if check_sql_injection(username, 'login'):
            QMessageBox.warning(self, 'Login error', 'Prohibited characters in login')
            return
        if check_sql_injection(password, 'password'):
            QMessageBox.warning(self, 'Password error', 'Prohibited characters in password')
            return

        answer = send_to_server(f"login {username} {password}")

        if answer == "wrong login":
            QMessageBox.warning(self, 'Login error', 'Wrong login')
        elif answer == "wrong password":
            QMessageBox.warning(self, 'Password error', 'Wrong password')
        else:
            current_login = username
            current_password = password
            self.switch_to_main()

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                margin: 10px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class RegistrationWindow(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Registration')

        self.label_username = QLabel('Username:', self)
        self.entry_username = QLineEdit(self)
        self.label_password = QLabel('Password:', self)
        self.entry_password = QLineEdit(self)
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.label_confirm_password = QLabel('Confirm Password:', self)
        self.entry_confirm_password = QLineEdit(self)
        self.entry_confirm_password.setEchoMode(QLineEdit.Password)
        self.register_button = QPushButton('Register', self)
        self.back_button = QPushButton('Sign in', self)

        self.register_button.clicked.connect(self.register_user)
        self.back_button.clicked.connect(self.switch_to_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.entry_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.entry_password)
        layout.addWidget(self.label_confirm_password)
        layout.addWidget(self.entry_confirm_password)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

    def register_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()
        confirm_password = self.entry_confirm_password.text()

        if not(username and password and confirm_password):
            QMessageBox.warning(self, 'Input Error', 'Please enter all fields.')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Input Error', 'Passwords do not match. Please try again.')
            return

        if len(username) > 32:
            QMessageBox.warning(self, 'Login error', 'Username is too long\nMax - 32')
            return
        if len(password) > 32:
            QMessageBox.warning(self, 'Password error', 'Password is too long\nMax - 32')
            return

        if check_sql_injection(username, 'login'):
            QMessageBox.warning(self, 'Login error', 'Prohibited characters in login')
            return
        if check_sql_injection(password, 'password'):
            QMessageBox.warning(self, 'Password error', 'Prohibited characters in password')
            return

        answer = send_to_server(f"register {username} {password} {confirm_password}")

        if answer == "login already exists":
            QMessageBox.warning(self, 'Login error', 'User with this name is already exists')
            return

        QMessageBox.information(self, 'Registration', f'User {username} registered successfully!')
        self.entry_username.clear()
        self.entry_password.clear()
        self.entry_confirm_password.clear()

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                margin: 10px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class MainWindow(QWidget):
    def __init__(self, switch_to_contacts, switch_to_events):
        super().__init__()
        self.switch_to_contacts = switch_to_contacts
        self.switch_to_events = switch_to_events
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Application')

        self.label_change_password = QLabel('Change Password:', self)
        self.label_old_password = QLabel('Old Password:', self)
        self.entry_old_password = QLineEdit(self)
        self.entry_old_password.setEchoMode(QLineEdit.Password)
        self.label_new_password = QLabel('New Password:', self)
        self.entry_new_password = QLineEdit(self)
        self.entry_new_password.setEchoMode(QLineEdit.Password)
        self.label_confirm_new_password = QLabel('Confirm New Password:', self)
        self.entry_confirm_new_password = QLineEdit(self)
        self.entry_confirm_new_password.setEchoMode(QLineEdit.Password)
        self.change_password_button = QPushButton('Change Password', self)
        self.contacts_button = QPushButton('My Contacts', self)
        self.events_button = QPushButton('My Events', self)

        layout = QVBoxLayout()
        layout.addWidget(self.label_change_password)
        layout.addWidget(self.label_old_password)
        layout.addWidget(self.entry_old_password)
        layout.addWidget(self.label_new_password)
        layout.addWidget(self.entry_new_password)
        layout.addWidget(self.label_confirm_new_password)
        layout.addWidget(self.entry_confirm_new_password)
        layout.addWidget(self.change_password_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.contacts_button)
        button_layout.addWidget(self.events_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

        self.change_password_button.clicked.connect(self.change_password)
        self.contacts_button.clicked.connect(self.switch_to_contacts)
        self.events_button.clicked.connect(self.switch_to_events)

    def change_password(self):
        global current_login, current_password
        old_password = self.entry_old_password.text()
        new_password = self.entry_new_password.text()
        confirm_new_password = self.entry_confirm_new_password.text()

        if not(old_password and new_password and confirm_new_password):
            QMessageBox.warning(self, 'Input Error', 'Please enter all fields.')
            return

        if old_password != current_password:
            QMessageBox.warning(self, 'Password Error', 'Old password is incorrect')
            return

        if len(new_password) > 32:
            QMessageBox.warning(self, 'Password error', 'New password is too long\nMax - 32')
            return

        if new_password != confirm_new_password:
            QMessageBox.warning(self, 'Password Error', 'Passwords do not match. Please try again.')
            return

        if check_sql_injection(new_password, 'password'):
            QMessageBox.warning(self, 'Password error', 'Prohibited characters in password')
            return

        if old_password == new_password:
            QMessageBox.warning(self, 'Password Error', 'Can\'t leave the old password')
            return

        answer = send_to_server(f"change_password {current_login} {new_password}")

        QMessageBox.information(self, 'Change password', f'Password changed successfully')
        current_password = new_password
        self.entry_old_password.clear()
        self.entry_new_password.clear()
        self.entry_confirm_new_password.clear()

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                margin: 10px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

contacts = []
class ContactsWindow(QWidget):
    def __init__(self, switch_to_events, switch_to_main):
        super().__init__()
        self.switch_to_events = switch_to_events
        self.switch_to_main = switch_to_main
        self.initUI()
        self.load_contacts()

    def load_contacts(self):
        global contacts, current_login

        answer = send_to_server(f'get_contacts {current_login}')[:-1]

        contact_matrix = [[j for j in i.split(',')] for i in answer.split(';')]
        for contact in contact_matrix:
            contacts.append({
                'surname': contact[0],
                'name': contact[1],
                'patronymic': contact[2],
                'birth_date': contact[3],
                'city': contact[4],
                'street': contact[5],
                'house_number': contact[6],
                'apartment_number': contact[7],
                'phone': contact[8]
            })

            self.list_widget.addItem(QListWidgetItem(f"{contact[0]} {contact[1]} {contact[8]}"))

    def initUI(self):
        self.setWindowTitle('Contacts')

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.change_contact)

        self.add_button = QPushButton('Add Contact', self)
        self.remove_button = QPushButton('Remove Contact', self)
        self.events_button = QPushButton('My Events', self)
        self.change_password_button = QPushButton('Change Password', self)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.events_button)
        button_layout.addWidget(self.change_password_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

        self.add_button.clicked.connect(self.add_contact)
        self.remove_button.clicked.connect(self.remove_contact)
        self.events_button.clicked.connect(self.switch_to_events)
        self.change_password_button.clicked.connect(self.switch_to_main)

    def add_contact(self):
        global contacts, current_login
        dialog = AddContactDialog(self)
        if dialog.exec_():
            contact = dialog.get_contact()
            if contact:
                request = f'add_contact {current_login} '
                for i in contact.values():
                    request += i + ' '

                answer = send_to_server(request.strip())

                if answer == 'contact with this phone number is already exists':
                    QMessageBox.warning(self, 'Contact error', 'You already have this contact')
                    return

                contacts.append(contact)
                self.list_widget.addItem(QListWidgetItem(f"{contact['surname']} {contact['name']} {contact['phone']}"))

    def remove_contact(self):
        global contacts, current_login
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            index = self.list_widget.row(item)
            self.list_widget.takeItem(index)

            request = f'remove_contact {current_login} {contacts[index]['phone']}'
            send_to_server(request)

            del contacts[index]

    def change_contact(self, item):
        global contacts
        index = self.list_widget.row(item)
        contact = contacts[index]
        dialog = EditContactDialog(contact, self)
        if dialog.exec_():
            updated_contact = dialog.get_contact()
            if updated_contact:
                request = f'change_contact {current_login} {contacts[index]['phone']} '
                contacts[index] = updated_contact
                for i in updated_contact.values():
                    request += i + ' '

                send_to_server(request.strip())

                QMessageBox.information(self, 'Change contact', f'Contact changed successfully')
                item.setText(f"{updated_contact['surname']} {updated_contact['name']} {updated_contact['phone']}")


    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """


class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add Contact')

        self.form_layout = QFormLayout()

        self.surname_label = QLabel('Surname:*', self)
        self.surname_entry = QLineEdit(self)
        self.form_layout.addRow(self.surname_label, self.surname_entry)

        self.name_label = QLabel('Name:*', self)
        self.name_entry = QLineEdit(self)
        self.form_layout.addRow(self.name_label, self.name_entry)

        self.patronymic_label = QLabel('Patronymic:', self)
        self.patronymic_entry = QLineEdit(self)
        self.form_layout.addRow(self.patronymic_label, self.patronymic_entry)

        self.birth_date_label = QLabel('Birth Date:', self)
        self.birth_date_entry = QDateEdit(self)
        self.birth_date_entry.setCalendarPopup(True)
        self.form_layout.addRow(self.birth_date_label, self.birth_date_entry)

        self.city_label = QLabel('City:', self)
        self.city_entry = QLineEdit(self)
        self.form_layout.addRow(self.city_label, self.city_entry)

        self.street_label = QLabel('Street:', self)
        self.street_entry = QLineEdit(self)
        self.form_layout.addRow(self.street_label, self.street_entry)

        self.house_number_label = QLabel('House Number:', self)
        self.house_number_entry = QLineEdit(self)
        self.form_layout.addRow(self.house_number_label, self.house_number_entry)

        self.apartment_number_label = QLabel('Apartment Number:', self)
        self.apartment_number_entry = QLineEdit(self)
        self.form_layout.addRow(self.apartment_number_label, self.apartment_number_entry)

        self.phone_label = QLabel('Phone Number:*', self)
        self.phone_entry = QLineEdit(self)
        self.form_layout.addRow(self.phone_label, self.phone_entry)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

    def get_contact(self):
        last_name = self.surname_entry.text()
        first_name = self.name_entry.text()
        phone = self.phone_entry.text()

        if not last_name or not first_name or not phone:
            QMessageBox.warning(self, 'Input Error', 'Please enter all required fields.')
            return None

        return {
            'surname': last_name,
            'name': first_name,
            'patronymic': self.patronymic_entry.text(),
            'birth_date': self.birth_date_entry.date().toString('yyyy-MM-dd'),
            'city': self.city_entry.text(),
            'street': self.street_entry.text(),
            'house_number': self.house_number_entry.text(),
            'apartment_number': self.apartment_number_entry.text(),
            'phone': phone
        }

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                margin: 10px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EditContactDialog(QDialog):
    def __init__(self, contact, parent=None):
        super().__init__(parent)
        self.contact = contact
        self.original_contact = contact.copy()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Edit Contact')

        self.form_layout = QFormLayout()

        self.surname_label = QLabel('Surname:*', self)
        self.surname_entry = QLineEdit(self)
        self.surname_entry.setText(self.contact.get('surname', ''))
        self.surname_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.surname_label, self.surname_entry)

        self.name_label = QLabel('Name:*', self)
        self.name_entry = QLineEdit(self)
        self.name_entry.setText(self.contact.get('name', ''))
        self.name_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.name_label, self.name_entry)

        self.patronymic_label = QLabel('Patronymic:', self)
        self.patronymic_entry = QLineEdit(self)
        self.patronymic_entry.setText(self.contact.get('patronymic', ''))
        self.patronymic_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.patronymic_label, self.patronymic_entry)

        self.birth_date_label = QLabel('Birth Date:', self)
        self.birth_date_entry = QDateEdit(self)
        self.birth_date_entry.setCalendarPopup(True)
        birth_date = QDate.fromString(self.contact.get('birth_date', ''), 'yyyy-MM-dd')
        self.birth_date_entry.setDate(birth_date)
        self.birth_date_entry.dateChanged.connect(self.check_changes)
        self.form_layout.addRow(self.birth_date_label, self.birth_date_entry)

        self.city_label = QLabel('City:', self)
        self.city_entry = QLineEdit(self)
        self.city_entry.setText(self.contact.get('city', ''))
        self.city_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.city_label, self.city_entry)

        self.street_label = QLabel('Street:', self)
        self.street_entry = QLineEdit(self)
        self.street_entry.setText(self.contact.get('street', ''))
        self.street_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.street_label, self.street_entry)

        self.house_number_label = QLabel('House Number:', self)
        self.house_number_entry = QLineEdit(self)
        self.house_number_entry.setText(self.contact.get('house_number', ''))
        self.house_number_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.house_number_label, self.house_number_entry)

        self.apartment_number_label = QLabel('Apartment Number:', self)
        self.apartment_number_entry = QLineEdit(self)
        self.apartment_number_entry.setText(self.contact.get('apartment_number', ''))
        self.apartment_number_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.apartment_number_label, self.apartment_number_entry)

        self.phone_label = QLabel('Phone Number:*', self)
        self.phone_entry = QLineEdit(self)
        self.phone_entry.setText(self.contact.get('phone', ''))
        self.phone_entry.textChanged.connect(self.check_changes)
        self.form_layout.addRow(self.phone_label, self.phone_entry)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setEnabled(False)
        self.button_box.accepted.connect(self.save_contact)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

    def check_changes(self):
        current_contact = self.get_contact()
        if current_contact != self.original_contact:
            self.button_box.button(QDialogButtonBox.Save).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Save).setEnabled(False)

    def save_contact(self):
        current_contact = self.get_contact()
        if current_contact == self.original_contact:
            QMessageBox.warning(self, 'No Changes', 'No changes have been made.')
        elif not current_contact:
            QMessageBox.warning(self, 'Input Error', 'Please enter all required fields.')
        else:
            self.accept()

    def get_contact(self):
        surname = self.surname_entry.text()
        name = self.name_entry.text()
        phone = self.phone_entry.text()

        if not (surname and name and phone):
            return None

        return {
            'surname': surname,
            'name': name,
            'patronymic': self.patronymic_entry.text(),
            'birth_date': self.birth_date_entry.date().toString('yyyy-MM-dd'),
            'city': self.city_entry.text(),
            'street': self.street_entry.text(),
            'house_number': self.house_number_entry.text(),
            'apartment_number': self.apartment_number_entry.text(),
            'phone': phone
        }

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                margin: 10px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EventsWindow(QWidget):
    def __init__(self, switch_to_contacts, switch_to_main):
        super().__init__()
        self.switch_to_contacts = switch_to_contacts
        self.switch_to_main = switch_to_main
        self.initUI()
        self.load_events()

    def initUI(self):
        self.setWindowTitle('Events')

        self.calendar = CustomCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.show_events_for_date)

        self.contacts_button = QPushButton('My Contacts', self)
        self.change_password_button = QPushButton('Change Password', self)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.contacts_button)
        button_layout.addWidget(self.change_password_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

        self.contacts_button.clicked.connect(self.switch_to_contacts)
        self.change_password_button.clicked.connect(self.switch_to_main)

    def load_events(self):
        global current_login
        answer = send_to_server(f"get_events {current_login}")[:-1]
        event_matrix = [[j for j in i.split(' ')[:-1]] for i in answer.split(';')]
        for event in event_matrix:
            if len(event) >= 2:
                date_str = event[0]
                events = event[1:]
                date = QDate.fromString(date_str, 'yyyy-MM-dd')
                if date.isValid():
                    for i in events:
                        self.calendar.setEvent(date, i)

    def show_events_for_date(self, date):
        dialog = EventListDialog(date, self.calendar, self)
        dialog.exec_()

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QCalendarWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

class EventListDialog(QDialog):
    def __init__(self, date, calendar, parent=None):
        super().__init__(parent)
        self.date = date
        self.calendar = calendar
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Events for {self.date.toString("MMMM d, yyyy")}')

        self.list_widget = QListWidget(self)
        events = self.calendar.getEvents(self.date)
        for event in events:
            self.list_widget.addItem(QListWidgetItem(event))
        self.list_widget.itemDoubleClicked.connect(self.change_event)

        self.add_button = QPushButton('Add Event', self)
        self.remove_button = QPushButton('Remove Event', self)
        self.close_button = QPushButton('Close', self)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet(self.get_stylesheet())

        self.add_button.clicked.connect(self.add_event)
        self.remove_button.clicked.connect(self.remove_event)
        self.close_button.clicked.connect(self.close)

    def change_event(self, item):
        old_event_name = item.text()
        new_event_name, ok = QInputDialog.getText(self, 'Change Event', 'Enter new event name:', text=old_event_name)
        if ok and new_event_name:
            answer = send_to_server(f"change_event {current_login} {self.date.toString('yyyy-MM-dd')} {old_event_name} {new_event_name}")
            if answer == "successful change_event":
                self.calendar.removeEvent(self.date, old_event_name)
                self.calendar.setEvent(self.date, new_event_name)
                item.setText(new_event_name)

    def add_event(self):
        event_name, ok = QInputDialog.getText(self, 'Add Event', 'Enter event name:')
        if ok and event_name:
            answer = send_to_server(f"add_event {current_login} {self.date.toString('yyyy-MM-dd')} {event_name}")
            if answer == "successful add_event":
                self.list_widget.addItem(QListWidgetItem(event_name))
                self.calendar.setEvent(self.date, event_name)

    def remove_event(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            event_name = item.text()
            answer = send_to_server(f"remove_event {current_login} {self.date.toString('yyyy-MM-dd')} {event_name}")
            if answer == "successful remove_event":
                self.calendar.removeEvent(self.date, event_name)
                self.list_widget.takeItem(self.list_widget.row(item))

    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

login_window = None
registration_window = None
main_window = None
contacts_window = None
events_window = None

def show_login_window():
    global login_window
    login_window = LoginWindow(switch_to_registration, switch_to_main)
    login_window.resize(300, 300)
    login_window.show()

def show_registration_window():
    global registration_window
    registration_window = RegistrationWindow(switch_to_login)
    registration_window.resize(300, 300)
    registration_window.show()

def show_main_window():
    global main_window
    main_window = MainWindow(switch_to_contacts, switch_to_events)
    main_window.resize(300, 400)
    main_window.show()

def show_contacts_window():
    global contacts_window
    contacts_window = ContactsWindow(switch_to_events, switch_to_main)
    contacts_window.resize(300, 400)
    contacts_window.show()

def show_events_window():
    global events_window
    events_window = EventsWindow(switch_to_contacts, switch_to_main)
    events_window.resize(300, 400)
    events_window.show()

def switch_to_registration():
    global login_window, registration_window
    if login_window:
        login_window.close()
    show_registration_window()

def switch_to_login():
    global registration_window, login_window
    if registration_window:
        registration_window.close()
    show_login_window()

def switch_to_main():
    global login_window, main_window, contacts_window, events_window
    if login_window:
        login_window.close()
    if contacts_window:
        contacts_window.close()
    if events_window:
        events_window.close()
    show_main_window()

def switch_to_contacts():
    global main_window, contacts_window
    if main_window:
        main_window.close()
    if events_window:
        events_window.close()
    show_contacts_window()

def switch_to_events():
    global main_window, events_window
    if main_window:
        main_window.close()
    if contacts_window:
        contacts_window.close()
    show_events_window()

if __name__ == '__main__':
    dbIP, dbPort = "localhost", 7432
    serverAddr = (str(dbIP), int(dbPort))
    clientSock.connect(serverAddr)

    app = QApplication(sys.argv)
    show_login_window()
    sys.exit(app.exec_())
