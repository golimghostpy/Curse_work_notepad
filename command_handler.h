#ifndef COMMAND_HANDLER_H
#define COMMAND_HANDLER_H

#include <iostream>
#include <vector>
#include "general_functions.h"
#include <pqxx/pqxx>
#define _BSD_SOURCE 1
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <thread>
#include <mutex>
#include <atomic>
#include <format>
#include <valarray>
#include <openssl/sha.h>
#include <iomanip>

enum class CommandType {
    LOGIN,
    REG,
    GET_CONTACTS,
    ADD_CONTACT,
    REMOVE_CONTACT,
    CHANGE_CONTACT,
    CHANGE_PASSWORD,
    GET_EVENTS,
    ADD_EVENT,
    REMOVE_EVENT,
    CHANGE_EVENT,
    UNKNOWN
};

using namespace std;

#endif //COMMAND_HANDLER_H
