## django 搭建的 web 购物平台

#### 目录结构说明 

    .
    ├── apps
    │   ├── cart  - 购物车模块
    │   ├── goods - 商品模块
    │   ├── order - 订单模块
    │   └── user  - 用户模块
    ├── celery_tasks
    │   └── tasks.py - 异步任务
    ├── dailyfresh
    │   ├── settings.py - 配置文件
    │   ├── urls.py
    │   └── wsgi.py
    ├── db
    │   └── base_model.py - 数据表公有字段
    ├── manage.py - django 管理器
    ├── redis_string.py - redis 使用说明
    ├── static - 静态文件放置文件夹
    └── templates - 模板文件

