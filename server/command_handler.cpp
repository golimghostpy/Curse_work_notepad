#include "command_handler.h"

atomic<int> cntThreads(1);

CommandType get_com (const string& command){
    if (command == "login") {return CommandType::LOGIN;}
    if (command == "register") {return CommandType::REG;}
    if (command == "get_contacts") {return CommandType::GET_CONTACTS;}
    if (command == "add_contact") {return CommandType::ADD_CONTACT;}
    if (command == "remove_contact") {return CommandType::REMOVE_CONTACT;}
    if (command == "change_contact") {return CommandType::CHANGE_CONTACT;}
    if (command == "change_password") {return CommandType::CHANGE_PASSWORD;}
    if (command == "get_events") {return CommandType::GET_EVENTS;}
    if (command == "add_event") {return CommandType::ADD_EVENT;}
    if (command == "remove_event") {return CommandType::REMOVE_EVENT;}
    if (command == "change_event") {return CommandType::CHANGE_EVENT;}
    return CommandType::UNKNOWN;
}

string hash_password(const string& password)
{
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, password.c_str(), password.size());
    SHA256_Final(hash, &sha256);

    stringstream ss;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        ss << hex << setw(2) << setfill('0') << (int)hash[i];
    }
    return ss.str();
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
    string login = command[1];
    string hashed_new_password = hash_password(command[2]);

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

string get_contacts(pqxx::work& db, const vector<string>& command)
{
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());

    pqxx::result contacts = db.exec_params("select * from contacts where owner = $1", owner);

    if (contacts.empty())
    {
        return "no contacts";
    }

    string answer = "";
    for (const auto& contact : contacts)
    {
        string one_contact = "";
        for (auto i = 2; i < contact.size() - 1; ++i)
        {
            one_contact += contact[i].as<string>() + ",";
        }
        one_contact += contact[contact.size() - 1].as<string>();
        answer += one_contact + ";";
    }
    return answer;
}

string add_contact(pqxx::work& db, const vector<string>& command)
{
    // add_contact owner surname name patronymic birthday city street house_num apartment_num phone_num

    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());

    pqxx::result is_phone = db.exec_params("select * from contacts where phone_number = $1 and owner = $2", command[10], owner);

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

string remove_contact(pqxx::work& db, const vector<string>& command)
{
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());

    db.exec_params("delete from contacts where phone_number = $1 and owner = $2", command[2], owner);
    db.commit();
    return "successful remove_contact";
}

string change_contact(pqxx::work& db, const vector<string>& command)
{
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());

    db.exec_params("update contacts set surname = $1, name = $2, patronymic = $3, birthday = $4, city = $5, "
                   "street = $6, house_number = $7, apartment_number = $8, phone_number = $9 where owner = $10 and phone_number = $11",
                   command[3], command[4], command[5], command[6], command[7], command[8], command[9], command[10], command[11], owner, command[2]);
    db.commit();
    return "contact changed successfully";
}

string add_event(pqxx::work& db, const vector<string>& command) {
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());
    pqxx::result events = db.exec_params("select event_list from events where owner = $1 and date = $2", owner, command[2]);

    string event_list;
    if (!events.empty()) {
        event_list = events[0][0].as<string>() + "," + command[3];
        db.exec_params("update events set event_list = $1 where owner = $2 and date = $3", event_list, owner, command[2]);
    } else {
        event_list = command[3];
        db.exec_params("insert into events (owner, date, event_list) values ($1, $2, $3)", owner, command[2], event_list);
    }
    db.commit();
    return "successful add_event";
}

string remove_event(pqxx::work& db, const vector<string>& command) {
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());
    pqxx::result events = db.exec_params("select event_list from events where owner = $1 and date = $2", owner, command[2]);

    if (!events.empty()) {
        string event_list = events[0][0].as<string>();
        size_t pos = event_list.find(command[3]);
        if (pos != string::npos) {
            event_list.erase(pos, command[3].length());
            if (!event_list.empty() && event_list.front() == ',') {
                event_list.erase(0, 1);
            }
            if (!event_list.empty() && event_list.back() == ',') {
                event_list.pop_back();
            }
            db.exec_params("update events set event_list = $1 where owner = $2 and date = $3", event_list, owner, command[2]);
        }
    }
    db.commit();
    return "successful remove_event";
}

string change_event(pqxx::work& db, const vector<string>& command) {
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());
    pqxx::result events = db.exec_params("select event_list from events where owner = $1 and date = $2", owner, command[2]);

    if (!events.empty()) {
        string event_list = events[0][0].as<string>();
        size_t pos = event_list.find(command[3]);
        if (pos != string::npos) {
            event_list.replace(pos, command[3].length(), command[4]);
            db.exec_params("update events set event_list = $1 where owner = $2 and date = $3", event_list, owner, command[2]);
        }
    }
    db.commit();
    return "successful change_event";
}

