# RESTful API 设计指南

## 概述

REST（Representational State Transfer）是一种软件架构风格，用于设计网络应用。RESTful API 遵循 REST 原则，提供了一组标准化的接口设计方法。

## 核心原则

RESTful API 设计遵循以下核心原则：

* **无状态性**：每个请求都包含所有必要的信息
* **统一接口**：使用标准化的接口设计
* **可缓存**：响应应该明确标识是否可缓存
* **分层系统**：客户端不需要知道是否连接到最终服务器

## HTTP 方法

RESTful API 使用标准的 HTTP 方法来执行操作：

| 方法 | 描述 | 示例 |
| --- | --- | --- |
| GET | 获取资源 | GET /users |
| POST | 创建资源 | POST /users |
| PUT | 更新资源（完整） | PUT /users/1 |
| PATCH | 更新资源（部分） | PATCH /users/1 |
| DELETE | 删除资源 | DELETE /users/1 |

## 状态码

API 应该返回适当的 HTTP 状态码：

| 状态码 | 含义 | 使用场景 |
| --- | --- | --- |
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权 |
| 403 | Forbidden | 禁止访问 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

## API 设计示例

以下是一个用户管理 API 的设计示例：

### 获取用户列表

```
GET /api/users
Host: example.com
Accept: application/json
```

### 创建用户

```
POST /api/users
Host: example.com
Content-Type: application/json

{
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25
}
```

### 更新用户

```
PATCH /api/users/1
Host: example.com
Content-Type: application/json

{
    "age": 26
}
```

### 删除用户

```
DELETE /api/users/1
Host: example.com
```

## 响应格式

API 响应应该使用统一的 JSON 格式：

### 成功响应

```
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "张三",
        "email": "zhangsan@example.com"
    }
}
```

### 错误响应

```
{
    "code": 400,
    "message": "参数错误",
    "errors": [
        {
            "field": "email",
            "message": "邮箱格式不正确"
        }
    ]
}
```

## 最佳实践

* 使用名词而不是动词来命名资源
* 使用复数形式表示资源集合
* 使用嵌套资源表示关系
* 提供分页、排序、过滤功能
* 实现版本控制
* 提供 API 文档

## 总结

RESTful API 设计需要遵循一系列原则和最佳实践。通过合理的设计，可以创建出易于使用、可维护的 API 接口。