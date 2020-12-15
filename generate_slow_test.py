import random
import datetime


def randomtimes(start, end, n, frmt="%Y-%m-%d"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    return [random.random() * (etime - stime) + stime for _ in range(n)]

randomtimes('2018-06-01','2018-11-01',10)

if __name__ == '__main__':
    fields = ['a', 'b', 'c', 'd', 'e']
    tables = ['T_bill', 'T_user', 'T_money', 'T_computer']
    sql_list = []

    for i in range(20000):
        table_idx = random.randint(0, len(tables) - 1)
        field_num = random.randint(1, len(tables))
        where_list = []
        for j in range(field_num):
            where_list.append(random.choice(["and", "or"]))
            where_list.append("{} {} {}".format(
                random.choice(fields),
                random.choice(["like", "="]),
                "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', random.randint(1, 10)))))
        sql = "select * from {} where {};".format(tables[table_idx], " ".join(where_list[1:]))
        data = {
            "query": sql,
            ""
        }
