FROM python:3.11-slim

# instalacion mod_wsgi y apache
RUN apt-get update && apt-get install -y apache2 libapache2-mod-wsgi-py3

# dependencias
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copiar carpeta al contenedor
COPY . /app

# configuracion personalizada de apache al directorio correspondiente
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

# habilitar mod_wsgi y reiniciar Apache
RUN a2enmod wsgi
RUN service apache2 restart

# exponer el puerto 80
EXPOSE 80

# comando para iniciar Apache
CMD ["apachectl", "-D", "FOREGROUND"]
