#ifndef CONTACT_H
#define CONTACT_H

#include <iostream>
#include <vector>

using namespace std;

class Contact {
    string name;
    string surname;
    string patronymic;
    string birthday;
    string city;
    string street;
    string house_number;
    string apartment_number;
    string phone_number;

    Contact(vector<string> personal_information): name(personal_information[0]), surname(personal_information[1]),
                                                  patronymic(personal_information[2]), birthday(personal_information[3]),
                                                  city(personal_information[4]), street(personal_information[5]),
                                                  house_number(personal_information[6]), apartment_number(personal_information[7]),
                                                  phone_number(personal_information[8]) {}

};



#endif //CONTACT_H
