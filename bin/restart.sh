git -C /opt/m-erp pull
docker compose restart $1
if [[ "$1" == "" || "$1" == "ui-service" ]]; then
  docker restart nginx_proxy
fi

