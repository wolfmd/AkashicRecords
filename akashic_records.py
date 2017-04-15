from flask import Flask, request, redirect, url_for, g
from flask.ext.pymongo import PyMongo
import json
from flask import render_template
from state_service import StateService
import requests
from neo4j.v1 import GraphDatabase


app = Flask(__name__)
app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'AkashicRecords'


mongo = PyMongo(app, config_prefix='MONGO')



@app.route('/trending')
def trending_page():
    pass




@app.route('/sentiment')
def sentiment_page():
    pass




@app.route('/article')
def article_page():
    pass





@app.route('/home')
def home():
    pass




@app.route('/')
def index():
    found_article_data = {
        'title': '',
        'text': '',
        'entities': [],
        'keywords': [],
        'concepts': [],
        'relations': []
    }
    for article_data in mongo.db.historic_political_article_data.find():
        if 'reddit' not in article_data['url']:
            if len(article_data['relations']) > 20:
                found_article_data['title'] = article_data['cleanedTitle']
                found_article_data['text'] = article_data['full_text']
                found_article_data['entities'] = article_data['entities'][:5]
                found_article_data['keywords'] = article_data['keywords'][:5]
                found_article_data['concepts'] = article_data['concepts'][:5]

                relation_sentence_groups = {}
                for relation in article_data['relations']:
                    try:
                        relation_sentence = relation['sentence']
                        if relation_sentence in relation_sentence_groups.keys():
                            relation_sentence_groups[relation_sentence].append(relation)
                        else:
                            relation_sentence_groups[relation_sentence] = [relation]
                    except Exception as e:
                        print(e.args)

                for sentence, relations in relation_sentence_groups.items():
                    relation_data = {
                        'sentence': sentence,
                        'relations': relations
                    }
                    found_article_data['relations'].append(relation_data)

                break

    return render_template('index.html', article=found_article_data)





if __name__ == '__main__':
    app.run()







'''


@app.route('/search/<search_input>')
def search_results(search_input):


    matching_results = []

    if search_input is not None:
        for work in mongo.db.cat_data.find():
            if search_input in work['title']:
                matching_results.append(work)

    return render_template('search.html', matching_results=matching_results)


@app.route('/works/<work_id>')
def works_page(work_id):
    work = mongo.db.cat_data.find_one({'_id': work_id})
    authors = []
    for author in work['authors']:
        author_data = requests.get(str('https://openlibrary.org' + author['author']['key'] + '.json')).text
        authors.append(author_data)
    work['authors'] = authors
    return render_template('works.html', work=work)


@app.route('/find', methods = ['POST', 'GET'])
def find():
   if request.method == 'POST':
      search_input = request.form['search_input']
      return redirect(url_for('search_results', search_input = search_input))
   else:
       search_input = request.args.get('search_input')
       return redirect(url_for('search_results', search_input = search_input))


'''