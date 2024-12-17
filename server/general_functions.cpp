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

string join(const vector<string>& vec, const string& delimiter) {
    string result;
    for (size_t i = 0; i < vec.size(); ++i) {
        result += vec[i];
        if (i < vec.size() - 1) {
            result += delimiter;
        }
    }
    return result;
}