# crawler_old
垃圾毕设, 模仿ZoomEye
模块较多，很多地方需要手工运行

针对中文网页
爬虫使用Gevent Pool，Redis分布式
cms识别因为时间问题，没用到机器学习，只是简单的根据robots.txt 首页meta等关键字分类，只加入了10左右cms
检索没来得及用ES
内置massscan，可以分布式扫IP 端口，百兆带宽，40多分钟可扫全国4亿IP。

结果：运行2天，共识别了20多万cms， 大约20%的ZoomEye数量，dedecms占ZoomEye的1/3左右， Wordpress占1/5 左右

评价：只运行了2天多，爬虫就爬不动了，下载队列中大部分网站速度异常慢。 
