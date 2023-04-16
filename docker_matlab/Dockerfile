FROM mathworks/matlab:r2023a

USER root
# Create a custom directory for the license file
RUN mkdir -p /opt/matlab-licenses

# Copy your license file into the container
COPY license.lic /opt/matlab-licenses/license.lic

# Set the environment variable to point to the license file
ENV MLM_LICENSE_FILE /opt/matlab-licenses/license.lic
