FROM eclipse-mosquitto:latest

# Declare build arguments
ARG IOT_USERNAME
ARG IOT_PASSWORD

# Create the password file during the build
# The -b flag indicates that the password is provided on the command line
# The -c flag creates the file.
# This command adds a user with the specified username and password.
RUN mosquitto_passwd -b -c /mosquitto/config/mosquitto.passwd $IOT_USERNAME $IOT_PASSWORD

# Change the ownership of the password file to the mosquitto user
RUN chown mosquitto:mosquitto /mosquitto/config/mosquitto.passwd

# The base image has its own ENTRYPOINT to start mosquitto.
# It will automatically load the configuration and the password file.
