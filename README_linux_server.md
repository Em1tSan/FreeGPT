# Установка проекта и настройка его как сервиса

Переходим в каталог /opt:

```bash
➜  ~ cd /opt 
➜  /opt
```

Клонируем репозиторий:

```bash
git clone https://github.com/Em1tSan/FreeGPT
```

Выдаем права пользователю www-data на репозиторий:

```bash
chown -R www-data:www-data /opt/FreeGPT/
```

Выдаем разрешение на выполнение git pull пользователю www-data:

```bash
➜  /opt visudo


# И добавляем строку
# Allow members of group sudo to execute any command
git ALL=(www-data) /usr/bin/git pull
```

Заходим под пользователем www-data для проверки работы git pull и создания виртуального окружения (venv) и устанавливаем зависимости из requirements.txt:

```bash
# Заходим под пользователем www-data
➜  /opt su www-data -s /bin/bash

# Переходим в проект
$ cd /opt/FreeGPT

# Проверяем что git pull работает
$ git pull
hint: Pulling without specifying how to reconcile divergent branches is
hint: discouraged. You can squelch this message by running one of the following
hint: commands sometime before your next pull:
hint:
hint:   git config pull.rebase false  # merge (the default strategy)
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
Already up to date.

# Создаем виртуальное окружение для проекта
$ python3 -m venv .venv

# Активируем виртуальное окружение
$ source .venv/bin/activate

# Устанавливаем необходимые зависимости в виртуальное окружение:
$ pip install -r requirements.txt

# После установки зависимостей проверяем что проект запускается и работает
$ python3 run.py 
Config file "config.json" is exists and is readable. Loading...
Running on http://127.0.0.1:1338
Running on http://<white.ip>:1338
```

Настройка запуска проекта как сервис systemd:

```bash
# Создаем файл сервиса, вместо vim используйте ваш любимый редактор
vim /etc/systemd/system/chat.service

# Содержимое файла

[Unit]
Description=Web ChatGPT
After=network.target

[Service]
WorkingDirectory=/opt/FreeGPT/
ExecStartPre=/usr/bin/git pull
ExecStartPre=/bin/bash -c 'cd /opt/FreeGPT/ && source .venv/bin/activate && pip install -r requirements.txt'
ExecStart=/bin/bash -c 'cd /opt/FreeGPT/ && source .venv/bin/activate && python3 run.py'
#ExecStart=/opt/FreeGPT/.venv/bin/python3 /opt/FreeGPT/run.py
Restart=always
RestartSec=10s
User=www-data

[Install]
WantedBy=multi-user.target
```

Сохраняем и проверяем:

```bash
# Обновляем данные systemd с внесенными изменениями
➜  ~ systemctl daemon-reload 

# Включаем автозапуск сервиса
➜  ~ systemctl enable chat.service

# Запускаем сервис
➜  ~ systemctl start chat.service

# Проверяем что все запустилось. Если при запуске есть ошибки - скорей всего проблема с правами на файлы
➜  ~ systemctl status chat.service
● chat.service - Web ChatGPT
     Loaded: loaded (/etc/systemd/system/chat.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2023-07-19 14:05:45 MSK; 5min ago
   Main PID: 11878 (python3)
      Tasks: 2 (limit: 2320)
     Memory: 47.6M
        CPU: 1.386s
     CGroup: /system.slice/chat.service
             └─11878 /opt/FreeGPT/.venv/bin/python3 /opt/FreeGPT/run.py

Jul 19 14:05:44  git[11869]: hint:   git config pull.rebase false  # merge (the default strategy)
Jul 19 14:05:44  git[11869]: hint:   git config pull.rebase true   # rebase
Jul 19 14:05:44  git[11869]: hint:   git config pull.ff only       # fast-forward only
Jul 19 14:05:44  git[11869]: hint:
Jul 19 14:05:44  git[11869]: hint: You can replace "git config" with "git config --global" to set a default
Jul 19 14:05:44  git[11869]: hint: preference for all repositories. You can also pass --rebase, --no-rebase,
Jul 19 14:05:44  git[11869]: hint: or --ff-only on the command line to override the configured default per
Jul 19 14:05:44  git[11869]: hint: invocation.
Jul 19 14:05:45  git[11877]: Already up to date.
Jul 19 14:05:45  systemd[1]: Started Web ChatGPT.
```

# Установка и настройка NGINX + Certbot 

Устанавливаем nginx для проксирования сервиса на домен, certbot для получения ssl сертификата, apache2-utils для создания авторизации:

```bash
➜  ~ sudo apt install nginx certbot apache2-utils
```

### Получаем сертификат ssl:

