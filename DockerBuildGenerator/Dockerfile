FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_EXPORTER_VERSION=1.8.1

# Cập nhật hệ thống và cài đặt các gói cần thiết
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    lsb-release \
    openssh-server \
    sudo \
    uidmap \
    iptables \
    git && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục cần thiết cho SSH
RUN mkdir -p /var/run/sshd

# Thiết lập người dùng root
RUN echo 'root:admin123' | chpasswd

# Tạo user "admin" và thêm vào nhóm sudo
RUN useradd -m -s /bin/bash admin && \
    echo 'admin:admin123' | chpasswd && \
    adduser admin sudo

# Cho phép SSH password login
RUN sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/^#\?PermitEmptyPasswords .*/PermitEmptyPasswords no/' /etc/ssh/sshd_config

# Cài đặt Docker
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Download and install Node Exporter
RUN wget https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz && \
    tar -xzf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz && \
    mv node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter /usr/local/bin/ && \
    rm -rf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64*
# Cho phép user "admin" sử dụng docker mà không cần sudo
RUN usermod -aG docker admin

# Expose SSH and Node Exporter ports
EXPOSE 22 9100

# Start both sshd and node_exporter
CMD /usr/sbin/sshd && /usr/local/bin/node_exporter --web.listen-address="0.0.0.0:9100"
