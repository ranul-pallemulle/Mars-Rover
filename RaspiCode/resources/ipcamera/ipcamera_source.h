#ifndef IPCAMERA_SOURCE_H
#define IPCAMERA_SOURCE_H
#include <string>

int initialise(std::string ip, int port);
int start_stream();
int stop_stream();
int cleanup();


#endif /* IPCAMERA_SOURCE_H */
