from datetime import datetime
import enums


def generate_history_pipeline(region_id, store_id, quality_val, year_val, unit_id, week_from, week_to):
    week_num = datetime.today().isocalendar()[1]
    pipeline = [{
                    '$match': {
                        'week': {
                            '$gte': week_num - 4
                        },
                        'year': year_val
                    }
                } if week_from is None and week_to is None else {
        '$match': {
            'week': {
                '$gte': week_from,
                '$lte': week_to
            },
            'year': year_val
        }
    }]
    if region_id is not None:
        pipeline.append(
            {
                '$match': {
                    'region': enums.region_dict[region_id].value,
                }
            })

    if store_id is not None:
        pipeline.append(
            {
                '$match': {
                    'point_type': enums.point_dict[store_id].value,
                }
            })

    if quality_val is not None:
        pipeline.append(
            {
                '$match': {
                    'quality': enums.quality_dict[quality_val]
                }
            })

    if unit_id is not None:
        pipeline.append(
            {
                '$match': {
                    'unit':  enums.unit_metric_dict[unit_id]
                }
            })


    return pipeline
