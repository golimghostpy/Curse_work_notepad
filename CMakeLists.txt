cmake_minimum_required(VERSION 3.29)
project(.)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBPQXX REQUIRED libpqxx)
pkg_check_modules(LIBPQ REQUIRED libpq)
find_package(OpenSSL REQUIRED)

include_directories(${LIBPQXX_INCLUDE_DIRS} ${LIBPQ_INCLUDE_DIRS} ${OPENSSL_INCLUDE_DIR})

link_directories(${LIBPQXX_LIBRARY_DIRS} ${LIBPQ_LIBRARY_DIRS})

add_executable(notebook command_handler.cpp
        general_functions.cpp)
target_link_libraries(notebook ${LIBPQXX_LIBRARIES} ${LIBPQ_LIBRARIES} OpenSSL::Crypto OpenSSL::SSL)