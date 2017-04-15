import ujson as json


from watson_developer_cloud import AlchemyDataNewsV1, AlchemyLanguageV1, ToneAnalyzerV3, WatsonException
import datetime
from pymongo import MongoClient, InsertOne, DeleteOne, ReplaceOne
import re
import requests



'''
    Other Api Keys:
    - 2190f450728492113ce4e5b880a72eefbea73308
    6b686d275c4cce6fe46efcbffd38a73f526c921c
    - d4a97f67bd08aa3720bd3be9dc5c92ad720f16fa
    - d0eaa84bd893b3cf74fc3b9f421d68c565b3eece
    - 6986aa6422f93320f04afb2fc73b185d1f64f16c
    - 4e1cb9a6ee6aa63df294081a617e4badcc9b5d33
    8d08311e0e4414627830b863eac01c8661ead2d3
    - original key = ab47ce88f70194629e6986fa08dda1fc8f9961a4
'''


class WatsonService(object):
    api_key = ''

    api_full_return_fields = [
        'enriched.url.title',
        'enriched.url.url',
        'enriched.url.author',
        'enriched.url.feeds',
        'enriched.url.cleanedTitle',
        'enriched.url.relations',
        'enriched.url.entities.entity.quotations',
        'enriched.url.keywords',
        'enriched.url.url',
        'enriched.url.publicationDate',
        'enriched.url.text',
        'enriched.url.entities',
        'enriched.url.concepts',
        'enriched.url.taxonomy',
        'enriched.url.docSentiment',
        'enriched.url.publicationDate',
    ]

    api_return_fields = [
        'enriched.url.title', 'enriched.url.url', 'enriched.url.publicationDate', 'enriched.url.enrichedTitle.taxonomy'
    ]

    base_url = 'https://watson-api-explorer.mybluemix.net/alchemy-api/calls/data/GetNews'
    second_base_url = 'https://watson-api-explorer.mybluemix.net/alchemy-api/calls/data/GetNews?apikey=edd60853a78c2a0e33859cfff509999b2012ca19'
    database_name = 'AkashicRecords'


    def __init__(self):


        self.alchemy_language = AlchemyLanguageV1(api_key=self.api_key)
        self.alchemy_data_news = AlchemyDataNewsV1(api_key=self.api_key)
        # self.tone_analyzer = ToneAnalyzerV3(version='2016-05-19 ', username=self.config['username'], password=self.config['password'])
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[self.database_name]
        self.news_source_article_data = self.database['news_source_article_data']
        self.historic_political_article_data = self.database['historic_political_article_data']




    def get_article_text(self, article_url):
        result = self.alchemy_language.text(url=article_url)
        stop_here = ""
        full_text = result['text']
        return full_text


    def get_article_text_non_api(self, article_url):
        api_url = 'https://alchemy-language-demo.mybluemix.net/api/text'
        params = {
            'url': article_url
        }
        result = requests.post(api_url, data=params)
        article_text = result.json()['text']
        stop_here = ""
        return article_text



    def get_language_results(self, url):

        fields = [

        ]
        combined_operations = ['page-image', 'entity', 'keyword', 'title', 'author',
                               'taxonomy', 'concept', 'doc-emotion']
        # print(
            # json.dumps(alchemy_language.combined(url=url, extract=combined_operations),
        language_results = {

        }

        article_text = ""

        for field in fields:
            api_url = 'https://alchemy-language-demo.mybluemix.net/api/' + field
            params = {
                'url': url
            }



            result = requests.post(api_url, data=params)
            article_text = result.json()['text']
            stop_here = ""
        return article_text








    def get_tone_of_text_non_api(self, text_data):
        api_url = 'https://tone-analyzer-demo.mybluemix.net/api/tone'
        params = {
            'text': text_data
        }
        result = requests.post(api_url, data=params)
        tone_data = result.json()
        return tone_data


    def get_typed_relations_non_api(self, text_data):
        api_url = 'https://alchemy-language-demo.mybluemix.net/api/typedRelations'
        params = {
            'text': text_data,
            'entities': 1,
            'keywords': 1,
            'arguments': 1
        }
        result = requests.post(api_url, data=params)
        typed_relations = result.json()
        return typed_relations


    def request_source_articles(self, source_url, params=None):
        return_fields = 'enriched.url.cleanedTitle,enriched.url.relations,enriched.url.entities.entity.quotations,' \
                        'enriched.url.keywords,enriched.url.url,enriched.url.author,enriched.url.publicationDate,' \
                        'enriched.url.text,enriched.url.entities,enriched.url.concepts,enriched.url.taxonomy,' \
                        'enriched.url.entities, enriched.url.docSentiment'

        request_params = {}

        if params is not None:
            request_params = {
                'apikey': 'edd60853a78c2a0e33859cfff509999b2012ca19',
                'q.enriched.url.url': source_url,
                'return': params.get('return', return_fields),
                'start': params.get('start', 'now-3d'),
                'end': params.get('end', 'now'),
                'count': params.get('count', '500'),
                'rank': 'high',
                'outputMode': 'json'
            }
        else:
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

        return requests.get(url=self.base_url, params=request_params).json()



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
            stop_here = ""

        stop_here = ""

        return results_data


    def get_source_articles_data(self, source_url, params=None):
        json_data = {}
        try:
            cleaned_url = source_url.replace('.com', '')
            json_data = self.request_source_articles(cleaned_url, params)
        except Exception as e:
            print(e.args)
        return json_data


    def clean_news_source_url(self, url):
        clean_url = url.replace('http://', '').replace('https://', '').replace('www.', '')
        return clean_url


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