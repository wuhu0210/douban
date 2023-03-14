import csv
import re
import urllib.error  
import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
# 设置绘图中文显示和模板
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')

# 设置正则表达式用于提取信息
findlink = r'<a href="(.*?)">'
findimgSrc = r'<img.*src="(.*?)"'
findtitle = r'<span class="title">(.*)</span>'
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findJudge = r'<span class="rating_num" property="v:average">(.*)</span>'
findInq = r'<span class="inq">(.*)</span>'
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 获取网页html文本信息
def askURL(url):
    head = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / "
                      "83.0.4103.61 Safari / 537.36 "
    }
    html = ""
    request = urllib.request.Request(url, headers=head)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# 利用BeautifulSoup库进行html文本有用数据的提取
def fillData(baseURL):
    dataList = []
    for i in range(0, 10):
        # print(i)
        url = baseURL + str(i * 25)
        html = askURL(url)
        # print(url)
        soup = BeautifulSoup(html, "html.parser")
        # print(soup.find_all("div",class_="item"))

        for item in soup.find_all("div", class_="item"):
            data = []
            item = str(item)
            link = re.findall(findlink, item)[0]
            # print(link)
            data.append(link)
            imgSrc = re.findall(findimgSrc, item)[0]
            # print(imgSrc)
            data.append(imgSrc)
            titles = re.findall(findtitle, item)
            if len(titles) >= 2:
                ctitle = titles[0]
                data.append(ctitle)
                # print(ctitle)
                otitle = titles[1].replace("/", "")
                data.append(otitle)
                # print(otitle)
            else:
                data.append(titles[0])
                data.append(" ")

            judgeNum = re.findall(findJudge, item)[0]
            # print(judgeNum)
            data.append(judgeNum)

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。", "")
                data.append(inq)
            else:
                data.append(" ")
            # print(inq)
            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)
            bd = re.sub('/', " ", bd)
            data.append(bd.strip())
            dataList.append(data)
            # print(data)i
    return dataList


