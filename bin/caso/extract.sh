[ ! -f /etc/caso/caso.conf ] && args="--config-file /usr/etc/caso/caso.conf"

caso-extract -d $args
