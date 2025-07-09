# 统一API接口规范

## 概述

本文档定义了股票信息查询系统的统一API接口规范，旨在为Web界面、命令行工具和其他客户端提供一致的数据访问接口。

## API基础信息

- **基础URL**: `/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证机制

当前版本API无需认证，但未来可能引入API密钥机制以限制访问频率。

## 错误处理

所有API错误响应遵循统一格式：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息"
  }
}
```

## 接口列表

### 1. 获取实时行情

#### 请求
- **URL**: `GET /quotes/realtime`
- **参数**:
  - `symbol` (string, required): 股票代码，例如 "600900"
  
#### 响应
```json
{
  "data": {
    "卖五价": 23.45,
    "卖五量": 1000,
    "买五价": 23.40,
    "买五量": 800,
    "最新": 23.42,
    "涨幅": 1.25,
    "涨跌": 0.29,
    // ... 其他字段
  }
}
```

### 2. 获取历史数据

#### 请求
- **URL**: `GET /quotes/history`
- **参数**:
  - `symbol` (string, required): 股票代码
  - `period` (string, optional): 时间周期，可选值: "daily", "weekly", "monthly", "1", "5", "15", "30", "60"，默认为"daily"
  - `start_date` (string, optional): 开始日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
  - `end_date` (string, optional): 结束日期，格式 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:MM:SS"
  - `adjust` (string, optional): 复权类型，可选值: "", "qfq" (前复权), "hfq" (后复权)

#### 响应
```json
{
  "data": [
    {
      "时间": "2023-07-10",
      "开盘": 23.10,
      "收盘": 23.42,
      "最高": 23.50,
      "最低": 23.05,
      "成交量": 1000000,
      "成交额": 23450000,
      // ... 其他字段（根据period不同可能有所不同）
    }
  ]
}
```

### 3. 获取技术指标

#### 请求
- **URL**: `GET /analysis/indicators`
- **参数**:
  - `symbol` (string, required): 股票代码
  - `period` (string, optional): 时间周期，可选值: "daily", "weekly", "monthly"，默认为"daily"

#### 响应
```json
{
  "data": [
    {
      "指标名称": "EMA5",
      "值": "23.35",
      "操作": "买入"
    },
    {
      "指标名称": "RSI",
      "值": "65.20",
      "操作": "中立"
    },
    // ... 其他指标
  ]
}
```

### 4. 获取板块行情

#### 请求
- **URL**: `GET /boards`
- **参数**: 无

#### 响应
```json
{
  "data": [
    {
      "排名": 1,
      "板块名称": "新能源",
      "板块代码": "BK001",
      "最新价": 1234.56,
      "涨跌幅": 2.35,
      // ... 其他字段
    }
  ]
}
```

### 5. 获取热门股票排名

#### 请求
- **URL**: `GET /stocks/hot`
- **参数**: 无

#### 响应
```json
{
  "data": [
    {
      "当前排名": 1,
      "代码": "600900",
      "股票名称": "长江电力",
      "最新价": 23.42,
      "涨跌幅": 1.25
    }
  ]
}
```

### 6. 获取股票基本信息

#### 请求
- **URL**: `GET /stocks/info`
- **参数**:
  - `symbol` (string, required): 股票代码

#### 响应
```json
{
  "data": [
    {
      "item": "股票代码",
      "value": "600900"
    },
    {
      "item": "股票简称",
      "value": "长江电力"
    },
    // ... 其他信息
  ]
}
```

## 响应格式

所有成功的API响应都遵循以下格式：

```json
{
  "data": {...},  // 具体的数据内容
  "timestamp": "2023-07-10T10:00:00Z"  // 响应时间戳
}
```

对于列表类型的数据，`data`字段为数组；对于单个对象的数据，`data`字段为对象。

## 分页

对于可能返回大量数据的接口（如历史数据），将支持分页参数：

- `page` (integer, optional): 页码，默认为1
- `page_size` (integer, optional): 每页条数，默认为50，最大100

分页响应格式：
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 1000
  }
}
```

## 版本控制

API版本通过URL路径控制，当前版本为v1。未来版本将在路径中体现，如`/api/v2/`。