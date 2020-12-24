from src.utils.MasonTimeUtils import get_utc_datetime_from_iso8601_string
from src.dataStructures.ElasticsearchUtils import ElasticsearchUtils


def get_elasticsearch_nearest_query(lat=0, lon=0, start_datetime="2020-10-10T10:00:00Z",
                                    end_datetime="2020-10-10T11:00:00Z"):
    dt_lower_bound = get_utc_datetime_from_iso8601_string(start_datetime)
    dt_upper_bound = get_utc_datetime_from_iso8601_string(end_datetime)

    query = {
        "bool":
            {
                "must":
                    {"range":
                        {
                            "valid_at": {"gt": dt_lower_bound, "lt": dt_upper_bound}
                        },
                    },
                "should":
                    {
                        "distance_feature": {"field": "location", "origin": {"lat": lat, "lon": lon}, "pivot": "100m"}
                    }

            }
    }
    return query


def get_query_for_all_measures_within_geohash(geohash_value, start_datetime="2020-10-10T10:00:00Z",
                                              end_datetime="2020-10-10T11:00:00Z"):
    dt_lower_bound = get_utc_datetime_from_iso8601_string(start_datetime)
    dt_upper_bound = get_utc_datetime_from_iso8601_string(end_datetime)
    query = {
        "bool":
            {
                "must":
                    [
                        {
                            "geo_bounding_box": {
                                "location": {
                                    "top_left": geohash_value,
                                    "bottom_right": geohash_value
                                }
                            }

                        },
                        {"range":
                            {
                                "valid_at": {"gt": dt_lower_bound, "lt": dt_upper_bound}
                            }
                        }

                    ]
            }

    }
    return query


def execute_query(query, indexes, _from, _to, class_to_use):
    a = class_to_use.search(index=indexes).query(query)[
        _from:_to].execute()
    # .filter("geo_distance", distance='20km', location={'lat': lat, 'lon': lon}) \
    # .execute()
    observations = list(map(lambda p: class_to_use(**p.to_dict()).get_rep(), a))
    return observations


def get_initial_final_indexes_from_query_parameters(query_parameters):
    if ElasticsearchUtils.QueryKeyWords.PAGE in query_parameters:
        page = int(query_parameters[ElasticsearchUtils.QueryKeyWords.PAGE])
    else:
        page = 0
    if ElasticsearchUtils.QueryKeyWords.ITEMS in query_parameters:
        items = min(int(query_parameters[ElasticsearchUtils.QueryKeyWords.ITEMS]), 1000)
    else:
        items = 1000
    _from = page * items
    _to = (page + 1) * items
    return _from, _to
