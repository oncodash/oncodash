FROM python:3.7-alpine

# ERROR logs are sent to terminal
ENV PYTHONUNBUFFERED=1

# no __pycache__ written by container root in the bindmount
# Would end up in permission errors when building 
ENV PYTHONDONTWRITEBYTECODE=1 

# Add non-privliged user that will be used when running the container
ARG UNAME=djangouser
RUN adduser -D $UNAME

# Copy in source code and set up rights 
RUN mkdir /opt/app/ && chown $UNAME:$UNAME /opt/app/
WORKDIR /opt/app
COPY --chown=$UNAME:$UNAME ./requirements.txt ./requirements.txt
ENV PATH /home/$UNAME/.local/bin:$PATH
RUN pip install -r requirements.txt
COPY --chown=$UNAME:$UNAME . .
EXPOSE 8888

USER $UNAME
# RUN python manage.py collectstatic

# Run gunicorn web server
CMD ["gunicorn", "core.wsgi", "--bind", "0.0.0.0:8888"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]