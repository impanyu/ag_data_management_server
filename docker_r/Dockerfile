# Use the Debian-specific R base image
FROM r-base:latest

# Update package lists and install system dependencies
RUN apt-get update && apt-get install -y \
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
