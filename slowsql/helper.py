
def build_aggs(agg):
    for k in agg.keys():
        if k != "aggs":
            options = agg.get(k)
            return A(k, **options)


def get_aggs(agg, d):
    if 'aggs' not in d.keys():
        return

    aggs = d.get('aggs')
    if len(aggs.keys()) > 1:
        for metric_name in aggs.keys():
            agg = agg.metric(metric_name, build_aggs(aggs.get(metric_name)))
    elif len(aggs.keys()) == 1:
        k = list(aggs.keys())[0]
        agg = agg.bucket(k, build_aggs(aggs.get(k)))
        get_aggs(agg, aggs.get(k))


def get_results(agg_query, result):
    if 'aggs' not in agg_query.keys():
        return {}

    aggs = agg_query.get('aggs')
    if len(aggs.keys()) == 1:
        key_name = list(aggs.keys())[0]
        bucket_results = []
        for bucket in result[key_name]['buckets']:
            doc_count = 0
            key_val = ''
            if 'key_as_string' in bucket:
                key_val = bucket.key_as_string
            elif 'key' in bucket:
                key_val = bucket.key
            else:
                raise Exception('no key found in bucket')
            if 'doc_count' in bucket:
                doc_count = bucket.doc_count
            ret = get_results(aggs[key_name], bucket)
            if isinstance(ret, list):
                for r in ret:
                    r[key_name + "_count"] = doc_count
                    r[key_name] = key_val
                bucket_results.extend(ret)
            elif isinstance(ret, dict):
                ret[key_name] = key_val
                ret[key_name + "_count"] = doc_count
                bucket_results.append(ret)
        return bucket_results
    else:
        ret = {}
        for key_name in aggs.keys():
            if 'value' in result[key_name]:
                val = result[key_name]['value']
                ret[key_name] = val
            elif list(aggs[key_name].keys())[0] == 'top_hits':
                print(result[key_name])
                hits = result[key_name]['hits']['hits']
                if len(hits) > 0:
                    for source_field in hits[0]['_source']:
                        ret[source_field] = hits[0]['_source'][source_field]

        return ret