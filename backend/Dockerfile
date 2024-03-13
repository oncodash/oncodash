FROM python:3.8-slim-bookworm

# ERROR logs are sent to terminal
ENV PYTHONUNBUFFERED=1

# no __pycache__ written by container root in the bindmount
# Would end up in permission errors when building
ENV PYTHONDONTWRITEBYTECODE=1

# Add non-privileged user that will be used when running the container
ARG UNAME=djangouser
RUN adduser --disabled-login $UNAME

# Update apk and install python3 headers for numpy
RUN apt-get update
RUN apt-get install -y python3-dev

# Copy in source code and set up rights
RUN mkdir /opt/app/ && chown $UNAME:$UNAME /opt/app/
WORKDIR /opt/app
COPY --chown=$UNAME:$UNAME ./requirements.txt ./requirements.txt
ENV PATH /home/$UNAME/.local/bin:$PATH

# install deps
RUN pip install -U pip \
    && pip install -U setuptools \
    && pip install -r requirements.txt

# copy in the source code
COPY --chown=$UNAME:$UNAME . .

EXPOSE 8888
USER $UNAME

# Run gunicorn web server for production
# CMD ["gunicorn", "backend.wsgi", "--bind", "0.0.0.0:8888"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]
