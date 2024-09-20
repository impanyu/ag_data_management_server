# Use the Debian-specific R base image
FROM r-base:latest

# Update GPG keys and package lists
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -qO- https://ftp-master.debian.org/keys/archive-key-11.asc | apt-key add - && \
    wget -qO- https://ftp-master.debian.org/keys/archive-key-11-security.asc | apt-key add - && \
    apt-get update

# Install system dependencies
RUN apt-get install -y \
    libgdal-dev \
    libudunits2-dev \
    libgeos-dev \
    libproj-dev

# Install R packages
RUN R -e "install.packages(c('sf', 'dplyr', 'data.table', 'raster'), repos='https://cloud.r-project.org/', dependencies=TRUE)"

# Set the working directory
WORKDIR /root

# Start R when the container launches
CMD ["R"]
