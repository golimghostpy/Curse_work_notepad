import sys
import socket
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
        username = self.entry_username.text()
        password = self.entry_password.text()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Fill all fields')
            return

        if len(username) > 32:
            QMessageBox.warning(self, 'Login error', 'Login is too long\nMax - 32')
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
            QMessageBox.warning(self, 'Login error', 'Login is too long\nMax - 32')
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

        QMessageBox.information(self, 'Registration', f'User  {username} registered successfully!')
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

        self.contacts_button.clicked.connect(self.switch_to_contacts)
        self.events_button.clicked.connect(self.switch_to_events)

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

class ContactsWindow(QWidget):
    def __init__(self, switch_to_events, switch_to_main):
        super().__init__()
        self.switch_to_events = switch_to_events
        self.switch_to_main = switch_to_main
        self.contacts = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Contacts')

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)

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
        dialog = AddContactDialog(self)
        if dialog.exec_():
            contact = dialog.get_contact()
            if contact:
                self.contacts.append(contact)
                self.list_widget.addItem(QListWidgetItem(f"{contact['last_name']} {contact['first_name']} {contact['phone']}"))

    def remove_contact(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            index = self.list_widget.row(item)
            self.list_widget.takeItem(index)
            del self.contacts[index]

    def item_double_clicked(self, item):
        QMessageBox.information(self, 'Item Double Clicked', f'You double-clicked on {item.text()}')

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

        self.last_name_label = QLabel('Last Name:*', self)
        self.last_name_entry = QLineEdit(self)
        self.form_layout.addRow(self.last_name_label, self.last_name_entry)

        self.first_name_label = QLabel('First Name:*', self)
        self.first_name_entry = QLineEdit(self)
        self.form_layout.addRow(self.first_name_label, self.first_name_entry)

        self.middle_name_label = QLabel('Middle Name:', self)
        self.middle_name_entry = QLineEdit(self)
        self.form_layout.addRow(self.middle_name_label, self.middle_name_entry)

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
        last_name = self.last_name_entry.text()
        first_name = self.first_name_entry.text()
        phone = self.phone_entry.text()

        if not last_name or not first_name or not phone:
            QMessageBox.warning(self, 'Input Error', 'Please enter all required fields.')
            return None

        return {
            'last_name': last_name,
            'first_name': first_name,
            'middle_name': self.middle_name_entry.text(),
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
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)

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

    def item_double_clicked(self, item):
        QMessageBox.information(self, 'Item Double Clicked', f'You double-clicked on {item.text()}')

    def add_event(self):
        event_name, ok = QInputDialog.getText(self, 'Add Event', 'Enter event name:')
        if ok and event_name:
            self.list_widget.addItem(QListWidgetItem(event_name))
            self.calendar.setEvent(self.date, event_name)

    def remove_event(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            event_name = item.text()
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
