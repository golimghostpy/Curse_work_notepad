FROM gcc:14.2.0

ARG UID=10001
ARG GID=10001

RUN apt-get update && apt-get install -y libssl-dev libpqxx-dev libpq-dev cmake g++ nlohmann-json3-dev logrotate
COPY logrotate.conf /etc/logrotate.d/logrotate.conf

WORKDIR /app

COPY . .

RUN groupadd -g $GID tester && \
    useradd -u $UID -g $GID -m tester


RUN chown -R tester:tester /app

USER tester

RUN cmake .
RUN make

EXPOSE 5432
EXPOSE 7432

CMD ["./notebook"]
