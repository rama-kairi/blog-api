# Pull base image
FROM python:3.9

# Set working directory
WORKDIR /blog/

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y libpq-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev


# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./prestart.sh .

COPY . /blog/

# run entrypoint.sh
# ENTRYPOINT ["/blog/prestart.sh"]

# EXPOSE 8000
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]