#include "command_handler.h"

CommandType get_com (const string& command){
    if (command == "login") {return CommandType::LOGIN;}
    return CommandType::UNKNOWN;
}

void authorization(const vector<string>& command){
    string login = command[1], password = command[2];

}

void handle_command()
{
    string str;
    getline(cin, str);

    vector<string> command = split(str, ',');
    CommandType token = get_com(command[0]);
    switch(token){
        case CommandType::LOGIN: authorization(command); break;
        default: cout << "Wrong command " << command[0] << endl; break;
    }
}

int main() {
    try {
        // Параметры подключения
        string connection_string = "dbname=notebook user=postgres password=as180371 host=localhost";

        // Создайте объект соединения
        pqxx::connection C(connection_string);

        // Проверьте соединение
        if (C.is_open()) {
            cout << "Успешное подключение к базе данных: " << C.dbname() << endl;
        } else {
            cerr << "Не удалось открыть базу данных" << endl;
            return 1;
        }

        // Здесь вы можете выполнять SQL-запросы
        pqxx::work W(C);

        W.exec("delete from authentication");

        pqxx::result R = W.exec("SELECT * FROM authentication");

        for (const auto& row : R) {
            cout << "Row: ";
            for (const auto& field : row) {
                cout << field.c_str() << " ";
            }
            cout << endl;
        }

        // Завершите транзакцию
        W.commit();

        // Закройте соединение
        C.close();
    } catch (const exception &e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}
