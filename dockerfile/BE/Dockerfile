# 1. Base image
FROM openjdk:17-jdk-slim

# 2. Add JAR file
ARG JAR_FILE=build/libs/ctc.jar
COPY ${JAR_FILE} app.jar

# 4. Run the application
ENTRYPOINT ["java", "-jar", "/app.jar"]