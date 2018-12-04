# Django B2C电商项目
## 用户模块
* 注册、登录
  > 采用Django自带的认证系统,继承了AbstractUser类，本身就包含了cookie、session操作
  >> 基本方法使用`authenticate() login() logout() login_required()`
  >Redis实现对session的缓存，
  >邮件采用Django内置的send_mail()函数，采用celery实现异步请求。
  >历史浏览记录使用Redis的list作为记录
## 商品模块
* 采用MySQL数据库
* haystack+whoosh实现对商品的检索
* Nginx+fastdfs实现对图片的存储
## 订单模块
* 生成订单
 > 使用MySQL事务，对一组sql操作进行提交或者撤销
 > 使用悲观锁处理订单并发效果
* 支付订单
  >调用支付宝的支付接口。
## 购物车模块
  >使用Redis对购物车商品进行记录缓存
