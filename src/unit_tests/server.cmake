# Find the securics shared library
find_library(SECURICSEXT NAMES libsecuricsext.so HINTS "${SRC_FOLDER}")
set(uname "Linux")

if(NOT SECURICSEXT)
    message(FATAL_ERROR "libsecuricsext not found! Aborting...")
endif()

# Add compiling flags
add_compile_options(-ggdb -O0 -g -coverage -DTEST_SERVER -DENABLE_AUDIT -DINOTIFY_ENABLED -fsanitize=address -fsanitize=undefined)
link_libraries(-fsanitize=address -fsanitize=undefined)
# Set tests dependencies
set(TEST_DEPS ${SECURICSLIB} ${SECURICSEXT} -lpthread -ldl -lcmocka -fprofile-arcs -ftest-coverage)

add_subdirectory(analysisd)
add_subdirectory(remoted)
add_subdirectory(securics_db)
add_subdirectory(os_auth)
add_subdirectory(os_crypto)
add_subdirectory(securics_modules)
add_subdirectory(monitord)
add_subdirectory(logcollector)
add_subdirectory(os_execd)
add_subdirectory(os_integrator)
add_subdirectory(addagent)
add_subdirectory(os_maild)
add_subdirectory(os_csyslogd)
