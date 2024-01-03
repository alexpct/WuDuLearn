FROM debian:latest

# Update packages and install necessary software
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    nano \
    git \
    sudo \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# Set up SSH
RUN mkdir /var/run/sshd
RUN echo 'root:passwort' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# Add user WuDu, set password, and add to sudoers
RUN useradd -m WuDu && \
    echo "WuDu:passwort" | chpasswd && \
    adduser WuDu sudo

# Expose port 22 for SSH
EXPOSE 22

WORKDIR /workspace

# Start SSH daemon
CMD ["/usr/sbin/sshd", "-D"]
