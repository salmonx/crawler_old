# crawler_old
本科毕设, 模仿Shodan，对比ZoomEye

针对中文网页
爬虫使用Gevent Pool，Redis分布式
cms识别因为时间问题，没用到机器学习，根据robots.txt首页meta等关键字分类
内置massscan，可以分布式扫IP 端口，百兆带宽，40多分钟可扫全国4亿IP。

运行2天，共识别了20多万cms，约20%的ZoomEye数量，dedecms 30% Wordpress 20%