```bash
certbot certonly --standalone -d your.domain.name

Output
IMPORTANT NOTES:
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/your.domain.name/fullchain.pem
Key is saved at: /etc/letsencrypt/live/your.domain.name/privkey.pem
This certificate expires on 2024-05-10.
These files will be updated when the certificate renews.
Certbot has set up a scheduled task to automatically renew this certificate in the background.
```

запоминаем из вывода пути до сертификата и ключа (fullchain.pem и privkey.pem).

### Делаем файл авторизации и добавляем пользователей:

```bash
# Первого пользователя добавляем с ключом -c
➜  ~ htpasswd -c /etc/nginx/.htpasswd user 

# Остальных можно добавлять уже без ключа
➜  ~ htpasswd /etc/nginx/.htpasswd user2
```

### Настройка nginx:

Далее в конфиге заменяйте ***your.domain.name*** на имя вашего домена. Данные настройки используются в случае если FreeGPT будет первым проектом на nginx, в случае если у вас уже что-то крутиться - переходите к следующему шагу

```bash
➜  ~ vim /etc/nginx/sites-enabled/default

# Настройка для редиректа с 80 порта на 443
server {
        listen 80;
        server_name your.domain.name;
        return 301 https://$server_name$request_uri;
        }

# Настройка проксирования сервиса на домен
server {
        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;
        server_name your.domain.name;

        # Прописываем пути до ключей которые запомнили выше
        ssl_certificate /etc/letsencrypt/live/your.domain.name/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your.domain.name/privkey.pem;

        location / {
                auth_basic "Restricted Content";
                auth_basic_user_file /etc/nginx/.htpasswd;

                proxy_pass http://127.0.0.1:1338;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
        }
}
```

Если же у вас на nginx уже запущены проекты которые прописаны в /etc/nginx/sites-enabled/default или вы хотите так же сделать endpoint с доменом (в данном случаем меняем http://127.0.0.1:1338 на http://127.0.0.1:1337):

```bash
➜  ~ cat /etc/nginx/sites-enabled/your.domain.name

server {
    listen 80;
    server_name your.domain.name;
    return 301 https://$server_name$request_uri;
    }
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name your.domain.name;
    
    # Прописываем пути до ключей которые запомнили выше
    ssl_certificate /etc/letsencrypt/live/your.domain.name/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.name/privkey.pem;

    location / {
         proxy_pass http://127.0.0.1:1338;
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Включаем nginx в автозагрузку и запускаем его:

```bash
# Включаем автозапуск
➜  ~ systemctl enable nginx

# Запускаем сервис nginx
➜  ~ systemctl start nginx

# Проверяем что все запустилось без ошибок
➜  ~ systemctl status nginx 
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2023-07-19 16:17:24 MSK; 1s ago
       Docs: man:nginx(8)
    Process: 12739 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 12740 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 12741 (nginx)
      Tasks: 3 (limit: 2320)
     Memory: 5.4M
        CPU: 84ms
     CGroup: /system.slice/nginx.service
             ├─12741 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─12742 nginx: worker process
             └─12743 nginx: worker process

Jul 19 16:17:24   systemd[1]: Starting A high performance web server and a reverse proxy server...
Jul 19 16:17:24   systemd[1]: Started A high performance web server and a reverse proxy server.
```

Если ошибок нет и все настройки выполнены правильно \- можно проверить доступность сайта через браузер.

Закрываем порты для внешки:

```bash
➜  ~ sudo apt-get install iptables-persistent

# iptables для Chat
➜  ~ sudo iptables -A INPUT -p tcp -s localhost --dport 1338 -j ACCEPT
➜  ~ sudo iptables -A INPUT -p udp -s localhost --dport 1338 -j ACCEPT
➜  ~ sudo iptables -A INPUT -p tcp --dport 1338 -j DROP
➜  ~ sudo iptables -A INPUT -p udp --dport 1338 -j DROP

# iptables для Endpoint
➜  ~ sudo iptables -A INPUT -p tcp -s localhost --dport 1337 -j ACCEPT
➜  ~ sudo iptables -A INPUT -p udp -s localhost --dport 1337 -j ACCEPT
➜  ~ sudo iptables -A INPUT -p tcp --dport 1337 -j DROP
➜  ~ sudo iptables -A INPUT -p udp --dport 1337 -j DROP

➜  ~ netfilter-persistent save
➜  ~ netfilter-persistent reload
```

Автообновление сертификата certbot и проекта:

```bash
# Открываем crontab для редактирования
➜  ~ crontab -e

# Автообновление сертификатов для домена
0 0 1 * * certbot renew --quiet

# Авторестарт сервиса проекта, при этом с гита подтягиваются обновления и переподключаются прокси.
*/30 * * * * systemctl restart chat.service > /dev/null 2>&1
```
