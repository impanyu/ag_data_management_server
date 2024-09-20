# Use rocker/rstudio as the base image
FROM rocker/rstudio:latest

# Install system dependencies for sf and raster
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libudunits2-dev \
    libgeos-dev \
    libproj-dev

# Install R packages
RUN R -e "install.packages(c('sf', 'dplyr', 'data.table', 'raster'), repos='https://cran.rstudio.com/')"

# Set the working directory
WORKDIR /home/rstudio

# The CMD is already set in the rocker/rstudio base image, so we don't need to specify it again