string get_events(pqxx::work& db, const vector<string>& command) {
    int owner = stoi(db.exec_params("select user_id from authentication where login = $1", command[1])[0][0].c_str());
    pqxx::result events = db.exec_params("select date, event_list from events where owner = $1", owner);

    cout << join(command, " ") << endl;

    if (events.empty())
    {
        return "no events";
    }

    string answer = "";
    for (const auto& event : events) {
        cout << event[1].as<string>() << endl;
        answer += event[0].as<string>() + ",";
        for (auto i: split(event[1].as<string>(), ','))
        {
            answer += i + ",";
        }
        answer += ";";
    }
    cout << answer << endl;
    return answer;
}

string handle_command(pqxx::work& db, string request)
{
    vector<string> command = split(request, ' ');
    CommandType token = get_com(command[0]);
    switch(token){
        case CommandType::LOGIN: return authorization(db, command);
        case CommandType::REG: return registration(db, command);
        case CommandType::GET_CONTACTS: return get_contacts(db, command);
        case CommandType::ADD_CONTACT: return add_contact(db, command);
        case CommandType::REMOVE_CONTACT: return remove_contact(db, command);
        case CommandType::CHANGE_CONTACT: return change_contact(db, command);
        case CommandType::CHANGE_PASSWORD: return change_password(db, command);
        case CommandType::ADD_EVENT: return add_event(db, command);
        case CommandType::REMOVE_EVENT: return remove_event(db, command);
        case CommandType::CHANGE_EVENT: return change_event(db, command);
        case CommandType::GET_EVENTS: return get_events(db, command);
        default: return "Wrong command " + command[0];
    }
}

mutex Muter;
void serve_client(int clientSocket, const char* clientIP, pqxx::work& db) {
    ++cntThreads;

    while (true) {
        {
            lock_guard<mutex> lock(Muter);
            vector<char> clientBuffer(1024);

            ssize_t bytesRead = recv(clientSocket, clientBuffer.data(), clientBuffer.size() - 1, 0);
            if (bytesRead <= 0) {
                cout << "Client [" << clientIP << "] was disconnected" << endl;
                break;
            }
            clientBuffer[bytesRead] = '\0';

            string request(clientBuffer.data());

            string answer = handle_command(db, request);
            send(clientSocket, answer.c_str(), answer.size(), 0);
        }
    }

    close(clientSocket);
    --cntThreads;
}

void start_server(pqxx::work& db) {
    int serverSocket;

    if ((serverSocket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        cerr << "Error of create socket" << endl;
        return;
    }

    int opt = 1;
    if (setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == -1) {
        cerr << "Error of setting parameters of socket" << endl;
        return;
    }

    struct sockaddr_in address;
    string serverIP = "0.0.0.0";
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = inet_addr(serverIP.c_str());
    address.sin_port = htons(7432);

    if (bind(serverSocket, (struct sockaddr *)&address, sizeof(address)) < 0) {
        cerr << "Error of binding" << endl;
        return;
    }

    if (listen(serverSocket, 1) < 0) {
        cerr << "Error of socket listening" << endl;
        return;
    }

    cout << "Server started" << endl;

    while (true){
        sockaddr_in clientAddress;
        socklen_t clientSize = sizeof(clientAddress);
        int clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientSize);
        if(clientSocket < 0){
            cout << "Error to connect client" << endl;
            continue;
        }

        if(cntThreads <= 100){
            char* clientIP = inet_ntoa(clientAddress.sin_addr);
            cout << "Client[" << clientIP << "] was connected" << endl;
            thread(serve_client, clientSocket, clientIP, ref(db)).detach();
        }
        else{
            string answer = "A lot of clients now, try it later";
            send(clientSocket, answer.c_str(), answer.size(), 0);
            close(clientSocket);
        }
    }

    close(serverSocket);
}


int main() {
    try {
        string filename = "config.json";

        if (!filesystem::exists(filename)) {
            cout << "File does not exist: " << filename << endl;
            return 1;
        }

        ifstream file(filename);
        if (!file.is_open()) {
            cout << "Error opening file" << endl;
            return 1;
        }

        json config;
        file >> config;


        const string dbname = config["dbname"], user = config["user"], password = config["password"], database_ip = config["database_ip"];
        int port = config["database_port"];

        pqxx::connection db_connection("dbname=" + dbname + " user=" + user + " password=" + password + " host=" + database_ip + " port=" + to_string(port));

        // Проверьте соединение
        if (db_connection.is_open()) {
            cout << "Успешное подключение к базе данных: " << db_connection.dbname() << endl;
        } else {
            cerr << "Не удалось открыть базу данных" << endl;
            return 1;
        }

        // Здесь вы можете выполнять SQL-запросы
        pqxx::work db(db_connection);
        start_server(db);

        // Закройте соединение
        db_connection.disconnect();
    } catch (const exception &e) {
        cerr << e.what() << endl;
        return 1;
    }

    return 0;
}
