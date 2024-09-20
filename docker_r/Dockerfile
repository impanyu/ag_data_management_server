# Use the R base image
FROM r-base:latest

# Install system dependencies for sf and raster
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libudunits2-dev \
    libgeos-dev \
    libproj-dev

# Install R packages
RUN R -e "install.packages(c('sf', 'dplyr', 'data.table', 'raster'), repos='https://cran.rstudio.com/')"

# Set the working directory
WORKDIR /root

# Start R when the container launches
CMD ["R"]
