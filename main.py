from flask import Flask, render_template, request, json
import requests
import mysql.connector as MYSQL

app = Flask(__name__)


@app.route("/")
def homepage():
    return render_template("home.html")

# Seems to be working
@app.route("/addcustomer", methods=['POST'])
def add_customer():
    data = json.loads(request.get_data().decode('utf8'))
    def f(x): return ("({0}{1}{2}) {3}{4}{5} {6}{7}{8}{9}").format(
        *([c for c in x])) if len(x) == 10 else " "
    query = (
        "INSERT INTO CUSTOMER (Name, Phone)  "
        'VALUES ( "{}", "{}" ) '
    )
    cnx = MYSQL.connect(
        user='root', password='trial123456', database='carrental2019')
    cursor = cnx.cursor()
    result = ""
    ph_num = f(data["number"])
    try:
        affected_count = cursor.execute(query.format(data["name"], ph_num))
        cnx.commit()
        print("Affected rows is: ", affected_count)
        result = "Success! Added a user to the database! Name: {} Phone: {}. Number of rows affected is: {} ".format(
            data["name"], ph_num, affected_count)
    except MYSQL.IntegrityError:
        print("Could not insert row")
        result = "Could not insert row! Error"
    finally:
        cursor.close()
    return json.dumps(result)

# seems to be working
@app.route('/addvehicle', methods=['POST'])
def addvehicle():
    data = json.loads(request.get_data().decode('utf8'))
    print(data)
    query = (
        "INSERT INTO VEHICLE (VehicleID, Description, Year, Type, Category) "
        'VALUES ( "{}", "{}", "{}", {}, {} )'
    )
    cnx = MYSQL.connect(
        user='root', password='trial123456', database='carrental2019')
    cursor = cnx.cursor()
    result = ""
    try:
        affected_count = cursor.execute(query.format(
            data["vin"], data["desc"], data["year"], data["type"], data["cat"]))
        cnx.commit()
        print("Affected rows is: ", affected_count)
        result = "Success! Added a vehicle to the database! VIN: {} Description: {} Year: {} Type: {} Category: {}. Number of rows affected is: {} ".format(
            data["vin"], data["desc"], data["year"], data["type"], data["cat"], affected_count)
    except MYSQL.IntegrityError:
        print("Could not insert row")
        result = "Could not insert row! Error Integrity Error"
    finally:
        cursor.close()
    # Return the row here
    return json.dumps(result)

# seems to be working
@app.route("/addreservation", methods=['POST'])
def add_reservation():
    def query_db(query, error, to_commit=False):
        result = []
        cnx = MYSQL.connect(
            user='root', password='trial123456', database='carrental2019')
        cursor = cnx.cursor()
        try:
            cursor.execute(query)
            if to_commit:
                cnx.commit()
                result.append("success")
                print(query, "committed result")
            else:
                result = cursor.fetchall()
            if len(result) == 0:
                return -1, json.dumps({
                    'success': 0,
                    'msg': error
                })
            return 1, result
        except MYSQL.Error as identifier:
            print("Error", identifier.msg)
            return 0, json.dumps({
                'success': 1,
                'msg': identifier.msg
            })
        finally:
            cursor.close()

    data = json.loads(request.get_data().decode('utf8'))
    print(data)
    # first check if name is valid or not, if not return
    success, result = query_db((
        "SELECT c.CustID FROM Customer AS c "
        'WHERE c.Name = "{}" '
    ).format(data["user_name"]),
        "There's no entry in the database for user with name: {}".format(
            data["user_name"])
    )
    if success != 1:  # theres' an error, notify the front end
        return result
    cust_id = (result[0])[0]
    print("Customer id: ", cust_id)

    # get the id for vehicle
    success, result = query_db((
        "SELECT v.VehicleID FROM Vehicle AS v "
        'WHERE v.Description = "{}"  and v.Year = "{}" and v.Type = {} and v.Category = {}'
    ).format(data["name"], data["year"], data["cat"], data["type"]),
        "There's no vehicle as specified! Something went wrong"
    )
    if success != 1:  # theres' an error, notify the front end
        return result
    vehicle_id = (result[0])[0]
    print("Printing result ", result)
    import datetime
    today_date = datetime.datetime.now().date()
    paid_for = today_date
    start_date = datetime.date(*(int(s) for s in data['start'].split('-')))
    end_date = datetime.date(*(int(s) for s in data['end'].split('-')))
    time_delta = (end_date - start_date).days
    no_weeks, no_days = int(time_delta/7), time_delta % 7
    print(no_days, no_weeks)
    if data["paid_for"] == False:
        paid_for = 'NULL'
    else:
        paid_for = '"'+today_date.strftime('%Y-%m-%d')+'"'
    # now insert into rental
    if no_weeks != 0:
        # first insert weekly rentals
        weekly_end = start_date + datetime.timedelta(days=no_weeks*7)
        success, result = query_db((
            "INSERT INTO rental (CustID, VehicleID, StartDate, OrderDate, RentalType, Qty, TotalAmount, PaymentDate, ReturnDate)  "
            'VALUES ({},"{}","{}","{}",{},{},{},{},"{}") '
        ).format(cust_id, vehicle_id, data["start"], today_date, 7, no_weeks, int(data["weekly"])*no_weeks, paid_for, weekly_end),
            "Could not insert for multiple weeks",
            to_commit=True
        )
        if no_days != 0:
            # now insert no of weeks
            daily_start = start_date + datetime.timedelta(days=no_weeks*7+1)
            success, result = query_db((
                "INSERT INTO rental (CustID, VehicleID, StartDate, OrderDate, RentalType, Qty, TotalAmount, PaymentDate, ReturnDate)  "
                'VALUES ({},"{}","{}","{}",{},{},{},{},"{}") '
            ).format(cust_id, vehicle_id, daily_start, today_date, 1, no_days, ((int(data["daily"])*no_days)-1), paid_for, data["end"]),
                "Could not insert Daily record",
                to_commit=True
            )
    else:
        # only daily rentals
        success, result = query_db((
            "INSERT INTO rental (CustID, VehicleID, StartDate, OrderDate, RentalType, Qty, TotalAmount, PaymentDate, ReturnDate)  "
            'VALUES ({},"{}","{}","{}",{},{},{},{},"{}") '
        ).format(cust_id, vehicle_id, data["start"], today_date, 1, no_days, int(data["total"]), paid_for, data["end"]),
            "Could not insert whole record",
            to_commit=True
        )

    return json.dumps({
        "success": 1
    })

