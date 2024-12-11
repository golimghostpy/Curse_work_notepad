#include "general_functions.h"

vector<string> split(const string& str, char delimiter) {
    vector<string> splited;
    stringstream ss(str);
    string token;

    while (getline(ss, token, delimiter)) {
        splited.push_back(token);
    }

    return splited;
}