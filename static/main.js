
var element_to_add_for_reservation = [];
var element_to_add_for_return = [];
var table_return = null;
var reserve_table = null;
var view_user = null;
var view_vehicle = null;

function make_ajax_call(url_to_make, returning_function, data_to_send, type_of_request) {
    $.ajax({
        type: type_of_request,
        contentType: 'application/json; charset=utf-8',
        url: url_to_make,
        data: JSON.stringify(data_to_send),
        dataType: "json",
        success: function (param) {
            console.log("in success callback");
            returning_function(param);
        }
    });


}

//Callback for when user presses to add a customer
function add_customer() {
    var name = $("#name_customer").val();
    var num = $("#phone_customer").val();
    console.log(name)
    if (name.length > 0) {
        data = {
            name: name,
            number: num
        }
        make_ajax_call("/addcustomer", function (param) {
            alert(param);
            console.log((param));
        }, data, "POST");
    } else {
        alert("There's no name!");
    }

}

//Callback for when user presses to add a vehicle
function add_vehicle() {
    var vin = $("#vehicle_vin").val();
    //TODO: make sure the length of VIN is as needed for the database
    if (vin.length != 18) {
        alert("Vehicle's VIN must be 18 characters long! Error.");
        return;
    }
    var desc = $("#vehicle_description").val();
    if (desc.length == 0) {
        alert("There's no Description for vehicle");
        return;
    }
    var year = $("#vehicle_year").val();
    if (year.length == 0) {
        alert("There's no Year for vehicle");
        return;
    }
    var type = $("#vehicle_type").val();
    if (type.length == 0) {
        alert("There's no type for vehicle");
        return;
    }
    var cat = $("#vehicle_category").val();
    if (cat.length == 0) {
        alert("There's no category for vehicle");
        return;
    }
    make_ajax_call("/addvehicle", function (param) {
        //Notify the user in someway
        alert(param);
    }, {
        "vin": vin,
        "desc": desc,
        "year": year,
        "type": type,
        "cat": cat
    }, "POST");
}

//Callback for when user presses to reserve a vehicle
function reserve_car(params) {
    $.modal.close();
    var is_paid = false;
    if (params === 1) {
        is_paid = true;
    }
    var data = element_to_add_for_reservation.pop();
    make_ajax_call("/addreservation", function (server) {
        //Successfully added records in the database
        if (server["success"] == 1) {
            alert("Added a record in the database");
            back_button(3);
        } else {
            alert(server["msg"]);
        }
    }, {
        "name": data["name"],
        "year": data["year"],
        "type": data["type"],
        "cat": data["cat"],
        "daily": data["daily"],
        "weekly": data["weekly"],
        "total": data["total"],
        "user_name": data["user_name"],
        "start": data["start"],
        "end": data["end"],
        "vin":data["vin"],
        "paid_for": is_paid
    }, "POST");
}

//To get all the cars available for specified parameters
function fetch_cars() {
    var name = $("#reserve_name").val();
    var start = $("#reserve_start").val();
    var end = $("#reserve_end").val();
    var type = $("#rental_type").val();
    var category = $("#rental_category").val();
    if (start.length === 0 || end.length === 0 || name.length == 0) {
        alert("Please select a date/name");
        return;
    }
    if (type.length === 0 || category.length === 0) {
        alert("Please select type/category of vehicle");
        return;
    }
    make_ajax_call("/getreservation", function (param) {
        //Notify the user in someway
        console.log("Fetched reservation from the database", param);
        if (param == "noentry") {
            alert("There's no customer with that name, please create a custoner");
            return;
        }
        reserve_table = $("#reservation_table").DataTable({
            data: param,
            "bDestroy": true,
            "columnDefs": [{
                "targets": -1,
                "data": null,
                "defaultContent": "<button>Reserve</button>"
            }],
            columns: [
                { title: "Description" },
                { title: "Year" },
                { title: "Type" },
                { title: "Category" },
                { title: "Daily Rate" },
                { title: "Weekly Rate" },
                { title: "Total Cost" },
                {title:"VIN"},
                { title: "Reserve this" }
            ]
        });
        $('#reservation_table tbody').on('click', 'button', function () {
            var data = reserve_table.row($(this).parents('tr')).data();
            element_to_add_for_reservation.push({
                "name": data[0],
                "year": data[1],
                "type": data[2],
                "cat": data[3],
                "daily": data[4],
                "weekly": data[5],
                "total": data[6],
                "start": start,
                "end": end,
                "user_name": name,
                "vin":data[7]
            });
            $("#fade").modal({
                fadeDuration: 100
            });
        });
    }, {
        "name": name,
        "start": start,
        "end": end,
        "type": type,
        "cat": category
    }, "POST");
}

