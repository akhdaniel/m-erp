docker compose ps -q | xargs -I {} sh -c 'echo "" > $(docker inspect --format="{{.LogPath}}" {})'
