# EOVSA Flarelist Webpage Deployment Guide

This guide details the process for deploying the EOVSA Flarelist webpage, accessible via [https://www.ovsa.njit.edu/flarelist](https://www.ovsa.njit.edu/flarelist). It covers essential steps such as configuring Apache, setting up environment variables, and securing the site with SSL/TLS. The deployment is performed under the user account 'sjyu' on the OVSA server.

## 1. Apache Configuration

Start by setting up the Apache configuration file to define how the web server handles requests to your site.

### Edit the Apache Configuration

Location: `/etc/apache2/sites-available/000-default.conf`

```apache
<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        ServerName ovsa.njit.edu
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        # Proxy requests for static files to the Flask application
        ProxyPass /flarelist/static http://localhost:8000/flarelist/static
        ProxyPassReverse /flarelist/static http://localhost:8000/flarelist/static

        # Proxy other requests to the backend server
        ProxyPass /flarelist http://localhost:8000/
        ProxyPassReverse /flarelist http://localhost:8000/

        <Location /flarelist/>
            Require all granted
            ProxyPreserveHost On
        </Location>

        ProxyPass /lwa/ http://localhost:5001/
        ProxyPassReverse /lwa/ http://localhost:5001/

        <Location /lwa/>
            Require all granted
            ProxyPreserveHost On
        </Location>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>
```

### Reload Apache

After setting up the Apache configuration, reload the service to apply changes:

```bash
sudo service apache2 reload
sudo service apache2 restart
```

## 2. Setting Environment Variables

Environment variables are used to securely store application configuration, such as database credentials.

### Edit the `.bashrc` File

Add the following lines to `/home/sjyu/.bashrc` to set up environment variables for the database and Flask application:

```bash
export FLARE_DB_HOST='localhost'
export FLARE_DB_DATABASE='EOVSA_flare_list_wiki_db'
export FLARE_LC_DB_DATABASE='EOVSA_lightcurve_QL_db'
export FLARE_DB_USER='root'
export FLARE_DB_PASSWORD='C@l1b4Me'
export FLARE_FLASK_SECRET_KEY='4d77c9688990c55d3f6d0e3c95f01cd1'
```

### Note: the Secure `FLARE_FLASK_SECRET_KEY` is generated using python:
```python
import secrets
key_bytes = secrets.token_bytes(16)
print(key_bytes.hex())
```

## 3. SSL/TLS Setup for ovsa.njit.edu

Securing your site with SSL/TLS is critical for protecting your users' data.

### Obtain an SSL Certificate with Let's Encrypt

Let's Encrypt provides free SSL certificates. Use Certbot to automate the certificate installation:

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-apache
sudo certbot --apache -d ovsa.njit.edu -d www.ovsa.njit.edu
```

### Reload Apache to Apply SSL Configuration

```bash
sudo systemctl reload apache2
```

> **Note**: Ensure to renew the Let's Encrypt certificate before it expires, typically every 90 days.

## 4. Launching the Web Application with Gunicorn

### Use Screen for Persistent Sessions

First, check if a `flarelist` screen session exists:

```bash
screen -ls
```

If it exists, reattach to it:

```bash
screen -rd flarelist
```

If not, create a new session named `flarelist`:

```bash
screen -S flarelist
```

### Start the Flask Application

Navigate to the Flask application directory and start Gunicorn:

```bash
cd /var/www/html/flarelist
gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
```