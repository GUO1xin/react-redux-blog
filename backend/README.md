# 后端服务（Flask + MySQL）

为 react-redux-blog 提供自建 API，替换掉官方演示服务器 `https://conduit.productionready.io/api`。接口协议与前端 `src/agent.js` 保持一致（RealWorld / Conduit API spec），所以前端业务代码不需要改动，只切了 `API_ROOT`。

## 1. 建库

在本机 MySQL 里执行：

```sql
CREATE DATABASE react_redux_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. 配置环境变量

```bash
cd backend
cp .env.example .env
```

按你本机 MySQL 的账号密码修改 `.env`。

## 3. 安装依赖 & 建表

```bash
pip install -r requirements.txt
flask --app app init-db
```

## 4. 启动服务

```bash
flask --app app run
```

默认监听 `http://localhost:5000`，所有接口挂在 `/api` 前缀下（`/api/users`、`/api/articles` 等）。

## 跨域说明

- 开发环境：前端 `package.json` 里配置了 `"proxy": "http://localhost:5000"`，`npm start` 时 CRA 开发服务器会自动把 `/api/*` 转发到这里，浏览器侧不存在跨域请求。
- 生产 / 前后端分离部署：后端额外用 `Flask-CORS` 允许了 `.env` 里 `CORS_ORIGIN` 配置的来源，避免真实跨域场景下被浏览器拦截。

## 数据模型

`users` / `articles` / `comments` / `tags`，外加 `article_tags`（文章-标签多对多）、`favorites`（用户收藏文章多对多）、`follows`（用户关注用户，自关联多对多）。

## 分页

`GET /api/articles` 支持 `limit`、`offset`、`tag`、`author`、`favorited` 查询参数，用 SQL `LIMIT/OFFSET` 分页并单独 `COUNT(*)` 返回 `articlesCount`，不会一次性把全表拉到内存再切片。
