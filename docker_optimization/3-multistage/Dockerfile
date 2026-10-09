FROM golang:1.22 AS builder

WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server .

FROM alpine:3.20
COPY --from=builder /app/server /server
USER nobody
EXPOSE 8000
CMD ["/server"]
