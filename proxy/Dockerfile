FROM node:18-alpine
WORKDIR /app

# Install production deps
COPY package.json package-lock.json* ./
RUN npm ci --only=production

COPY . .
EXPOSE 3000
CMD [ "npm", "start" ]
