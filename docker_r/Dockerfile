# Start from the official R image
FROM r-base:latest

# Install system dependencies required by R packages
# - libudunits2-dev: Required for 'sf'
# - libgdal-dev, libgeos-dev, libproj-dev: Required for 'sf' to work with spatial data
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
