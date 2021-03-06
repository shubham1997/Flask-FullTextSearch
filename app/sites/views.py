#resource, resources, Resources
from flask import Blueprint, render_template, request,flash, redirect, url_for, jsonify, current_app
from app.sites.models import Sites, SitesSchema
from app.users.models import db
from app.users.views import Resource

import subprocess
from flask_restful import Api

sites = Blueprint('sites', __name__)
#http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
schema = SitesSchema(only=('id','tag'))
new_schema = SitesSchema()

# API START

api = Api(sites)


class SitesList(Resource):
    def get(self):
        query =  Sites.query.all()
        sites = new_schema.dump(query, many=True).data
        return jsonify({"sites":sites})

    def post(self):
         data=request.get_json(force=True)
         form_errors = schema.validate(data['site'])
         if not form_errors:
             url = data['site']['url']
             content = data['site']['content']
             tag = data['site']['tag']
             reddit_score = data['site']['reddit_score']
             ycombinator_score = data['site']['ycombinator_score']             
             site = Sites(url, content, tag, reddit_score=reddit_score, ycombinator_score=ycombinator_score)
             add = site.add(site)
             #if does not return any error
             if not add :
                return jsonify({"message":"success"})
             else:
                return jsonify({"message":add})
         else:
            print(form_errors)
            

class SitesUpdate(Resource):

    def get(self, id):
        query =  Sites.query.get(id)
        site = new_schema.dump(query).data
        return jsonify({"site":site})


    def put(self, id):
        site=Sites.query.get_or_404(id)
        data=request.get_json(force=True)
        form_errors = schema.validate(data['site'])
        if not form_errors:
               site.url = data['site']['url']
               site.content = data['site']['content']
               site.tag = data['site']['tag']
               site.reddit_score = data['site']['reddit_score']
               site.ycombinator_score = data['site']['ycombinator_score']
               update = site.update()
               #if does not return any error
               if not update :
                  return jsonify({"message":"success"})
               else:
                  return jsonify({"message":update})

    def delete(self, id):
        site=Sites.query.get_or_404(id)
        delete=site.delete(site)
        if not delete :
                 return jsonify({"message":"success"})

        else:
            return jsonify({"message":delete})




api.add_resource(SitesList, '/')
api.add_resource(SitesUpdate, '/<int:id>')

### SEARCH START ###
@sites.route('/search', methods=['GET'])
def search():

   return render_template('search.html')


@sites.route('/results/<int:page>', methods=['GET'] )
@sites.route('/results', defaults={'page': 1}, methods=['GET'] )
def results(page):
           search_string = request.args['search']
           query = Sites.query.search(search_string)
           results = query.paginate(page=page, per_page=10)
           return render_template('results.html', results=results)


@sites.route('/tags', methods=['GET'])
def tags():
    query = Sites.query.with_entities(Sites.id,Sites.tag).order_by(Sites.tag)
    tags = schema.dump(query, many=True).data
    return jsonify({"tags":tags})

## For testing only
@sites.route('/tag', methods=['GET'])

def tag():

    return render_template('tag.html')
## End testing
### SEARCH END ###

"""
#Sites
@sites.route('/' , methods=['GET'])
@login_required
def site_index():
    return render_template('/sites/index.html')

new_schema = SitesSchema()
@sites.route('/sites', methods=['GET'])
@login_required
def sites_all():
    query =  Sites.query.all()
    sites = new_schema.dump(query, many=True).data
    return jsonify({"sites":sites})


@sites.route('/add' , methods=['POST', 'GET'])
@login_required
def site_add():

    if request.method == 'POST':
        #Validate form values by de-serializing the request, http://marshmallow.readthedocs.org/en/latest/quickstart.html#validation


    return render_template('/sites/add.html')

@sites.route('/update/<int:id>' , methods=['POST', 'GET'])
@login_required
def site_update (id):
    #Get site by primary key:
    site=Sites.query.get_or_404(id)
    if request.method == 'POST':
        form_errors = schema.validate(request.form.to_dict())
        if not form_errors:
           site.url = request.form['url']
           site.content = request.form['content']
           site.tag = request.form['tag']
           return update(site , id, success_url = 'sites.site_index', fail_url = 'sites.site_update')
        else:
           flash(form_errors)


    return render_template('/sites/update.html', site=site)


@sites.route('/delete/<int:id>' , methods=['POST', 'GET'])
@login_required
def site_delete (id):
     site = Sites.query.get_or_404(id)
     return delete(site, fail_url = 'sites.site_index')

#CRUD FUNCTIONS
#Arguments  are data to add, function to redirect to if the add was successful and if not
def add (data, success_url = '', fail_url = ''):
    add = data.add(data)
    #if does not return any error
    if not add :
       flash("Add was successful")
       return redirect(url_for(success_url))
    else:
       message=add
       flash(message)
       return redirect(url_for(fail_url))


def update (data, id, success_url = '', fail_url = ''):

            update=data.update()
            #if does not return any error
            if not update :
              flash("Update was successful")
              return redirect(url_for(success_url))
            else:
               message=update
               flash(message)
               return redirect(url_for(fail_url, id=id))



def delete (data, fail_url=''):
     delete=data.delete(data)
     if not delete :
              flash("Delete was successful")

     else:
          message=delete
          flash(message)
     return redirect(url_for(fail_url))
"""
#Create  Triggers and Functions
@sites.route('/trigger', methods=['GET'])
def trig():
   SQL_index = db.text("""CREATE INDEX tsv_idx ON sites USING gin(search) """)
   db.engine.execute(SQL_index)
   SQL = db.text("""CREATE OR REPLACE FUNCTION search_trigger() RETURNS trigger AS $$
                begin
                  new.search :=
                    setweight(to_tsvector(coalesce(new.url,'')), 'B') ||
                    setweight(to_tsvector(coalesce(new.content,'')), 'C')||
                    setweight(to_tsvector(coalesce(new.tag,'')), 'A');
                  return new;
                end
                $$ LANGUAGE plpgsql""")
   db.engine.execute(SQL)
   SQL1 = db.text("""CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
               ON sites FOR EACH ROW EXECUTE PROCEDURE search_trigger();""")
   db.engine.execute(SQL1)
   return "Done"
