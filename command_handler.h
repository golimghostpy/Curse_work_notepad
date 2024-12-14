#ifndef COMMAND_HANDLER_H
#define COMMAND_HANDLER_H

#include <iostream>
#include <vector>
#include "Contact.h"
#include "Event.h"
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

enum class CommandType {
    LOGIN,
    REG,
    ADD_CONTACT,
    CHANGE_PASSWORD,
    UNKNOWN
};

using namespace std;

#endif //COMMAND_HANDLER_H
