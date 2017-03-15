#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import logging
from gevent.pool import Pool
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ip_proxy_urls = {
	'kxdaili' : 'http://www.kxdaili.com/dailiip/1/1.html',
	'mimvp' : 'http://proxy.mimvp.com/free.php?proxy=in_hp',
	'xici' : 'http://www.xicidaili.com/nn/',
	'ip181' : 'http://www.ip181.com/',
	'httpdaili' : 'http://www.httpdaili.com/mfdl/',
	'66ip' : 'http://www.66ip.cn/nmtq.php?isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip&getnum='
}

probe_url = 'http://1212.ip138.com/ic.asp'

class IPSpider(object):
	
	headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }

	def __init__(self):
		self.proxyes = []

	def get_html(self,url):
		request = urllib2.Request(url)
		request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
		html = urllib2.urlopen(request)
		return html.read()


	def get_bs(self,url):
		soup = BeautifulSoup(self.get_html(url), "lxml")
		return soup


	def img2port(self,img_url):
		code = img_url.split("=")[-1]
		if code.find("AO0OO0O")>0:
			return 80
		else:
			return None


	def fetch_all(self):
		logger.info('Ready for fetch ip proxy')
		count = 0

		self.fetch_kxdaili()
		logger.info('fetch %s ip from kxdaili...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		self.fetch_xici()
		logger.info('fetch %s ip from xici...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		self.fetch_mimvp()
		logger.info('fetch %s ip from mimvp...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		self.fetch_ip181()
		logger.info('fetch %s ip from ip181...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		self.fetch_httpdaili()
		logger.info('fetch %s ip from httpdaili...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		self.fetch_66ip()
		logger.info('fetch %s ip from 66ip...' % (int(len(self.proxyes)) - count))
		count = len(self.proxyes)

		logger.info('Finish fetching! There are %s ips!' % count)

		return self.proxyes
		
	def fetch_kxdaili(self):
		try:
			url = ip_proxy_urls['kxdaili']
			soup = self.get_bs(url)
			table_tag = soup.find("table", attrs={"class": "segment"})
			trs = table_tag.tbody.find_all("tr")
			for tr in trs:
				tds = tr.find_all("td")
		    	ip = tds[0].text
		    	port = tds[1].text
		    	proxy_type = tds[3].text.split(',')[0].lower()
		    	latency = tds[4].text.split(" ")[0]
		    	if float(latency) < 0.5: # 输出延迟小于0.5秒的代理
		        	proxy = {proxy_type : "%s:%s" % (ip, port)}
		        	self.proxyes.append(proxy)
		except Exception as e:
			logger.warning('fail to fetch from kxdaili. reason is %s' % e)


	def fetch_xici(self,page = 2):
		try:
			base_url = ip_proxy_urls['xici']
			for num in xrange(1,page + 1):
				url = base_url + str(num)
				soup = self.get_bs(url)
				table = soup.find("table", attrs={"id": "ip_list"})
				trs = table.find_all("tr")
				for i in range(1, len(trs)):
					tr = trs[i]
					tds = tr.find_all("td")
					ip = tds[1].text
					port = tds[2].text
					proxy_type = tds[5].text.lower()
					speed = tds[6].div["title"][:-1]
					latency = tds[7].div["title"][:-1]
					if float(speed) < 3 and float(latency) < 1:
						proxy = {proxy_type : "%s:%s" % (ip, port)}
						self.proxyes.append(proxy)
		except Exception as e:
			logger.warning("fail to fetch from xici. reason is %s" % e)


	def fetch_mimvp(self):
		try:
			url = ip_proxy_urls['mimvp']
			soup = self.get_bs(url)
			table = soup.find("div", attrs={"id": "list"}).table
			tds = table.tbody.find_all("td")
			for i in range(0, len(tds), 10):
				ip = tds[i+1].text
				port = self.img2port(tds[i+2].img["src"])
				proxy_type = tds[i+3].text.split('/')[0].lower()
				response_time = tds[i+7]["title"][:-1]
			if port is not None and float(response_time) < 1 :
			    proxy = {proxy_type : "%s:%s" % (ip, port)}
			    self.proxyes.append(proxy)
		except Exception as e:
			logger.warning("fail to fetch from mimvp.reason is %s" % e)


	def fetch_ip181(self): 
		try:
			url = ip_proxy_urls['ip181']
			soup = self.get_bs(url)
			table = soup.find("table")
			trs = table.find_all("tr")
			for i in range(1, len(trs)):
				tds = trs[i].find_all("td")
				ip = tds[0].text
				port = tds[1].text
				proxy_type = tds[3].text.split(',')[0].lower()
				latency = tds[4].text[:-2]
				if float(latency) < 1:
					proxy = {proxy_type : "%s:%s" % (ip, port)}
					self.proxyes.append(proxy)
		except Exception as e:
			logger.warning("fail to fetch from ip181: %s" % e)


	def fetch_httpdaili(self):
		try:
			url = ip_proxy_urls['httpdaili']
			soup = self.get_bs(url)
			table = soup.find('div',attrs = {'kb-item-wrap11'}).table
			trs = table.find_all('tr')
			for i in range(1, len(trs)):
				try:
					tds = trs[i].find_all('td')
					ip = tds[0].text
					port = tds[1].text
					is_anonymous = tds[2].text
					if is_anonymous == u'匿名':
						proxy = {'http' : "%s:%s" % (ip, port)}
						self.proxyes.append(proxy)
				except :
					pass	
		except Exception as e:
			logger.warning("fail to fetch from httpdaili. reason is %s" % e)
	

	def fetch_66ip(self,num = 20):
		try:
        	# 修改getnum大小可以一次获取不同数量的代理
			base_url = ip_proxy_urls['66ip']
			url = base_url + str(num)
			soup = self.get_bs(url)
			if soup.title.text.encode('utf-8') == '安小莫提示：匿名提取成功':
				for ip in  soup.body.text.split('$')[0].split('\r\n\t\t'):
					ip = ip.replace('/n','').replace('/r','').replace('/t','').strip()
					proxy = {'http' : ip}
					self.proxyes.append(proxy)
		except Exception as e:
			logger.warning("fail to fetch from httpdaili. reason is %s" % e)




class ActiveIPManager(object):
	
	def __init__(self):
		self.spider = IPSpider()
		self.active_IP_pool = []
		

	def probe_proxy_ip(self,proxy_ip):
		proxy = urllib2.ProxyHandler(proxy_ip)
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
		try:
			html = urllib2.urlopen(probe_url, timeout = 2)
			if html:
				soup = BeautifulSoup(html, "lxml")
				print soup.body.center.text.encode('utf-8')
				self.active_IP_pool.append(proxy_ip)
				return True
			else:
				print '%s probe fail !' % proxy_ip
				return False
		except Exception as e:
			print '%s probe fail! reason is %s' %(proxy_ip, e)
			return False

		
    

if __name__ == '__main__':

	import sys
	root_logger = logging.getLogger("")
	stream_handler = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
	stream_handler.setFormatter(formatter)
	root_logger.addHandler(stream_handler)
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	active_pool = ActiveIPManager()

	ip_list = active_pool.spider.fetch_all()
	
	pool = Pool(20)
	pool.map(active_pool.probe_proxy_ip, ip_list)

	print active_pool.active_IP_pool
						