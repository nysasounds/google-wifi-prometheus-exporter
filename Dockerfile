FROM alpine:3.17@sha256:ff6bdca1701f3a8a67e328815ff2346b0e4067d32ec36b7992c1fdc001dc8517

ENV SCRIPT_EXPORTER_VERSION=v2.11.0

RUN apk add python3 py3-requests curl ca-certificates

RUN ARCH=$(apk info --print-arch) && \
    case "$ARCH" in \
      x86_64) _arch=amd64 ;; \
      armhf) _arch=armv7 ;; \
      aarch64) _arch=arm64 ;; \
      *) _arch="$ARCH" ;; \
    esac && \
    echo https://github.com/ricoberger/script_exporter/releases/download/${SCRIPT_EXPORTER_VERSION}/script_exporter-linux-${_arch} && \
    curl -kfsSL -o /usr/local/bin/script_exporter \
      https://github.com/ricoberger/script_exporter/releases/download/${SCRIPT_EXPORTER_VERSION}/script_exporter-linux-${_arch} && \
    chmod +x /usr/local/bin/script_exporter

COPY config.yaml /config.yaml
COPY google-wifi-exporter.py /usr/local/bin/google-wifi-exporter.py
RUN chmod 555 /usr/local/bin/google-wifi-exporter.py \
    && chmod 444 /config.yaml

RUN adduser -D google.wifi

USER google.wifi

EXPOSE 9469

ENTRYPOINT  [ "/usr/local/bin/script_exporter", "-log.level", "debug", "-config.file", "/config.yaml" ]
