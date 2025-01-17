from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

#sqlalchemy database access
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return jsonify(FoodItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New menu Item (%s)  created!"%newItem.name)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    oldItem = editedItem.name
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Editted menu item \'%s\' to \'%s\'"%(oldItem, editedItem.name))
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("Deleted menu item \'%s\'"%(deleteItem.name))
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=deleteItem)
        
    return "page to delete a menu item. Task 3 complete!"


if __name__ == "__main__":
    app.secret_key='super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)


