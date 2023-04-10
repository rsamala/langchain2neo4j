# Use an official Node.js image as the base
FROM node:19-alpine

# Set the working directory
WORKDIR /app

# Serve the built files using a lightweight HTTP server
RUN npm install -g serve

# Copy the package.json and package-lock.json files to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the production version of the React app
RUN npm run build

# Expose the port on which the app will run
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build"]