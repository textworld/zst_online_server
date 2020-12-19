from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, GeoPoint, Boolean, Long, Float  # 这些都是类型


class SlowQuery(Document):
    finger = Text(fields={'raw': Keyword()})
    host = Text(fields={'raw': Keyword()})
    lock_time = Float()
    query_sql = Text(fields={'raw': Keyword()})
    query_time = Float()
    rows_examined = Long()
    rows_sent = Long()
    user = Text(fields={'raw': Keyword()})
    schema = Text(fields={'raw': Keyword()})

    class Index:
    # 声明使用哪个索引
        name = 'mysql-slowsql-test-*'