# 保存提取到的数据到本地
def saveData(data):
    with open('douban.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['link', 'img_link', 'name', 'origin_name', 'score', 'score1', 'short_sentence', 'content'])
        writer.writerows(data)
    f.close()


# 加工清洗数据
def processData():
    data = pd.read_csv("douban.csv")
    col_1 = data[["link", "img_link", "name", "origin_name", "score", "short_sentence", "content"]]  # 获取一列，用一维数据
    data_1 = np.array(col_1)

    for i in range(250):  # 去掉空格
        data_1[i][3] = data_1[i][3].lstrip()
        # print(data_1[i][3])
        s = data_1[i][6]
        data_1[i][6] = re.sub('...', '', s, 1)

    f = open('douban.csv', 'w', newline='', encoding='utf-8-sig')
    writer = csv.writer(f)
    writer.writerow(["link", "img_link", "name", "origin_name", "score", "short_sentence", "content"])
    for i in data_1:
        writer.writerow(i)
    f.close()
    print("数据存储完成")


# 从数据中提取有用统计信息
def getInfor():
    data = pd.read_csv("douban.csv")
    col_1 = data[["link", "img_link", "name", "origin_name", "score", "short_sentence", "content"]]  # 获取一列，用一维数据
    data_1 = np.array(col_1)

    data_chara = np.zeros(7)
    data_score = np.zeros(5)
    data_type = np.zeros(16)
    data_year = np.zeros(6)

    for i in range(250):
        if data_1[i][6].count('美国'):
            data_chara[0] = data_chara[0] + 1
        if data_1[i][6].count('中国'):
            data_chara[1] = data_chara[1] + 1
        if data_1[i][6].count('香港'):
            data_chara[2] = data_chara[2] + 1
        if data_1[i][6].count('大陆'):
            data_chara[3] = data_chara[3] + 1
        if data_1[i][6].count('法国') or data_1[i][6].count('意大利') or data_1[i][6].count('英国') \
                or data_1[i][6].count('德国') or data_1[i][6].count('西班牙') or data_1[i][6].count('瑞典') \
                or data_1[i][6].count('丹麦'):
            data_chara[4] = data_chara[4] + 1
        if data_1[i][6].count('印度') or data_1[i][6].count('日本') or data_1[i][6].count('韩国') \
                or data_1[i][6].count('伊朗'):
            data_chara[5] = data_chara[5] + 1
        if not (data_1[i][6].count('美国') or data_1[i][6].count('中国') or data_1[i][6].count('法国') \
                or data_1[i][6].count('意大利') or data_1[i][6].count('英国') or data_1[i][6].count('德国') \
                or data_1[i][6].count('西班牙') or data_1[i][6].count('瑞典') or data_1[i][6].count('丹麦') \
                or data_1[i][6].count('印度') or data_1[i][6].count('日本') or data_1[i][6].count('韩国') \
                or data_1[i][6].count('伊朗')):
            data_chara[6] = data_chara[6] + 1

    for i in range(250):
        if 9.5 < data_1[i][4]:
            data_score[0] = data_score[0] + 1
        if 9.5 >= data_1[i][4] >= 9.3:
            data_score[1] = data_score[1] + 1
        if 9.2 >= data_1[i][4] >= 9.0:
            data_score[2] = data_score[2] + 1
        if 8.9 >= data_1[i][4] >= 8.7:
            data_score[3] = data_score[3] + 1
        if 8.7 > data_1[i][4]:
            data_score[4] = data_score[4] + 1

    for i in range(250):
        if data_1[i][6].count('剧情'):
            data_type[0] = data_type[0] + 1
        if data_1[i][6].count('喜剧'):
            data_type[1] = data_type[1] + 1
        if data_1[i][6].count('动作'):
            data_type[2] = data_type[2] + 1
        if data_1[i][6].count('爱情'):
            data_type[3] = data_type[3] + 1
        if data_1[i][6].count('科幻'):
            data_type[4] = data_type[4] + 1
        if data_1[i][6].count('动画'):
            data_type[5] = data_type[5] + 1
        if data_1[i][6].count('悬疑'):
            data_type[6] = data_type[6] + 1
        if data_1[i][6].count('惊悚'):
            data_type[7] = data_type[7] + 1
        if data_1[i][6].count('恐怖'):
            data_type[8] = data_type[8] + 1
        if data_1[i][6].count('犯罪'):
            data_type[9] = data_type[9] + 1
        if data_1[i][6].count('音乐') or data_1[i][6].count('歌舞'):
            data_type[10] = data_type[10] + 1
        if data_1[i][6].count('历史') or data_1[i][6].count('传记'):
            data_type[11] = data_type[11] + 1
        if data_1[i][6].count('战争'):
            data_type[12] = data_type[12] + 1
        if data_1[i][6].count('冒险'):
            data_type[13] = data_type[13] + 1
        if data_1[i][6].count('灾难'):
            data_type[14] = data_type[14] + 1
        if data_1[i][6].count('武侠'):
            data_type[15] = data_type[15] + 1

    for i in range(250):
        if int(re.findall("\d+", data_1[i][6])[0]) >= 2010:
            data_year[0] = data_year[0] + 1
        if 2009 >= int(re.findall("\d+", data_1[i][6])[0]) >= 2000:
            data_year[1] = data_year[1] + 1
        if 1999 >= int(re.findall("\d+", data_1[i][6])[0]) >= 1990:
            data_year[2] = data_year[2] + 1
        if 1989 >= int(re.findall("\d+", data_1[i][6])[0]) >= 1980:
            data_year[3] = data_year[3] + 1
        if 1979 >= int(re.findall("\d+", data_1[i][6])[0]) >= 1950:
            data_year[4] = data_year[4] + 1
        if 1950 > int(re.findall("\d+", data_1[i][6])[0]):
            data_year[5] = data_year[5] + 1

    f = open('douban_info.csv', 'w', newline='', encoding='utf-8-sig')
    writer = csv.writer(f)
    writer.writerow(["美国", "中国", "中国香港", "中国大陆", "欧洲", "亚洲其他", "其他"])
    writer.writerow(data_chara)
    writer.writerow(["9.5+分", "9.3-9.5分", "9.0-9.2分", "8.7-8.9分", "8.7-分"])
    writer.writerow(data_score)
    writer.writerow(["剧情", "喜剧", "动作", "爱情", "科幻", "动画", "悬疑", "惊悚", "恐怖",
                     "犯罪", "音乐", "历史", "战争", "冒险", "灾难", "武侠"])
    writer.writerow(data_type)
    writer.writerow(["2010+", "2000-2009", "1990-1999", "1980-1989", "1950-1979", "1950-"])
    writer.writerow(data_year)
    f.close()
    print("数据特征提取完成")


# 数据可视化
def showInfor():
    with open('douban_info.csv', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        info = [row for row in reader]

    plt.ion()  # 打开交互模式

    plt.figure(1, figsize=(12, 5))
    Num = 312
    data_country = info[1]
    labels = ['美国', '中国香港', '中国大陆', '欧洲', '亚洲其他', '其他国家']
    colors = ['red', 'orange', 'yellow', 'green', 'purple', 'blue']
    sizes = [float(data_country[0]) / Num * 100, float(data_country[2]) / Num * 100,
             float(data_country[3]) / Num * 100, float(data_country[4]) / Num * 100,
             float(data_country[5]) / Num * 100, float(data_country[6]) / Num * 100]
    expodes = (0.05, 0.05, 0.05, 0.05, 0.05, 0.05)
    plt.pie(sizes, autopct='%1.1f%%', explode=expodes, labels=labels, shadow=True, colors=colors)
    plt.legend(loc=(1, 0.8))
    plt.axis('equal')
    plt.title('国家分布图')
    plt.savefig('country.png')

    plt.figure(2, figsize=(12, 5))
    Num = 250
    data_score = info[3]
    labels = info[2]
    colors = ['red', 'orange', 'yellow', 'blue', 'purple']
    sizes = [float(data_score[0]) / Num * 100, float(data_score[1]) / Num * 100,
             float(data_score[2]) / Num * 100, float(data_score[3]) / Num * 100,
             float(data_score[4]) / Num * 100]
    expodes = (0.05, 0.05, 0.05, 0.05, 0.05)
    plt.pie(sizes, autopct='%1.1f%%', explode=expodes, labels=labels, shadow=True, colors=colors)
    plt.legend(loc=(1, 0.8))
    plt.axis('equal')
    plt.title('得分分布图')
    plt.savefig('score.png')

    plt.figure(3, figsize=(12, 6))
    rng = np.random.RandomState(0)
    x = info[4]
    y = np.zeros(16)
    for i in range(16):
        y[i] = float(info[5][i])
    colors = rng.rand(16)
    colors = ['navy', 'darkred', 'gainsboro', 'goldenrod', 'crimson', 'lawngreen',
              'deepskyblue', 'darkviolet', 'sandybrown', 'indigo', 'silver', 'lightcoral',
              'teal', 'lemonchiffon', 'sienna', 'maroon']
    sizes = 60 * y
    plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
    plt.colorbar()
    plt.xlabel('题材', fontsize=15, fontweight='bold')
    plt.ylabel('数量', fontsize=15, fontweight='bold')
    plt.title('题材分布图')
    plt.savefig('type.png')

    plt.figure(4, figsize=(8, 6))
    x = ['2010+', '2000-2009', '1990-1999', '1980-1989', '1950-1979', '1950-']
    y = np.zeros(6)
    for i in range(6):
        y[i] = float(info[7][i])
    for i in range(len(x)):
        plt.bar(x[i], y[i])
    plt.title('上映时间')
    plt.xlabel('时间段', fontweight='bold')
    plt.ylabel('数量', fontweight='bold')
    for a, b in zip(x, y):
        plt.text(a, b, '%.0f' % b, ha='center', va='bottom', fontsize=11)
    plt.savefig('year.png')

    plt.ioff()
    plt.show()


# 主函数实现所有功能
def main():
    print("start")
    baseURL = "https://movie.douban.com/top250?start="
    dataList = fillData(baseURL)
    # print(dataList)
    print('数据总长度：', len(dataList))
    saveData(dataList)
    processData()
    getInfor()
    showInfor()


if __name__ == "__main__":
    main()
    print("爬取完成")
