ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
# COPY run.sh /
# RUN chmod a+x /run.sh

# CMD [ "/run.sh" ]
ENV LANG C.UTF-8

WORKDIR /app
RUN apk add --update --no-cache dumb-init python3 py3-pip

RUN pip3 install --no-cache-dir -U pyserial yaml
COPY /app/ /app/
COPY start.sh /app/start.sh
RUN chmod a+x /app/start.sh

#ENTRYPOINT ["/app/start.sh"]
CMD [ "/app/start.sh" ]