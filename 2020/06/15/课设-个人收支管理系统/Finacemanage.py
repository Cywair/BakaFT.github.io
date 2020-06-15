import csv
import os
from prettytable import PrettyTable

'''
出于输入友好性和容错处理，日期输入方式改为这种格式
精确到日20191211
精确到月201912
'''
# 初始化一个字典，用于多个方法
summarization_dicts = [
    {"sort":"a1", "type":"收入","name":"股票收入", "amount":0},
    {"sort":"a2", "type":"收入","name":"工资", "amount":0},
    {"sort":"a3", "type":"收入","name":"奖金", "amount":0},
    {"sort":"b1", "type":"支出","name":"股票亏损", "amount":0},
    {"sort":"b2", "type":"支出","name":"生活花费", "amount":0},
    {"sort":"b3", "type":"支出","name":"医疗支出", "amount":0},
]


class Account(): # 定义一个Account类，实现多用户功能

    def __init__(self,name): # 初始化时绑定name属性
        self.name = name

    def createFile(self): # 该方法用于创建本地csv文件储存账单，包含了一个简单的 if-else 判断
        if os.path.exists(self.name + '.csv'):
            print('你的账单已存在于本地,正在登陆')
        else:
            print('似乎你是第一次使用,正在为你创建本地帐单')
            open(self.name+'.csv','w')

    def addTransaction(self,sort,date,amount,remark): # 该方法用于为当前用户添加一条记录
        '''
        :param sort: 类型编码
        :param date: 日期
        :param amount: 数额
        :param remark: 备注
        '''

        # 进行简单的参数合法性检查
        sorts = ['a1', 'a2', 'a3', 'b1', 'b2', 'b3']
        if sort in sorts:
            pass
        else:
            print('检查类型编码是否输入有误')
        if len(date) == 8:
            pass
        else:
            print('检查日期格式是否符合要求')

        # 通过一个 if-else 结构判断是否已经存在文件，若存在则使用追加模式，避免覆盖写入第一行
        if os.path.exists(self.name+'.csv'):
            with open(self.name + '.csv', 'a') as file:
                file.write(f"{sort},{date},{amount},{remark}\n")
        else:
            with open(self.name+'.csv','w') as file:
                file.write(f"{sort},{date},{amount},{remark}\n")

    def printSummarization(self): # 该方法用于打印指定查询月份的收支信息
        month = (input('输入要查询月份(如202004):\n'))
        print(f'\n{month[:4]}年{month[-2:]}月收支类别数据的汇总')
        # 首先整理数据
        '''
        读取CSV文件的每一行，判断月份是否相符和，然后将本行的数值累加到字典中对应的项
        '''
        with open(self.name+'.csv','r') as file:
            file_reader = csv.reader(file)
            for row in file_reader:
                if row[1][:6] == month:
                    amount = int(row[2])
                    sort = row[0]
                    for each in summarization_dicts:
                        if each['sort'] == sort:
                            each['amount'] = each['amount'] + amount
                else:
                    pass
        # 然后使用PrettyTable打印数据
        tb_summarization = PrettyTable()
        tb_summarization.field_names = ['收入/支出', '明细类别', '金额']
        # 把每个类型的数据一行一行加入PrettyTable对象
        for each in summarization_dicts:
            type = each['type']
            name = each['name']
            amount = each['amount']
            tb_summarization.add_row([type, name, amount])
        print(tb_summarization)
        # 还有一个总收支
        asum, bsum = 0, 0
        for each in summarization_dicts:
            if each['sort'][0] == 'a':
                asum = asum + each['amount']
            else:
                bsum = bsum + each['amount']
        # 重置一下字典里的amount,防止下次打印数据出错
        for each in summarization_dicts:
            each['amount'] = 0
        print(f'{month[:4]}年{month[-2:]}月的总收入为{asum},总支出为{bsum}\n')
        # 下面选择是否打印明细
        choice = input('是否输出该月各笔交易明细(y/n)\n')

        def printAllTransaction(): # 该函数用于将每一条交易格式化地添加到PrettyTable实例对象并打印
            tb_alltransaction = PrettyTable() # 初始化实例
            tb_alltransaction.field_names = ['类别', '收入/支出', '发生日期', '金额', '备注'] # 添加表头
            '''
            判断每条的月份值是否相符，如果符合,那么处理并转化这条交易的属性，并添加为tb_alltransaction的一行
            '''
            with open(self.name + '.csv', 'r') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    if row[1][:6] == month:
                        sort = row[0]
                        date = row[1]
                        type = ''
                        amount = row[2]
                        remark = row[3]
                        for each in summarization_dicts:
                            if sort == each['sort']:
                                sort = each['name']
                                type = each['type']
                        tb_alltransaction.add_row([sort, type, date, amount, remark])
                # 设置按照类别升序排序打印
                tb_alltransaction.sort_key("类别")
                tb_alltransaction.reversesort = True
                # 打印表格
                print(tb_alltransaction)
        # 是否选择打印明细
        if choice == 'n':
            pass
        else:
            printAllTransaction()
        menu()
        selectfunc()

    def diyFunc(self):
        '''
        该方法为作业中自定功能，大交易额记录查询
        显示所有单次交易量大于某特定值的记录，并统计数量,显示其占用户总交易量的比例
        '''
        print('''
        根据给定的一个数值，查询并显示所有单次交易数额大于等于给定值的交易记录。
        程序会统计符合条件的记录数量，并显示其占用户交易记录的次数比例
        ''')
        threshold = input('请输入一个给定阈值:\n')
        # 初始化一个计数变量
        count = 0
        # 初始化PrettyTable实例
        tb_threshold = PrettyTable()
        tb_threshold.field_names = ['类别', '收入/支出', '发生日期', '金额', '备注']
        '''
        迭代查询每条交易，如果交易金额大于阈值，则添加到表格中
        '''
        with open(self.name + '.csv', 'r') as file:
            lines = len(file.readlines()) # CSV文件的行数就是交易总次数
            file.seek(0) # 将读取文件的指针移动到文件最开头，因为readlines方法会把指针放到文件最后，导致后面的reader读不出东西
            file_reader = csv.reader(file)
            for row in file_reader:
                if row[2] >= threshold:
                    sort = row[0]
                    date = row[1]
                    type = ''
                    amount = row[2]
                    remark = row[3]
                    for each in summarization_dicts:
                        if sort == each['sort']:
                            sort = each['name']
                            type = each['type']
                    tb_threshold.add_row([sort, type, date, amount, remark])
                    count += 1
        print('\n符合条件的交易次数占总交易次数的比例: {:.2%}'.format(count / lines))
        print(tb_threshold)


