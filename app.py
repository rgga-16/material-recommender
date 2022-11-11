from flask import Flask, render_template, request
import config

def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])
app.register_error_handler(404, page_not_found)


@app.route('/', methods=["GET", "POST"])
def index():

    products = {
        "table": {"parts":["tabletop","legs"]},
        "carpet":{"parts":["carpet"]},
        "chair":{"parts":["backseat","seat","legs","arms"]},
    }
    
    n_products = len(products.keys())

    if request.method == 'POST':
        print()
    
    return render_template('index.html', **locals())


@app.route('/product-description', methods=["GET", "POST"])
def productDescription():

    if request.method == 'POST':
        query = request.form['productDescription']
        print(query)

        prompt = 'AI Suggestions for {} are:'.format(query)
        openAIAnswer = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

    return render_template('product-description.html', **locals())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