//Callback for when user presses to return a customer
function get_return_car() {
    var name = $("#return_name").val();
    var return_date = $("#return_returndate").val();
    var desc = $("#return_vehicledesc").val();

    if (name.length === 0 || return_date.length === 0 || desc.length === 0) {
        alert("You are missing fields! Check Name/Date/Information");
        return;
    }
    make_ajax_call("/getreturncar", function (param) {
        //Populate all the tables
        console.log("Fetched all return value from db");
        if (param["success"] == 0) {
            alert(param["msg"]);
            return;
        }
        table_return = $("#return_table").DataTable({
            data: param["data"],
            "bDestroy": true,
            "columnDefs": [{
                "targets": -1,
                "data": null,
                "defaultContent": "<button>Pay</button>"
            }],
            columns: [
                { title: "Name" },
                { title: "Vehicle Description" },
                { title: "Year" },
                { title: "Order Date" },
                { title: "Start Date" },
                { title: "Return Date" },
                // {title:"Type"},
                { title: "Total Amount" },
                {title: "VIN"},
                { title: "Return and Pay" }
                
            ]
        });
        $('#return_table tbody').on('click', 'button', function () {
            var data = table_return.row($(this).parents('tr')).data();
            element_to_add_for_return.push({
                "name": data[0],
                "desc": data[1],
                "year": data[2],
                "order": data[3],
                "start": data[4],
                "return": data[5],
                "total": data[6],
                "vin":data[7]
            });
            make_ajax_call("/addreturncar", function (param) {
                if (param == "Success") {
                    alert("Car has been returned");
                    var row = element_to_add_for_return.pop();
                    document.getElementById("add_return_data").innerHTML = `
                    Person Name: `+ row["name"] + `
                    , Description: `+ row["desc"] + `
                    , Year: `+ row["year"] + `
                    , Order Date: `+ row["order"] + `
                    , Start Date: `+ row["start"] + `
                    , Return Date: `+ row["return"] + `
                    , Total Amount: `+ row["total"] + `
                      ===> has been paid and returned`;
                    $("#return_modal").modal({
                        fadeDuration: 100
                    });
                    $("#return_modal").on($.modal.AFTER_CLOSE, function (param) {
                        back_button(4);
                    });
                }
            }, {
                "name": data[0],
                "desc": data[1],
                "year": data[2],
                "order": data[3],
                "start": data[4],
                "return": data[5],
                "total": data[6],
                "vin":data[7]
            }, "POST");
        });
    }, {
        "name": name,
        "return": return_date,
        "desc": desc
    }, "POST");
}

//Callback for when user presses to view results about user's details
function view_results() {
    make_ajax_call("/viewbalance", function (param) {
        //Notify the user in someway
        console.log("Query the db for result to the database");
        if (param == "noentry") {
            alert("There's no user record with that name, date and description. Try again");
            return;
        }
        view_user = $("#userview_table").DataTable({
            data: param,
            "bDestroy": true,
            "order": [[ 2, "desc" ]],
            columns: [
                { title: "User ID" },
                { title: "User Name" },
                { title: "User Balance" }
            ]
        });
    }, {
        "name": $("#view_username").val(),
        "id": $("#view_userid").val()
    }, "POST");
}

function view_vehicle_function() {
    make_ajax_call("/viewrate", function (param) {
        if (param == "noentry") {
            alert("There's no vehicle record with that parameters. Try again");
            return;
        }
        view_vehicle = $("#vehicleview_table").DataTable({
            data: param,
            "bDestroy": true,
            "order": [[ 2, "asc" ]],
            columns: [
                { title: "VIN" },
                { title: "Description" },
                { title: "Daily Price" }
            ]
        });
    }, {
        "desc": $("#view_vehicledesc").val(),
        "vin": $("#view_vehicleid").val()
    }, "POST");
}

function back_button(index) {
    if (index === 1) {
        $("#addcustomer").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    } else if (index === 2) {
        $("#addvehicle").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    } else if (index === 3) {
        if (reserve_table != null) {
            reserve_table.destroy();
            $("#reservation_table tr").remove();
            reserve_table = null;
        }
        $("#reservation").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    } else if (index === 4) {
        if (table_return != null) {
            table_return.destroy();
            $("#return_table tr").remove();
            table_return = null;
        }
        $("#returncar").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    } else if (index === 5) {
        if (view_user != null) {
            view_user.destroy();
            $("#userview_table tr").remove();
            view_user = null;
        }
        $("#viewresult").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    } else if (index === 6) {
        if (view_vehicle != null) {
            view_vehicle.destroy();
            $("#vehicleview_table tr").remove();
            view_vehicle = null;

        }
        $("#viewresult2").hide("slow", function () {
            document.getElementById("main-page").style.visibility = "visible";
            $("#main-page").show("slow");
        });
    }
}

function change_view(number) {
    console.log(number);
    if (number == 1) {
        $("#main-page").hide("slow", function () {
            document.getElementById("addcustomer").style.visibility = "visible";
            $("#addcustomer").show("slow");
        });
    } else if (number == 2) {
        $("#main-page").hide("slow", function () {
            document.getElementById("addvehicle").style.visibility = "visible";
            $("#addvehicle").show("slow");
        });

    } else if (number == 3) {
        $("#main-page").hide("slow", function () {
            document.getElementById("reservation").style.visibility = "visible";
            $("#reservation").show("slow");
        });
    } else if (number == 4) {
        $("#main-page").hide("slow", function () {
            document.getElementById("returncar").style.visibility = "visible";
            $("#returncar").show("slow");
        });
    } else if (number == 5) {
        $("#main-page").hide("slow", function () {
            document.getElementById("viewresult").style.visibility = "visible";
            $("#viewresult").show("slow");
        });
    } else if (number == 6) {
        $("#main-page").hide("slow", function () {
            document.getElementById("viewresult2").style.visibility = "visible";
            $("#viewresult2").show("slow");
        });
    }
}