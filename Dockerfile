FROM python:3.7-stretch
LABEL MAINTAINER=0xbug
ENV TZ=Asia/Shanghai
EXPOSE 80
RUN apt-get update
RUN apt-get install --no-install-recommends -y vim net-tools curl gnupg git redis-server supervisor software-properties-common wget
RUN curl https://openresty.org/package/pubkey.gpg | apt-key add -
RUN add-apt-repository -y "deb http://openresty.org/package/debian stretch openresty"
RUN apt-get update
RUN apt-get install -y openresty
COPY ./deploy /socialdb_vue_flask/deploy
RUN pip install --upgrade pip setuptools==45.2.0
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /socialdb_vue_flask/deploy/pyenv/requirements.txt -U
RUN cp /socialdb_vue_flask/deploy/nginx/*.conf /usr/local/openresty/nginx/conf/
RUN cp /socialdb_vue_flask/deploy/supervisor/*.conf /etc/supervisor/conf.d/
COPY ./client/dist /socialdb_vue_flask/client/dist
COPY server /socialdb_vue_flask/server
WORKDIR /socialdb_vue_flask/server
COPY ./docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh
CMD ["./docker-entrypoint.sh"]
