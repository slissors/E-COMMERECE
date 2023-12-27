from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, TextAreaField, FloatField, HiddenField
from flask_bootstrap import Bootstrap
from wtforms.validators import DataRequired, Length

app = Flask(__name__)

# photos = UploadSet('photos', IMAGES)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
bootstrap = Bootstrap(app)

# configure_uploads(app, photos)

db = SQLAlchemy(app)



#Table for products
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Integer)  # in cents
    stock = db.Column(db.Integer)
    eco = db.Column(db.Integer)
    desc = db.Column(db.String(500))
    bestBefore = db.Column(db.String(10))
    image = db.Column(db.String(100))


    # checks if fish in stock before adding to cart
    def warehouse(self):
        if session:
            fish = []
            fish = session['cart']

            index = 0
            if len(fish) >= 1:
                for ind, it in enumerate(fish):
                    if it.get('id') == self.id:
                        index = ind
                return self.stock - fish[index].get('quantity')
            else:
                return self.stock
        else:
            return self.stock



# ------------------------ FORMS HERE -----------------------------


class AddProduct(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 16)])
    price = FloatField('Price', validators=[DataRequired()])
    stock = IntegerField('Quantity', validators=[DataRequired()])
    eco = IntegerField('Eco Score', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    bestBefore = StringField('Best Before', validators=[DataRequired()])
    image = StringField('Image', validators=[DataRequired()])
    Add = SubmitField('Submit')


class Cart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')


class Checkout(FlaskForm):
    firstName = StringField('First Name')
    lastName = StringField('Last Name')
    phoneNumber = StringField('Phone Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    postcode = StringField('Postcodes')
    cardNumber = IntegerField('Card Number')
    expiryDate = StringField('Expiry Date')
    cvv = IntegerField('CVV')
    review = TextAreaField('Leave a Review (Optional)')

    

#handles cart sessions

# --------------- Routes ------------------



#----------------- HOME ------------------

#renders home
@app.route('/')
def index():
    products = Product.query.all()

    return render_template('index.html', products=products)


#singular product view 
@app.route('/product/<id>')
def product(id):
    form = Cart()
    product = Product.query.filter_by(id=id).first()

    return render_template('view.html', product=product, form=form)

#sorting products, in ascended order
@app.route('/sort/<string:sortby>')
def sortProducts(sortby):

    if sortby == 'name':
        products = Product.query.order_by(Product.name.asc())
        sorted_flag = True
    elif sortby == 'price':
        products = Product.query.order_by(Product.price.asc())
        sorted_flag = True
    elif sortby == 'eco':
        products = Product.query.order_by(Product.eco.asc())
        sorted_flag = True
    else:
        products = Product.query.all()
        sorted_flag = False

    return render_template('index.html', products=products, sorted_flag=sorted_flag)





# ------------------ CART ---------------------



#cart session quantatity logic taken from, but I modified it so when same fish in cart is added they are merged into same fish instead of seperate
#  https://github.com/allansifuna/Flask-Shopping-Cart-WebApp/blob/main/app.py


def cartSession():
    products = []
    fishTotals = {}  # Dictionary to store the totals of each fish
    counter = 0
    grandTotal = 0
    quantityTotal = 0

    for fish in session['cart']:
        product = Product.query.filter_by(id=fish['id']).first()

        quantity = int(fish['quantity'])
        total = quantity * product.price
        grandTotal += total

        quantityTotal += quantity

        # Check if the fish is already in the fishTotals dictionary, new fish added to fish  dictionary
        if fish['id'] in fishTotals:
            # If the fish exists, update the total and quantity
            fishTotals[fish['id']]['total'] += total
            fishTotals[fish['id']]['quantity'] += quantity

        else:
            fishTotals[fish['id']] = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'quantity': quantity,
                'total': total,
                'counter': counter
            }
            counter += 1

    # Convert the fish_totals dictionary to a list of products
    for fish in fishTotals.values():
        products.append(fish)

    return products, grandTotal, quantityTotal


# retrieve products, grand total, and quantity total from the cartSession() function and renders cart.html
@app.route('/cart')
def cart():

    products, grandTotal, quantityTotal = cartSession()

    # no products in the cart, render the emptyCart.html template
    if not products:
        return render_template('emptyCart.html')

    return render_template('cart.html', products=products, grandTotal=grandTotal, quantityTotal=quantityTotal)


# adds fish to cart from the index page with a quantity of 1
@app.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    # appends fish ID and quantity to cart session
    session['cart'].append({'id': id, 'quantity': 1})
    session.modified = True

    return redirect(url_for('index'))


# adds a fish to the cart from the singular fish view, allowing the user to choose the quantity
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():

    form = Cart()

    if form.validate_on_submit():
        # Appends the fish ID and quantity from the form to the cart session
        session['cart'].append({'id': form.id.data, 'quantity': form.quantity.data})
        session.modified = True

    elif 'cart' not in session:
        session['cart'] = []

    return redirect(url_for('index'))


# rmvs a fish from the cart
@app.route('/cartDelete/<counter>')
def cartDelete(counter):

    # deletes fish at the specified counter index from cart session
    del session['cart'][int(counter)]
    session.modified = True
    return redirect(url_for('cart'))







#the form does not update the table, as there is no database created, could not make it work
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = Checkout()

    products, grandTotal, quantityTotal = cartSession()

    if form.validate_on_submit():
        
        for product in products:
            product = Product.query.filter_by(id=product['id']).update(
                {'stock': Product.stock - product['quantity']})

        session['cart'] = []
        session.modified = True
       
        return render_template('thanks.html')

    return render_template('checkout.html', form=form, grandTotal=grandTotal, quantityTotal=quantityTotal)




# ------------- Admin STARTS HERE ---------------


#adds porduct to sale if form is filled oout
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    form = AddProduct()

    if form.validate_on_submit():

        newProduct = Product(name=form.name.data, 
                             price=form.price.data,
                             stock=form.stock.data, 
                             desc=form.desc.data, 
                             bestBefore=form.bestBefore.data, 
                             eco=form.eco.data, 
                             image=form.image.data)

        db.session.add(newProduct)
        db.session.commit()
 
    products = Product.query.all()
    return render_template('admin/admin.html', admin=True, form=form, products=products)


#allows product to be editted
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = AddProduct(request.form, obj=product)

    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('admin/editProducts.html', form=form, product=product)


#deletes product from table
@app.route('/deleteProduct/<int:id>', methods=['POST'])
def deleteProduct(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('admin'))




#the running man
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)