# Start from a stable Debian version (bullseye)
FROM debian:bullseye



# Install system dependencies required by R packages
RUN apt-get update && apt-get install -y \
    libudunits2-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('sf', 'dplyr', 'data.table', 'raster'), repos='https://cloud.r-project.org/')"

# Set the working directory
WORKDIR /home/rstudio

# Set the default command to run R when the container starts
CMD ["R"]
