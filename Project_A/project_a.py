import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from pandas import DataFrame
import time

base_url = 'http://car.bitauto.com'


def get_max_page():
    """

    :return: max_page 结果最大页数
    """
    # 组装第一页结果
    page_url = base_url+'/xuanchegongju/?l=8&mid=8&page={}'.format(1)
    # 使用fake_useragent 随机伪造User-Agent
    ua = UserAgent()
    my_headers = {'User-Agent': ua.random}
    try:
        re = requests.get(page_url, headers=my_headers)
        if re.status_code == 200:
            soup = BeautifulSoup(re.text, 'lxml')
            max_page = soup.find(class_='pagenation-box ssr-box').attrs['data-pages']
            # print(max_page)
            return int(max_page)
        else:
            print('页面请求失败，错误代码：%s' % re.status_code)
    except requests.ConnectionError as e:
        # 输出连接错误
        print('连接错误，错误信息：%s' % e.args)


def get_page(page):
    """

    :param page: 当前爬取页码
    :return: page_df 当前页结果的DF
    """
    # 根据页码组装URL
    page_url = base_url+'/xuanchegongju/?l=8&mid=8&page={}'.format(page)
    print(page_url)
    # 使用fake_useragent 随机伪造User-Agent
    ua = UserAgent()
    my_headers = {'User-Agent': ua.random}
    try:
        # 发送Request并获得response
        re = requests.get(page_url, headers=my_headers)
        # 当返回状态正常时
        if re.status_code == 200:
            # 使用BeautifulSoup和lxml进行解析
            soup = BeautifulSoup(re.text, 'lxml')
            # 从HTML中找到结果列表
            car_lists = soup.find(class_='search-result-list')
            page_df = DataFrame()
            # 循环获取DIV中的结果信息
            for item in car_lists.find_all(class_='search-result-list-item'):
                car_name = item.find(class_='cx-name text-hover').text
                car_image = item.find(class_='img').attrs['src']
                price_range = item.find(class_='cx-price').text
                model_list = item.find(class_='cx-ck-count text-hover').attrs['data-list']
                model_url = item.find('a').attrs['href']
                # 获取车型款式详情及指导价
                car_model = get_model(model_url, model_list)
                # 通过"-"符号拆分最高价和最低价
                mark = '-'
                if mark in price_range:
                    low_price = price_range.split('-')[0] + '万'
                    high_price = price_range.split('-')[1]
                else:
                    low_price = price_range
                    high_price = price_range
                car_info = {
                    '名称': car_name,
                    '图片链接': car_image,
                    '价格范围': price_range,
                    '最低价格': low_price,
                    '最高价格': high_price,
                    '车型清单': car_model
                }
                # 将每一车型信息字典转为DF并加入页面DF
                car_info_df = DataFrame([car_info])
                page_df = page_df.append(car_info_df, ignore_index=True)
            return page_df
        else:
            print('页面请求失败，错误代码：%s' % re.status_code)
    except requests.ConnectionError as e:
        # 输出连接错误
        print('连接错误，错误信息：%s' % e.args)


def get_model(model_url, model_list):
    """

    :param model_url: 车型url
    :param model_list: 款式编号代码
    :return: car_model 车型款式及指导价list
    """
    model_url = base_url+model_url
    model_num = model_list.split(',')
    car_model = []
    for num in model_num:
        # 拼接车型款式详情页URL
        url = model_url+'m'+num
        print('通过URL%s 获取车型款式信息' % url)
        # 解析
        model_re = requests.get(url)
        model_soup = BeautifulSoup(model_re.text, 'lxml')
        model_title = model_soup.find_all(class_='ck-name-item')
        guide_price = model_soup.find(class_='guide-price')
        # 判断处理暂无指导价的车型
        if guide_price:
            car_model.append(model_title[0].text+model_title[1].text+'  指导价：'+guide_price.text.replace("\n", '').strip())
        else:
            car_model.append(model_title[0].text + model_title[1].text + '  暂无报价')
    return car_model


if __name__ == '__main__':
    print('准备开始爬取……')
    start_time = time.time()
    # 获取结果最大页数
    max_page = get_max_page()
    # 建立结果DataFrame
    results_df = DataFrame(columns=['名称', '图片链接', '价格范围', '最低价格', '最高价格'])
    # 循环爬取全部结果页并加入结果DF
    for page in range(1, max_page+1):
        print('当前爬取页数：%s'% page)
        page_df = get_page(page)
        results_df = results_df.append(page_df, ignore_index=True)
    # 导出结果CSV文件
    results_df.to_csv('./spider_result.csv', header=True, index=False, encoding='utf_8_sig')
    end_time = time.time()
    cost_time = float(end_time-start_time)
    print('爬取完成，共耗时%.2f秒' % cost_time)
