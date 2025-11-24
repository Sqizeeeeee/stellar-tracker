FROM ubuntu:22.04 AS builder

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential cmake git \
    libprotobuf-dev protobuf-compiler protobuf-compiler-grpc \
    libgrpc-dev libgrpc++-dev \
    curl wget unzip make \
    ncurses-dev libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*


# Клонируем и собираем find_orb и зависимости
RUN git clone https://github.com/Bill-Gray/lunar.git && \
    git clone https://github.com/Bill-Gray/jpl_eph.git && \
    git clone https://github.com/Bill-Gray/find_orb.git && \
    git clone https://github.com/Bill-Gray/sat_code.git

# Собираем lunar
RUN cd lunar && \
    make && \
    make install PREFIX=/usr/local

# Собираем jpl_eph
RUN cd jpl_eph && \
    make libjpl.a && \
    make install PREFIX=/usr/local


RUN cd lunar && \
    make integrat && \
    make install 

RUN cd sat_code && \
    make && \
    make install PREFIX=/usr/local

# Собираем find_orb с правильной библиотекой sat
RUN cd find_orb && \
    sed -i 's/__float128/long double/g' lsquare.cpp && \
    sed -i 's/-Werror//g' makefile && \
    make LIBS="-L/usr/local/lib -llunar -ljpl -lsatell -lm" && \
    make install

RUN find / -name "find_orb" -type f 2>/dev/null && \
    cp find_orb/find_orb /usr/local/bin/

# Исправляем проблему с find_orb
RUN cd find_orb && \
    make clean && \
    make LIBS="-L/usr/local/lib -llunar -ljpl -lsatell -lm" && \
    cp find_orb /usr/local/bin/

# Создаем базовый конфиг для find_orb
RUN mkdir -p /root/.find_orb && \
    echo -e "! Find_Orb configuration file\nephemeris_file = /root/.find_orb/linux_p1550p2650.430t\nobs_long = 0.0\nobs_lat = 51.4778\nobs_alt = 0.0" > /root/.find_orb/find_orb.cfg

WORKDIR /src
COPY . .

# Генерируем proto файлы для orbit-service
RUN mkdir -p orbit-service/proto && \
    protoc \
      --cpp_out=orbit-service/proto \
      --grpc_out=orbit-service/proto \
      --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin \
      --proto_path=proto \
      proto/astro.proto

# Собираем наш orbit-service
WORKDIR /src/orbit-service
RUN mkdir -p build && cd build && \
    cmake .. && \
    cmake --build .


# Runtime образ
FROM ubuntu:22.04

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y wget \
    libprotobuf23 libgrpc++1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копируем бинарники из builder-стадии
COPY --from=builder /usr/local/bin/find_orb /usr/local/bin/
COPY --from=builder /src/orbit-service/build/orbit_service /usr/local/bin/

EXPOSE 50052
CMD ["/usr/local/bin/orbit_service"]

# Создаем директорию конфигурации find_orb и скачиваем JPL ephemeris
RUN mkdir -p /root/.find_orb && \
    cd /root/.find_orb && \
    wget ftp://ssd.jpl.nasa.gov/pub/eph/planets/Linux/de430t/linux_p1550p2650.430t