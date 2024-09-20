# Use the Debian-specific R base image
FROM r-base:latest

# Update package lists and install necessary tools
RUN apt-get update && apt-get install -y \
    gnupg \
    dirmngr \
    apt-transport-https \
    ca-certificates \
    software-properties-common

# Add the CRAN repository to sources list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && echo "deb https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list

# Install system dependencies for sf and raster
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    libudunits2-dev \
    libgeos-dev \
    libproj-dev

# Install R packages
RUN R -e "install.packages(c('sf', 'dplyr', 'data.table', 'raster'), repos='https://cloud.r-project.org/')"

# Set the working directory
WORKDIR /root

# Start R when the container launches
CMD ["R"]
