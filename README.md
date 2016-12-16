# EPM web

## Install

```bash
sudo apt install python3-pip
sudo pip3 install flask flask-api flask-markdown sqlalchemy toml siphash
```

Nginx reverse proxy config:

```nginx
location / {
    proxy_pass http://127.0.0.1:5000$request_uri;
    proxy_set_header Host $Host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Scheme $scheme;
}
```


## Usage

```bash
./epmweb.py
```
