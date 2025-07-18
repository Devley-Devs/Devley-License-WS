FROM oven/bun:latest

WORKDIR /app

COPY package.json .

RUN bun install

COPY . .

CMD ["bun", "run", "index.ts"]
