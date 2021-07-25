from elasticsearch_dsl import Document, Keyword, Text, Long, Float # 这些都是类型

class SlowQuery(Document):
    finger = Text(fields={'raw': Keyword()})
    query_timestamp = Long()
    lock_time_sec = Float()
    login_user = Text(fields={'raw': Keyword()})
    query_time_sec = Float()
    rows_examined = Long()
    rows_sent = Long()
    schema = Text(fields={'raw': Keyword()})
    slowsql = Text(fields={'raw': Keyword()})
    sql_id = Text(fields={'raw': Keyword()})

    class Index:
    # 声明使用哪个索引
        name = 'mysql_slow_log'


