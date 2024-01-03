#include <libssh/libssh.h>
#include <iostream>
#include <string>
#include <memory>

// Funktion zur Initialisierung einer SSH-Session
ssh_session initialize_ssh_session(const char* host, const char* user, const char* password) {
    ssh_session session = ssh_new();
    if (session == nullptr) {
        throw std::runtime_error("Failed to create SSH session");
    }

    ssh_options_set(session, SSH_OPTIONS_HOST, host);
    ssh_options_set(session, SSH_OPTIONS_USER, user);

    int rc = ssh_connect(session);
    if (rc != SSH_OK) {
        ssh_free(session);
        throw std::runtime_error("Failed to connect to SSH host");
    }

    rc = ssh_userauth_password(session, NULL, password);
    if (rc != SSH_AUTH_SUCCESS) {
        ssh_disconnect(session);
        ssh_free(session);
        throw std::runtime_error("Failed to authenticate with SSH host");
    }

    return session;
}

// Funktion zur Ausführung eines Befehls über SSH
std::string execute_ssh_command(ssh_session session, const std::string& command) {
    ssh_channel channel = ssh_channel_new(session);
    if (channel == nullptr) {
        throw std::runtime_error("Failed to create SSH channel");
    }

    int rc = ssh_channel_open_session(channel);
    if (rc != SSH_OK) {
        ssh_channel_free(channel);
        throw std::runtime_error("Failed to open SSH channel");
    }

    rc = ssh_channel_request_exec(channel, command.c_str());
    if (rc != SSH_OK) {
        ssh_channel_close(channel);
        ssh_channel_free(channel);
        throw std::runtime_error("Failed to execute command");
    }

    std::string response;
    char buffer[256];
    int nbytes;
    while ((nbytes = ssh_channel_read(channel, buffer, sizeof(buffer), 0)) > 0) {
        response.append(buffer, nbytes);
    }

    ssh_channel_close(channel);
    ssh_channel_free(channel);

    return response;
}

int main(int argc, char** argv) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " <user> <password> <host>\n";
        return 1;
    }

    const char* user = argv[1];
    const char* password = argv[2];
    const char* host = argv[3];

    try {
        ssh_session session = initialize_ssh_session(host, user, password);

        std::string command;
        while (true) {
            std::cout << "Enter command: ";
            std::getline(std::cin, command);
            if (command == "exit") break;

            std::string response = execute_ssh_command(session, command);
            std::cout << "Response:\n" << response << std::endl;
        }

        ssh_disconnect(session);
        ssh_free(session);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
