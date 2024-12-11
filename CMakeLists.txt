cmake_minimum_required(VERSION 3.29)
project(NoteBook)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBPQXX REQUIRED libpqxx)
pkg_check_modules(LIBPQ REQUIRED libpq)

include_directories(${LIBPQXX_INCLUDE_DIRS} ${LIBPQ_INCLUDE_DIRS})

link_directories(${LIBPQXX_LIBRARY_DIRS} ${LIBPQ_LIBRARY_DIRS})

set(CMAKE_CXX_STANDARD 20)
include_directories(.)

add_executable(notebook
        command_handler.cpp
        Contact.cpp
        Event.cpp
        general_functions.cpp
)

target_link_libraries(notebook ${LIBPQXX_LIBRARIES} ${LIBPQ_LIBRARIES})