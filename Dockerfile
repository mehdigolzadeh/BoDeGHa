FROM bitnami/python:3.9.13

# Move in server folder
WORKDIR /bodegha

# Copy requirements.txt and install all dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files in server directory
COPY . .

# Run bodegha.py
ENTRYPOINT [ "python",  "bodegha.py"]
CMD ["--help"]
