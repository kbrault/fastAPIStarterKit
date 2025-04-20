# Use Nginx as the base image
FROM nginx:stable-alpine

# Set the working directory inside the container
WORKDIR /usr/share/nginx/html

# Copy all frontend files, including components/
COPY . /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
