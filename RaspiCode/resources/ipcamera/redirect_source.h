#ifndef REDIRECT_SOURCE_H
#define REDIRECT_SOURCE_H
#include <string>
int start_redirect(std::string source_ip, int source_port,
		   std::string dest_ip, int dest_port);
int stop_redirect();

#endif /* REDIRECT_SOURCE_H */
