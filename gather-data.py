from pymongo import MongoClient
import requests





def main():
    query_url = 'https://topics.mediacloud.org/api/collections/9139458/stories'
    parameters = {
        'snapshotId': '1477',
        'timespandId': '39849',
        'sort': 'inlink',
        'limit': '5000'
    }
    response = requests.get(query_url, params=parameters)
    stop_here = ""

    client = MongoClient('localhost', 27017)
    database = client['AkashicRecords']
    articles = database['historic_political_article_data']

    article_data_list = []
    for article in articles.find():
        article_element_types = []
        relevance_threshold = 0.65

        for entity in article['entities']:
            if entity['relevance'] > relevance_threshold:
                if 'knowledgeGraph' in entity.keys():
                    if 'typeHierarchy' in entity['knowledgeGraph'].keys():
                        article_element_types.append(entity['knowledgeGraph']['typeHierarchy'].split('/')[1:])

        for keyword in article['keywords']:
            if keyword['relevance'] > relevance_threshold:
                if 'knowledgeGraph' in keyword.keys():
                    if 'typeHierarchy' in keyword['knowledgeGraph'].keys():
                        article_element_types.append(keyword['knowledgeGraph']['typeHierarchy'].split('/')[1:])

        article_data_list.append(article_element_types)

    stop_here = ""


if __name__ == '__main__':
    main()

