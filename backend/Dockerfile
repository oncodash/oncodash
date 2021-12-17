FROM python:3.7-alpine

# ERROR logs are sent to terminal
ENV PYTHONUNBUFFERED=1

# no __pycache__ written by container root in the bindmount
# Would end up in permission errors when building 
ENV PYTHONDONTWRITEBYTECODE=1 

# Add non-privliged user that will be used when running the container
ARG UNAME=djangouser
RUN adduser -D $UNAME

# Update apk and install python3 headers for numpy
RUN apk update
RUN apk add python3-dev

# install c++ compilers for pandas & numpy installations
RUN apk add --no-cache --virtual .build-deps \
    make \
    automake \
    gcc \
    g++ \
    subversion

# Copy in source code and set up rights 
RUN mkdir /opt/app/ && chown $UNAME:$UNAME /opt/app/
WORKDIR /opt/app
COPY --chown=$UNAME:$UNAME ./requirements.txt ./requirements.txt
ENV PATH /home/$UNAME/.local/bin:$PATH

# install deps
RUN pip install -U pip \
    && pip install -U setuptools \
    && pip install -r requirements.txt

# remove build-deps
RUN apk del .build-deps

# copy in the source code
COPY --chown=$UNAME:$UNAME . .

EXPOSE 8888
USER $UNAME

# Run gunicorn web server
CMD ["gunicorn", "core.wsgi", "--bind", "0.0.0.0:8888"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]