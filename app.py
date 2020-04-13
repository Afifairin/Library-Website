from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_, or_, not_

# url_for flask fn, css


app=Flask(__name__)
app.secret_key="hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True



db = SQLAlchemy(app)

class Booklist(db.Model):
    __searchable__ = ['title', 'author']
    id= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(200), nullable=False)
    author= db.Column(db.String(200),  default='N/A')
    count=db.Column(db.Integer, default='0')
    date_update= db.Column(db.DateTime, nullable= False, default= datetime.utcnow)

    def __repr__(self):
        return 'Book list '+ str(self.id)


class Admin:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    def __repr__(self):
        return f'<Admin: {self.username}>'

users = []
users.append(Admin(id=1, username='admin', password = 'password' )) 
users.append(Admin(id=2, username='afifa', password = 'lockdown' )) 
print(users)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin_login.html')

@app.route('/adminlogin', methods=['POST','GET'])
def admin_login():
    if request.method == 'POST':
        session.pop('user_id',None)

        username = request.form['username']
        password = request.form['password']
        for x in users: 
            if (x.username == username) and (x.password == password):
                if x.id == 1 :
                    session['user_id'] = x.id   
                    return redirect(url_for('books'))
                else:
                    session['user_id'] = x.id
                    return redirect(url_for('booklist')) #redirect to search
                    # users    

            else:
                return redirect(url_for('admin_login'))
        return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')
   


@app.route('/booklist', methods=['POST','GET'])
def booklist():
     all_books= Booklist.query.order_by(Booklist.title).all()

     return render_template('booklist.html', books=all_books )

@app.route('/dashboard', methods=['POST','GET'])
def books():
    if request.method=="POST":
        book_title=request.form['title']
        book_author=request.form['author']
        book_count=request.form['count']
        new_book = Booklist(title=book_title, author=book_author, count=book_count)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added")
        return redirect (url_for("books"))
    else:
        all_books= Booklist.query.order_by(Booklist.title).all()
        return render_template('dashboard.html', books=all_books)

@app.route('/delete/<int:id>' )
def delete(id):
    book_to_delete=Booklist.query.get_or_404(id)

    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/dashboard')   
    except:
        return 'life is helll'


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    book_to_update=Booklist.query.get_or_404(id)

    if request.method== 'POST':
        book_to_update.title= request.form['title']
        book_to_update.author= request.form['author']
        book_to_update.count= request.form['count']
        
        try:
            db.session.commit()
            flash("Book updated")
            return redirect('/dashboard')
            
        except:
            return "AAAAA......Quarentin"
            
    else:
        return render_template ('update.html', book= book_to_update)


@app.route('/search', methods=('POST','GET'))
def search():
    
    if request.method == 'POST':
        search_value = request.form ['search']
        search= "%{0}%".format(search_value)   
        results = Booklist.query.filter ( or_( Booklist.title.ilike(search),Booklist.author.ilike(search) ) ).all()
        return render_template('booklist.html', books=results)
    else:
        flash("no match found")
        return redirect('#')
        



@app.route('/getcommand', methods=('POST','GET'))
def getcommand():
    
    if request.method == 'POST':

        command= request.json['command']
       
        if command=="search":

            if request.method=="POST":    
                search_value = request.json ['search']
                #{"command":"search", "search":"", "id":"" ,"title":"lord","author":"tolkien", "count":""}
                search= "%{0}%".format(search_value)   
                results = Booklist.query.filter (or_( Booklist.title.ilike(search),Booklist.author.ilike(search) ) ).all()
                ret= [{'id':book.id, 'title': book.title, 'author':book.author, 'count':book.count}for book in results]        
                return  jsonify(ret)
           
        
        elif command=="delete":
            #{"command":"delete",  "id":"any id" ,"title":"","author":"", "count":""}
            id= request.json['id']
            book_to_delete=Booklist.query.get_or_404(id)

            db.session.delete(book_to_delete)
            db.session.commit()
            return jsonify({'result': True})
       
        elif command=="update":
        
            id= request.json['id']
            book_to_update=Booklist.query.get_or_404(id)

            book_to_update.title=request.json.get('title',book_to_update.title)
            book_to_update.author=request.json.get('author',book_to_update.author)
            book_to_update.count=request.json.get('count',book_to_update.count)
            
            db.session.commit()
            return jsonify({'result': True})
        
        elif command=="add":
            if request.method=="POST":
                book_title=request.json['title']
                book_author=request.json['author']
                book_count=request.json['count']
                new_book = Booklist(title=book_title, author=book_author, count=book_count)
                db.session.add(new_book)
                db.session.commit()
                id= new_book.id
                return jsonify({'id': id}) 
          

        elif command=="login":
    
            username = request.json['username']
            password = request.json['password']
            for x in users: 
                if (x.username == username) and (x.password == password):
                    if x.id == 1 :
                        return jsonify({'username': username})
                    else:
                        return jsonify({'username': username}) 
        
        elif command=="show_all":
            all_books= Booklist.query.order_by(Booklist.title).all()
            result= [{'id':book.id, 'title': book.title, 'author':book.author, 'count':book.count}for book in all_books]        
            return  jsonify(result)
           

                   
                            

if __name__=="__main__":
    db.create_all()
    app.run(host='0.0.0.0', debug=True)  #running on http://127.0.0.1:5000/


