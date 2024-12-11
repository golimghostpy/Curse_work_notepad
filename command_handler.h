#ifndef COMMAND_HANDLER_H
#define COMMAND_HANDLER_H

#include <iostream>
#include <vector>
#include "Contact.h"
#include "Event.h"
#include "general_functions.h"
#include <pqxx/pqxx>

enum class CommandType {
    LOGIN,
    UNKNOWN
};

using namespace std;

#endif //COMMAND_HANDLER_H
