from flask import Flask, render_template, request, jsonify
import sqlite3 as sql


tyre_cost_tbl = {
    "knobbly" : 15,
    "slick" : 10,
    "steelband" : 20,
    "reactive" : 40,
    "maglev" : 50
}
        
fuel_cost_tbl = {
    "petrol" : 4,
    "fusion" : 400,
    "steam" : 3,
    "bio" : 5,
    "electric" : 20,
    "rocket" : 16,
    "hamster" : 3,
    "thermo" : 300,
    "solar" : 40,
    "wind" : 20
}

#costs for fuel
cost_petrol = 4
cost_fusion = 400
cost_steam = 3
cost_bio = 5
cost_electric = 20
cost_rocket = 16
cost_hamster = 3
cost_thermo = 300
cost_solar = 40
cost_wind = 20
#costs for tyres
cost_knobbly = 15
cost_slick = 10
cost_steelband = 20
cost_reactive = 40
cost_maglev = 50

n_consumable_fuels = ["fusion", "thermo", "solar", "wind"]


# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies")
        record = cur.fetchone(); 
        return render_template("buggy-form.html", buggy = record)
    elif request.method == 'POST':
        msg=""
        qty_wheels = int(request.form['qty_wheels'])
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type']
        power_units = int(request.form['power_units'])
        aux_power_type = request.form['aux_power_type']
        aux_power_units = int(request.form['aux_power_units'])
        tyres = request.form['tyres']
        qty_tyres = int(request.form['qty_tyres'])
        cost = 0
        
        for i in tyre_cost_tbl:
            if tyres == i:
                tyrecost= tyre_cost_tbl[i] * qty_tyres
                cost += tyrecost
                
        for i in fuel_cost_tbl:
            if power_type == i:
                powercost= fuel_cost_tbl[i] * power_units
                cost += powercost
                
        for i in fuel_cost_tbl:
            if aux_power_type == i:
                auxpowercost= fuel_cost_tbl[i] * aux_power_units
                cost += auxpowercost
        
        if qty_wheels < 4:
            msg = "Error: The minimum number of wheels is 4. Please try again."
            return render_template("updated.html", msg = msg) 

        if qty_tyres < qty_wheels:
            msg = "Error: The minimum number of tyres must be equal to or greater than the number of wheels you have selected. Please try again."
            return render_template("updated.html", msg = msg) 

        if flag_color== flag_color_secondary and flag_pattern != "plain":
            msg = "Error: Primary and  Secondary color must be different if the flag pattern is not plain. Please try again."
            return render_template("updated.html", msg = msg) 
        
        if flag_color != flag_color_secondary and flag_pattern == "plain":
            msg = "Error: Primary and  Secondary color must be the same if the flag pattern is plain. Please try again."
            return render_template("updated.html", msg = msg) 

        if power_type in n_consumable_fuels:
            if power_units > 1:
                msg = "Error: You can only have one unit of non consumable fuel. Please try again."
                return render_template("updated.html", msg = msg)

        if aux_power_type in n_consumable_fuels:
            if aux_power_units > 1:
                msg = "Error: You can only have one unit of non consumable fuel. Please try again."
                return render_template("updated.html", msg = msg)

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, power_units=?, aux_power_type=?, aux_power_units=?, tyres=?, qty_tyres=?, cost=? WHERE id=?",
                        (qty_wheels, flag_color, flag_color_secondary, flag_pattern, power_type, power_units, aux_power_type, aux_power_units, tyres, qty_tyres, cost, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = f"Record successfully saved. The total cost of your buggy is: {cost}"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
