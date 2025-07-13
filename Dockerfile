# 使用 Node.js 18 作為基礎映像
FROM node:18-slim

# 設定工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json (如果存在)
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製應用程式程式碼
COPY . .

# 設定環境變數
ENV PORT=8080

# 暴露連接埠
EXPOSE 8080

# 啟動應用程式
CMD [ "npm", "start" ]