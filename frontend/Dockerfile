FROM node:24-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm prune --production

FROM node:24-alpine
WORKDIR /app
COPY package*.json ./

COPY . .

ENV NODE_ENV=production

EXPOSE 80
CMD ["/usr/local/bin/pm2-runtime", "start", "server.js", "-i", "0"]
