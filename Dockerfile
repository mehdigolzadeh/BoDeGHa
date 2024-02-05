FROM bitnami/python:3.8.8

# Move in server folder
WORKDIR /bodegha

# Copy requirements.txt and install all dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files in server directory
COPY . .

# Run BotHunter.py
ENTRYPOINT [ "python",  "bodegha.py"]
CMD ["--help"]
