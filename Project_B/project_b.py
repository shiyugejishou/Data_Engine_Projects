import pandas as pd
from efficient_apriori import apriori
import time

raw_data = pd.read_csv('./订单表.csv', encoding='GBK')
raw_products = pd.read_csv('./产品表.csv', encoding='GBK')


def data_process(raw_data):
    start_time = time.time()
    # 生成字典，客户与其购买的产品
    order_dict =raw_data.groupby('客户ID')['产品ID'].apply(list).to_dict()
    # 产品ID和产品型号生成字典
    products = raw_products.groupby('产品ID')['产品型号'].apply(list).to_dict()
    # print(order_dict.values())
    temp = []
    # 将产品ID与其对应的产品型号拼接并放入临时表,提高结果可读性
    for items in order_dict.values():
        temp_id = []
        for item in items:
            id_pro = str(item) + '-' + str(products[item]).replace("['", "").replace("']", "").strip()
            temp_id.append(id_pro)
        temp.append(temp_id)
    # 使用Apriori算法得出频繁项集和关联规则
    item_sets, rules = apriori(temp, min_support=0.02, min_confidence=0.4)
    end_time = time.time()
    cost_time = end_time - start_time
    print("频繁项集：", item_sets)
    print("关联规则：", rules)
    print("计算耗时%.2f 秒" % cost_time)


if __name__ == '__main__':
    data_process(raw_data)