# seems to be working
@app.route("/getreservation", methods=['POST'])
def get_reservation():
    data = json.loads(request.get_data().decode('utf8'))
    print(data)
    query = (
        'SELECT v.Description, v.Year, v.Category, v.Type, r.Daily , r.Weekly, (r.Daily * {} + r.Weekly * {} ) as total_cost  '
        'from vehicle as v, rate as r   '
        'where v.Type = {} and v.Category = {}  '
        'and v.VehicleID not in (select rt.VehicleID from rental as rt where rt.StartDate between "{}" and "{}" or rt.ReturnDate between "{}" and "{}" ) '
        'and v.Category = r.Category and v.Type = r.Type   '
    )

    # TODO: need to finalize if days and weeks must be exact or not!
    def calculate_days_week(start, end):
        import datetime
        days_diff = (abs((datetime.date(*(int(s) for s in end.split('-')))) -
                         (datetime.date(*(int(s) for s in start.split('-')))))).days
        no_days = (days_diff % 7)
        return int(no_days), int((days_diff-no_days)/7)
    cnx = MYSQL.connect(
        user='root', password='trial123456', database='carrental2019')
    cursor = cnx.cursor()
    result = ""
    try:
        affected_count = cursor.execute(query.format(
            *calculate_days_week(data["start"], data["end"]), data["type"], data['cat'], data['start'], data['end'], data['start'], data['end']))
        print("Affected rows is: ", affected_count)
        result = cursor.fetchall()
    except MYSQL.IntegrityError:
        print("Could not fetch row")
        result = None
    finally:
        cursor.close()
    if result == None:
        return json.dumps("noentry")    # return json.dumps("noentry")
    value = []
    for entry in result:
        value.append([attribute for attribute in entry])
    # description, year, type, category, daily, weekly, totalcost
    return json.dumps(value)


@app.route('/addreturncar', methods=["POST"])
def add_returncar():
    data = request.get_data().decode('utf8')
    order_date = ''
    print('return car: ', data)
    return json.dumps("Success")

# seems to be working
@app.route('/getreturncar', methods=["POST"])
def get_returncar():
    data = json.loads(request.get_data().decode('utf8'))
    print(data)
    cnx = MYSQL.connect(
        user='root', password='trial123456', database='carrental2019')
    cursor = cnx.cursor()
    result = ""
    try:
        affected_count = cursor.execute(
            (
                'select customer.Name, vehicle.Description, vehicle.Year, rental.OrderDate, rental.StartDate, rental.ReturnDate, rental.TotalAmount   '
                'from customer, vehicle, rental   '
                'where customer.CustID = rental.CustID and vehicle.VehicleID = rental.VehicleID  '
                'and customer.Name like "%{}%" and vehicle.Description like "%{}%" and rental.ReturnDate = "{}" and rental.PaymentDate is null '
            ).format(
                data["name"], data["desc"], data["return"]
            )
        )
        print("Affected rows is: ", affected_count)
        result = cursor.fetchall()
    except MYSQL.IntegrityError:
        print("Could not fetch row")
        result = None
    finally:
        cursor.close()
    if result == None:
        print("integrity error")
        return json.dumps({
            "success": 0,
            "msg": "No entries were found for that days "
        })
    value = []
    for entry in result:
        print(entry)
        order_d, start_d, return_d = entry[3].strftime(
            '%Y-%m-%d'), entry[4].strftime('%Y-%m-%d'), entry[5].strftime('%Y-%m-%d')
        value.append([entry[0], entry[1], entry[2],
                      order_d, start_d, return_d, entry[6]])
    # of the form [name, vehicle description, year, order date, start date, return date, total amount]
    if len(value) == 0:
        return json.dumps({
            "success": 0,
            "msg": "Entries were found but, no Unpaid records were found please check different names "
        })
    print(value)
    return json.dumps({
        "success": 1,
        'data': value
    }
    )


@app.route('/viewbalance', methods=["POST"])
def viewbalance():
    sentence = request.get_data().decode('utf8')
    print(sentence)
    # of the form [USERID, name, balance]
    return json.dumps([[123, "Paras Pathak", 999.90]])


@app.route('/viewrate', methods=["POST"])
def viewrate():
    sentence = request.get_data().decode('utf8')
    print(sentence)
    # of the form [VIN, Description, Daily rate]
    return json.dumps([["791vh890idalsn5634", "Porsche 911", 999.90]])


def index():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM Users WHERE id=1''')
    row_headers = [x[0]
                   for x in cur.description]  # this will extract row headers
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json.dumps(json_data)


if __name__ == "__main__":
    app.run(debug=True)
