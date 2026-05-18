FROM golang:1.22-alpine AS builder

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o gateway ./cmd/gateway

FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /build/gateway /gateway

EXPOSE 8080

ENTRYPOINT ["/gateway"]
