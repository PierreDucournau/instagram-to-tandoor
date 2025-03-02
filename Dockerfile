FROM python:3.13-slim

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    firefox-esr \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*


# Install Firefox WebDriver

# Comment / Uncomment the following line (for ARM architecture)
# RUN wget -q -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz \
#     && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
#     && rm /tmp/geckodriver.tar.gz \
#     && chmod +x /usr/local/bin/geckodriver

# Comment / Uncomment the following lines (for x86 architecture)
RUN wget -q -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && rm /tmp/geckodriver.tar.gz \
    && chmod +x /usr/local/bin/geckodriver

# Insall dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# dont change the browser
ENV BROWSER=docker
ENV FLASK_APP=app.py

EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]