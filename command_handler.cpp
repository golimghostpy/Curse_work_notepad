#include "command_handler.h"

#include <valarray>

CommandType get_com (const string& command){
    if (command == "login") {return CommandType::LOGIN;}
    if (command == "register") {return CommandType::REG;}
    if (command == "add_contact") {return CommandType::ADD_CONTACT;}
    if (command == "change_password") {return CommandType::CHANGE_PASSWORD;}
    return CommandType::UNKNOWN;
}

string hash_password(const string& password)
{
    string password_hash;
    password_hash = password;
    return password_hash;
}

string registration(pqxx::work& db, const vector<string>& command)
{
    string login = command[1], hashed_password = hash_password(command[2]);

    try
    {
        db.exec_params("insert into authentication (login, password) values ($1, $2)", login, hashed_password);
        db.commit();
    }
    catch (const std::exception& e)
    {
        cout << "Error: " << e.what() << endl;
        return "login already exists";
    }

    return "successful registration";
}

string change_password(pqxx::work& db, const vector<string>& command)
{
    string login = command[1], hashed_old_password = hash_password(command[2]);
    string hashed_new_password = hash_password(command[3]), confirm_new_password = hash_password(command[4]);

    pqxx::result check_password = db.exec_params("select password from authentication where login = $1", login);

    if (hashed_old_password != check_password[0][0].c_str())
    {
        return "old password is wrong";
    }

    if (command[2] == command[3])
    {
        return "can't leave the old password";
    }

    if (command[3] != command[4])
    {
        return "new passwords do not match";
    }

    db.exec_params("update authentication set password = $1 where login = $2", hashed_new_password, login);
    db.commit();
    return "password changed successfully";
}

string authorization(pqxx::work& db, const vector<string>& command){
    string login = command[1], hashed_password = hash_password(command[2]);

    pqxx::result user = db.exec_params("select login, password from authentication where login = $1", login);

    if (user.empty())
    {
        return "wrong login";
    }

    if (user[0][1].c_str() != hashed_password)
    {
        return "wrong password";
    }

    return "successful authorization";
}

string add_contact(pqxx::work& db, const vector<string>& command)
{
    // add_contact owner surname name patronymic birthday city street house_num apartment_num phone_num

    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());

    pqxx::result is_phone = db.exec_params("select * from contacts where phone_number = $1 and owner = $2", command[10], owner);

    for (const auto& row : is_phone) {
        cout << "Row: ";
        for (const auto& field : row) {
            cout << field.c_str() << " ";
        }
        cout << endl;
    }

    if (!is_phone.empty())
    {
        return "contact with this phone number is already exists";
    }

    db.exec_params("insert into contacts (owner, surname, name, patronymic, birthday, city, street, house_number, apartment_number, phone_number) "
                   "values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)",
        owner, command[2], command[3], command[4], command[5], command[6], command[7], command[8], command[9], command[10]);
    db.commit();


    return "successful add_contact";
}

string handle_command(pqxx::work& db)
{
    cout << "Enter command:" << endl;
    string str;
    getline(cin, str);

    vector<string> command = split(str, ' ');
    CommandType token = get_com(command[0]);
    switch(token){
        case CommandType::LOGIN: return authorization(db, command);
        case CommandType::REG: return registration(db, command);
        case CommandType::ADD_CONTACT: return add_contact(db, command);
        case CommandType::CHANGE_PASSWORD: return change_password(db, command);
        default: return "Wrong command " + command[0];
    }
}

int main() {
    try {
        // Параметры подключения
        string connection_string = "dbname=notebook user=postgres password=as180371 host=localhost";

        // Создайте объект соединения
        pqxx::connection db_connection(connection_string);

        // Проверьте соединение
        if (db_connection.is_open()) {
            cout << "Успешное подключение к базе данных: " << db_connection.dbname() << endl;
        } else {
            cerr << "Не удалось открыть базу данных" << endl;
            return 1;
        }

        // Здесь вы можете выполнять SQL-запросы
        pqxx::work db(db_connection);

        db.exec("delete from contacts where phone_number = '89825223100'");
        db.commit();

        cout << handle_command(db) << endl;

        /*
        pqxx::result R = W.exec("SELECT * FROM authentication");

        for (const auto& row : R) {
            cout << "Row: ";
            for (const auto& field : row) {
                cout << field.c_str() << " ";
            }
            cout << endl;
        }


        // Завершите транзакцию
        db.commit();

        */

        // Закройте соединение
        db_connection.close();
    } catch (const exception &e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}
