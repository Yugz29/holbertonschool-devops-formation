FROM node:20-alpine

ENV NODE_ENV=production
WORKDIR /usr/src/app

RUN addgroup -S app && adduser -S -G app app

COPY package*.json ./
RUN npm install --omit=dev && npm cache clean --force
COPY server.js ./

USER app
EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
