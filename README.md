[![Build Status](https://travis-ci.org/mayaculpa/veleda.svg?branch=master)](https://travis-ci.org/mayaculpa/veleda)

# Veleda

A data analytics platform for hydroponic setups. It visualizes and allows analysis of data covering the growth aspects of hydroponics. In combination with the [HAPI project][1], it creates a system that covers the data collection and automation to data storage and analysis.

## Requirements

### Required

- **Docker:** available for [Ubuntu][2], [Mac](3), [Windows][4] and other [Linux flavors][5]. Note that currently only Ubuntu is supported.
- **Secrets:** Secrets have to be provided for the grafana, influxdb, postgres and web services. Templates are provided and *should* be modified

### Optional

- **SMTP server:** To enable user registration, credentials to an SMTP server are required. For testing purposes, the admin account may be used.

## Starting the Services

Start the complete setup with:

    ./start.sh

Stop the setup with:

    docker-compose down

List the individual services with `docker ps`. Key data to the individual services:

| Name     | Purpose              | Port | Documentation |
| -------- | -------------------- | ---- |---------------|
| nginx    | Landing page         | 80   | N/A  |
| web      | User management      | 8001 | [readme](web/README.md) |
| grafana  | Time series analysis | 3000 | [readme](grafana/README.md) |
| postgres | User storage         | 5431 | N/A |
| influxdb | Time series storage  | 8086 | N/A |
| redis    | Async task storage   | 6379 | N/A |

The data is stored in volumes. List all active volumes with `docker volume ls`. To access Grafana, visit [localhost:3000](localhost:3000) after starting the services. The admin login credentials are defined in `web/secrets.flask`.

[1]: https://github.com/mayaculpa/hapi
[2]: https://docs.docker.com/install/linux/docker-ce/ubuntu/
[3]: https://docs.docker.com/docker-for-mac/install/
[4]: https://docs.docker.com/docker-for-windows/install/
[5]: https://docs.docker.com/install/
