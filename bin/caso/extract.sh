[ ! -f /etc/caso/caso.conf ] && args="--config-file /usr/etc/caso/caso.conf"

sudo caso-extract -d $args
