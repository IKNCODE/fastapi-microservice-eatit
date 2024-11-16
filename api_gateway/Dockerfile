# Используем centos образ OpenResty (т.к. в alpine версии не поддерживается luarocks)
FROM openresty/openresty:centos

# Устанавливаем необходимые зависимости для работы с luarocks


# Устанавливаем lua-resty-jwt через luarocks
RUN /usr/local/openresty/luajit/bin/luarocks install lua-resty-jwt

COPY lua-resty-jwt /etc/nginx

# Копируем файл конфигурации NGINX
COPY nginx.conf /nginx.conf

# Открываем порт 80 для сервера NGINX
EXPOSE 80

# Старт сервера NGINX
CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]