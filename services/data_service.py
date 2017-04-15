import ujson as json


from watson_developer_cloud import AlchemyDataNewsV1, AlchemyLanguageV1, ToneAnalyzerV3, WatsonException
import datetime
from pymongo import MongoClient, InsertOne, DeleteOne, ReplaceOne
import re
import requests









class DataService(object):
    base_url = 'https://watson-api-explorer.mybluemix.net/alchemy-api/calls/data/GetNews'
    second_base_url = 'https://watson-api-explorer.mybluemix.net/alchemy-api/calls/data/GetNews?apikey=edd60853a78c2a0e33859cfff509999b2012ca19'
    database_name = 'AkashicRecords'


    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[self.database_name]
        self.news_source_article_data = self.database['news_source_article_data']
        self.historic_political_article_data = self.database['historic_political_article_data']
        self.akashic_news_sources = self.database['AkashicNewsSources']


    # Refresh Database with Sources

    def refresh_and_return_news_sources(self):
        unique_id_set = self.get_unique_ids_from_collection(self.akashic_news_sources)
        news_sources_request = requests.get('https://newsapi.org/v1/sources?language=en')
        news_sources_raw = news_sources_request.json()['sources']
        new_news_sources = []
        for news_source in news_sources_raw:
            del news_source['id']
            news_source['_id'] = str(id(news_source))
            if news_source['_id'] not in unique_id_set:
                self.akashic_news_sources.insert(news_source)
                new_news_sources.append(news_source)
        return new_news_sources


    def pull_articles_from_source(self, source_url, params=None):
        url = self.clean_news_source_url(source_url)
        articles_data = self.get_source_articles_data(source_url=url, params=params)
        return articles_data




    def get_tone_of_text_non_api(self, text_data):
        api_url = 'https://tone-analyzer-demo.mybluemix.net/api/tone'
        params = {
            'text': text_data
        }
        result = requests.post(api_url, data=params)
        tone_data = result.json()
        return tone_data


    def get_article_text_non_api(self, article_url):
        api_url = 'https://alchemy-language-demo.mybluemix.net/api/text'
        params = {
            'url': article_url
        }
        result = requests.post(api_url, data=params)
        return result.json()['text']


    def get_source_articles_data(self, source_url, params=None):
        json_data = {}
        try:
            cleaned_url = source_url.replace('.com', '')
            json_data = self.request_source_articles(cleaned_url, params)
        except Exception as e:
            print(e.args)
        return json_data


    def clean_source_articles(self, source_id, source_articles):
        progress = 0
        cleaned_articles = []
        for source_article in source_articles['docs']:
            try:
                source_article_data = source_article['source']['enriched']['url']
                source_article_data['_id'] = str(hash(source_article_data['url']))
                full_text = self.get_article_text_non_api(source_article_data['url'])
                source_article_data['full_text'] = full_text
                source_article_data['source'] = source_id
                source_article_data['tone_data'] = self.get_tone_of_text_non_api(full_text)
                cleaned_articles.append(source_article_data)
                progress += 1
                print('Progress: ' + str(progress))
            except Exception as e:
                print(e.args)
        return cleaned_articles


    def get_articles_for_source(self, source_url, source_id, params=None):
        try:
            url = self.clean_news_source_url(source_url)
            source_articles_data = self.get_source_articles_data(source_url=url, params=params)
            progress = 0
            for source_article in source_articles_data['result']['docs']:
                try:
                    source_article_data = source_article['source']['enriched']['url']
                    source_article_data['_id'] = str(hash(source_article_data['url']))
                    full_text = self.get_article_text_non_api(source_article_data['url'])
                    source_article_data['full_text'] = full_text
                    source_article_data['source'] = source_id
                    source_article_data['tone_data'] = self.get_tone_of_text_non_api(full_text)
                    self.news_source_article_data.insert_one(source_article_data)
                    progress += 1
                    print('Progress: ' + str(progress))
                except Exception as e:
                    print(e.args)
        except Exception as a:
            print(a.args)



    def request_source_articles(self, source_url, params=None, results_next=None):
        return_fields = 'enriched.url.cleanedTitle,enriched.url.relations,enriched.url.entities.entity.quotations,' \
                        'enriched.url.keywords,enriched.url.url,enriched.url.author,enriched.url.publicationDate,' \
                        'enriched.url.text,enriched.url.entities,enriched.url.concepts,enriched.url.taxonomy,' \
                        'enriched.url.entities,enriched.url.docSentiment'

        if params is None:
            params = {}

        request_params = {
            'apikey': 'edd60853a78c2a0e33859cfff509999b2012ca19',
            'q.enriched.url.url': source_url,
            'return': params.get('return', return_fields),
            'start': params.get('start', 'now-3d'),
            'end': params.get('end', 'now'),
            'count': params.get('count', '500'),
            'outputMode': 'json'
        }

        if results_next is not None:
            request_params['next'] = results_next

        results = requests.get(url=self.base_url, params=request_params).json()
        results_data = results['result']

        if 'next' in results_data.keys():
            next_data = self.request_source_articles(source_url, params=request_params, results_next=results_data['next'])
            results_data['docs'].extend(next_data['docs'])


        return results_data



    def request_source_articles_taxonomy(self, score, results_next=None):
        return_fields = 'enriched.url.cleanedTitle,enriched.url.relations,' \
                        'enriched.url.entities.entity.quotations,' \
                        'enriched.url.keywords,enriched.url.url,enriched.url.author,enriched.url.publicationDate,' \
                        'enriched.url.text,enriched.url.entities,enriched.url.concepts,enriched.url.taxonomy,' \
                        'enriched.url.docSentiment,enriched.url.enrichedTitle,enriched.url.enrichedTitle.relations,' \
                        'enriched.url.enrichedTitle.keywords,enriched.url.enrichedTitle.entities,' \
                        'enriched.url.enrichedTitle.concepts,enriched.url.enrichedTitle.taxonomy'

        request_params = {
            'return': return_fields,
            'start': 'now-1d',
            'end': 'now',
            'count': '1000',
            'rank': 'high',
            'outputMode': 'json'
        }

        if results_next is not None:
            request_params['next'] = results_next

        url_to_use = self.second_base_url + '&q.enriched.url.taxonomy.taxonomy_=|label=law,score=>' + str(score) + '|'

        result = requests.get(url=url_to_use, params=request_params).json()
        results_data = result['result']

        if 'next' in results_data.keys():
            next_data = self.request_source_articles_taxonomy(score=score, results_next=results_data['next'])
            results_data['docs'].extend(next_data['docs'])

        return results_data





    def clean_news_source_url(self, url):
        clean_url = url.replace('http://', '').replace('https://', '').replace('www.', '')
        return clean_url






    def get_historic_political_articles(self, score):
        try:
            political_articles = self.request_source_articles_taxonomy(score=score)
            progress = 0
            length_docs = len(political_articles['docs'])
            for source_article in political_articles['docs']:
                try:
                    source_article_data = source_article['source']['enriched']['url']
                    source_article_data['_id'] = str(hash(source_article_data['url']))
                    full_text = self.get_article_text_non_api(source_article_data['url'])
                    source_article_data['full_text'] = full_text
                    source_article_data['tone_data'] = self.get_tone_of_text_non_api(full_text)
                    self.historic_political_article_data.insert_one(source_article_data)
                    progress += 1
                    print('Progress: ' + str(progress) + ' / ' + str(length_docs))
                except Exception as e:
                    print(e.args)
        except Exception as a:
            print(a.args)



    def get_unique_ids_from_collection(self, collection):
        id_set = set()
        for element in collection.find():
            id_set.add(element['_id'])
        return id_set