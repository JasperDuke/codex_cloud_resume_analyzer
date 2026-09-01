FROM node:20-bookworm-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
COPY server.js db.py ./
COPY public ./public

ENV NODE_ENV=production \
    PORT=10000 \
    DATABASE_PATH=/var/data/resume-analyzer.db

EXPOSE 10000

CMD ["node", "server.js"]