def menu(): # 首次进入要求输入用户名并初始化实例再打印菜单，执行完函数操作后再进入只打印菜单
    global name #声明全局变量
    if name != '':
        print(f'欢迎,{name}')
    else:
        name = input('欢迎使用,请先输入用户名以确认身份,如果不存在将自动注册:\n')
        user = Account(name)
        user.createFile() # 调用createFile方法，保证账单文件存在
        print(f'欢迎,{name}')
    print(tb_menu)


def selectfunc(): # 使用这个函数实现输入数字选择功能
    order = (input('输入需要执行功能的对应序号:\n'))
    if order == '1':
        menu_1()
    elif order == '2':
        menu_2()
    elif order == '3':
        menu_3()
    elif order == '4':
        menu_4()
    elif order == '5':
        exit()
    else:
        print('输入有误,请直接输入阿拉伯数字序号')
        selectfunc()


def menu_1(): # 切换用户名的函数实现
    global name
    name = input('请输入要切换到的用户名:\n')
    if name != '':
        # Windows下文件名不允许包含  ?、\/*"'<>|
        #name = name.replace('/', '／').replace('*', '[星号]').replace('?', '[问号]').replace(':', '[冒号]').replace('"', '双引号').replace('<', '[左尖括号]').replace('>', '[右尖括号]').replace('|', '[竖杠]')
        user = Account(name)
        user.createFile()
        menu()
        selectfunc()
    else:
        print('不允许空用户名')


def menu_2(): # 为当前用户添加记录的函数实现
    user = Account(name)
    while True: # 通过一个while True:循环来实现不断添加，并在循环体中加入了适合的break条件
        print('''
        输入格式: a1,20200126,2000.0,备注
        类型编码:
            收入: a1-股票收入 a2-工资 a3-奖金
            支出: b1-股票支出 b2-生活花费 b3-医疗支出
        ''')
        input_str = input('按照指定格式输入,不输入直接敲回车表示结束\n')
        if input_str  == '':  # 方便跳出循环
            break
        elif input_str.count(',') != 3: # 判断输入的字符串中英文逗号的数量来判定参数数量, 防止用户输入类似'a1'的内容后报错
            print('请检查输入的参数数量是否为4个')
        else:
            input_str_list = input_str.split(',')
            if len(input_str_list) == 4:
                sort, date, amount, remark = input_str_list
                user.addTransaction(sort, date, amount, remark) # 调用实例的addTransaction方法添加记录
                print('添加记录成功')
            else:
                print('输入参数有误,请检查逗号中英文和参数数量是否正确')
    menu()
    selectfunc()


def menu_3(): #打印指定月份的收支概况
    user = Account(name) # 初始化实例以调用下面的方法
    user.printSummarization()
    menu()
    selectfunc()


def menu_4(): #大额交易查询功能
    user = Account(name)
    user.diyFunc()
    menu()
    selectfunc()


# 定义当前的用户名
name = ''

# 利用PrettyTable打印菜单，此处为菜单配置
tb_menu = PrettyTable()  # 实例化一个PrettyTable表格对象
tb_menu.field_names = ['序号', '功能'] # 表头
tb_menu.add_row([1, '更换账户'])
tb_menu.add_row([2, '输入数据'])
tb_menu.add_row([3, '数据汇总'])
tb_menu.add_row([4, '大额交易统计'])
tb_menu.add_row([5, '退出'])
# 程序入口
menu()
selectfunc()