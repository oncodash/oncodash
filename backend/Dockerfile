FROM python:3.7-alpine

# ERROR logs are sent to terminal
ENV PYTHONUNBUFFERED=1

# no __pycache__ written by container root in the bindmount
# Would end up in permission errors when building 
ENV PYTHONDONTWRITEBYTECODE=1 

# Simple set up as root
WORKDIR /opt/app
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . .
EXPOSE 8000

# Add and set user called user inside the container file system
RUN adduser -D user
USER user

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]