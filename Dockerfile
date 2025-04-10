FROM alpine:latest

ARG PB_VERSION=0.26.6

RUN apk add --no-cache unzip ca-certificates curl

ADD https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip /tmp/pb.zip
RUN unzip -o /tmp/pb.zip -d /pb/ && chmod +x /pb/pocketbase

EXPOSE 8080

CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8080"]
