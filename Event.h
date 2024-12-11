#ifndef EVENT_H
#define EVENT_H

#include <iostream>
#include <vector>
#include "general_functions.h"

using namespace std;

class Event {
    string event_date;
    vector<string> event_list;

    Event(string date, string events): event_date(date), event_list(split(events, ',')) {}
};

#endif //EVENT_H
