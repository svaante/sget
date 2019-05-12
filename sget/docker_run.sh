docker run --it \
    -v host:host \
    -v /usr/lib:/usr/lib \
    -p 3030:3030 \
    --no-deps \
    image \
    bash
