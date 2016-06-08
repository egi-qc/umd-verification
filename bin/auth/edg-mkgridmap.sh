#!/bin/bash

cat <<'EOF' >> /tmp/edg-mkgridmap.conf
# DTEAM
# Map VO members (pj)
group vomss://voms.hellasgrid.gr:8443/voms/dteam?/dteam/Role=pilot .dteampj

# Map VO members (root group)
group vomss://voms.hellasgrid.gr:8443/voms/dteam?/dteam .dteam


# OPS
# Map VO members (sgm)
group vomss://voms2.cern.ch:8443/voms/ops?/ops/Role=lcgadmin .opssgm

# Map VO members (pj)
group vomss://voms2.cern.ch:8443/voms/ops?/ops/Role=pilot .opspj

# Map VO members (root group)
group vomss://voms2.cern.ch:8443/voms/ops?/ops .ops
EOF

/usr/sbin/edg-mkgridmap --output=/tmp/dn-grid-mapfile --safe --conf /tmp/edg-mkgridmap.conf
