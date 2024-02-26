function updateForm(id) {
    if (id>0) {
        $("#back-button-p").show();
    } else {
        $("#back-button-p").hide();
    }
    if (id<5) {
        $("#next-button-p").show();
    } else {
        $("#next-button-p").hide();
    }
    for (var i=1; i<6; i++) {
        if (i<=id+1) {
            $("#step" + i).show();
        } else {
            $("#step" + i).hide();
        }
        var inputsAndSelects = $("#step" + i + " input, #step" + i + " select");
        if (i<=id) {
            inputsAndSelects.prop("disabled", true);
        } else {
            inputsAndSelects.prop("disabled", false);
        }
    }
    if (id === 4) {
        $("#last-step").show();
    } else {
        $("#last-step").hide();
    }
    if (formId >= 2) {
        $("#student-info-box").removeClass("is-hidden")
        $("#other-students-info-box").removeClass("is-hidden")

    } else {
        $("#student-info-box").addClass("is-hidden")
        $("#other-students-info-box").addClass("is-hidden")
    }
}

function updatePricesTable(tableId, tutorId) {
    $.get({
        type: 'GET',
        url: '/get_tutor_prices/' + tutorId,
        success: function (response) {
            const price_data_v = response.price_table_v
            const price_data_p = response.price_table_p
            $("#subject-title").text($(element).find('td:first').text());
            prices_table_v.clear().draw();
            prices_table_v.row.add(createPricesRow(price_data_v, 3)).draw();
            prices_table_v.row.add(createPricesRow(price_data_v, 2)).draw();
            prices_table_v.row.add(createPricesRow(price_data_v, 1)).draw();
            prices_table_v.row.add(createPricesRow(price_data_v, 0)).draw();
            prices_table_v.order([0,  'desc']).draw();

            prices_table_p.clear().draw();
            prices_table_p.row.add(createPricesRow(price_data_p, 3)).draw();
            prices_table_p.row.add(createPricesRow(price_data_p, 2)).draw();
            prices_table_p.row.add(createPricesRow(price_data_p, 1)).draw();
            prices_table_p.row.add(createPricesRow(price_data_p, 0)).draw();
            prices_table_p.order([0,  'desc']).draw();
        }
    })


}

function checkValidValues(fId) {
    var valid = true
    if (fId === 4) {
        const hours = parseInt($('#step4 input').val());
        if (isNaN(hours) || hours < 1) {
            alert(
                "El valor ingresado para la cantidad de horas es Incorrecto! " +
                "\nModifique el valor y continue con los siguientes pasos."
            );
            valid = false
        }
    }
    if (fId === 3) {
        const students = parseInt($("#step3 input").val());
        if (isNaN(students) || students < 1) {
            alert(
                "La cantidad de alumnos ingresada es Incorrecta! "+
                "\nModifique el valor y continue con los siguientes pasos."
            );
            valid = false
        }
    }
    return valid
}

function updatePriceDetail(form_id) {
    var subjectId = $("#subject-selector").val();
    var classType =  $('#class-type-selector').val();
    var subjectElement = $("#subject-selector").find(`option[value='${subjectId}']`);
    var factor = parseFloat($("#prices-table-v").data("factor"))
    var indPrice = parseFloat($(subjectElement).data(`priceref`));
    var precioHora = indPrice * factor * 1.5;
    if (classType === "p") {precioHora *= 1.25}
    var students = parseInt($("#step3 input").val());
    var hours = parseInt($('#step4 input').val());

    if (form_id >= 0) {
        $("#price-detail-list").empty()
        renderPricesTable("prices-table", subjectId, showV=true, showP=true)
    }
    if (form_id >= 1) {
        if (classType === "v") {
            renderPricesTable("prices-table", subjectId, showV=true, showP=false)
        } else {
            renderPricesTable("prices-table", subjectId, showV=false, showP=true)
        }
    }
    if (form_id >= 2) {
        $("#price-detail-list").append(`<h4 class="subtitle is-4 has-text-centered my-1">Detalle del Precio</h4>`)
        $("#price-detail-list").append(`<hr class="fade-out-hr mt-3 mb-3">`)
        $("#price-detail-list").append(`<ul class="has-text-centered"></ul>`)

        if (students === 2) {
            var precioHora = precioHora * 0.8;
        } else if (students === 3) {
            var precioHora = precioHora * 0.7;
        } else if (students >3) {
            var precioHora = precioHora * 0.6;
        }

        var text = `<p>Valor de la hora simple: <strong>${formatPrice(precioHora)}</strong></p>`
        $("#price-detail-list ul").append(text)
        $("#price-detail-list").append(`<hr class="fade-out-hr mt-3 mb-3">`)
    }
    if (form_id >= 3) {
        var q10 = Math.floor(hours / 10);
        var r10 = hours % 10;
        var r10q5 = Math.floor(r10 / 5);
        var r10r5 = r10 % 5;
        var text = "";
        var indTotal = 0
        if (r10r5 !== 0) {
            var hoursString = "hora";
            var hourType = "simple";
            if (r10r5 > 1) {
                hoursString += "s";
                hourType += "s";
            }
            indTotal += r10r5 * precioHora
            text += `<li>${r10r5} ${hoursString} ${hourType} de ${formatPrice(precioHora)}</li>`;
        }
        if (r10q5 !== 0) {
            var precioSimple = precioHora * 6.25 / 1.5
            indTotal += r10q5 * precioSimple
            if (text !== "") {
                text += `<li>+</li>`
            }
            text += `<li>${r10q5} pack de 5 horas de ${formatPrice(precioSimple)}</li>`
        }
        if (q10 !== 0) {
            var hoursString = "pack";
            if (q10 > 1) {
                hoursString += "s";
            }
            var precioSimple = precioHora * 10.0 / 1.5
            indTotal += q10 * precioSimple
            if (text !== "") {
                text += `<li>+</li>`
            }
            text += `<li>${q10} ${hoursString} de 10 horas de ${formatPrice(precioSimple)}`
        }

        $("#price-detail-list").append(`<ul class="has-text-centered"></ul>`)
        $("#price-detail-list ul:last-of-type").append(text)
        $("#price-detail-list").append(`<hr class="fade-out-hr mt-3 mb-3">`)
        var perStudent = indTotal / students
        $("#price-detail-list").append(`<p>Total por estudiante: <strong>${formatPrice(perStudent)}</strong></p>`)
        $("#price-detail-list").append(`<hr class="fade-out-hr mt-3 mb-3">`)
        $("#price-detail-list").append(`<p>Total: <strong>${formatPrice(indTotal)}</strong></p>`)
    }
    if (form_id >=4) {
        $("#last-step p.is-pulled-right").text(formatPrice(indTotal))
    }
}

function createStudentInfo(studentSuffix, includeName= true, includeLastName = true, includePhone = true, includeUsername = true) {
    var studentInfo = `<div id="student-info-${studentSuffix}" class="has-text-centered mt-5">
                        <h1 class="subtitle m-2">Estudiante ${studentSuffix}</h1>
                        <hr class="fade-out-hr m-2">`

    if (includeUsername) {
        studentInfo += `<div class="field">
                          <p class="control has-icons-left has-icons-right">
                            <input id="student-username-${studentSuffix}" class="input is-success is-small" type="text" placeholder="Usuario">
                              <span class="icon is-small is-left">
                                <i class="fa fa-user"></i>
                              </span>
                              <span class="icon is-small is-right">
                                <i class="fa fa-check"></i>
                              </span>
                          </p>
                        </div>`
    }
    if (includeName) {
        studentInfo += `<div class="field">
                          <p class="control has-icons-left has-icons-right">
                            <input id="student-name-${studentSuffix}" class="input is-success is-small" type="text" placeholder="Nombre/s">
                              <span class="icon is-small is-left">
                                <i class="fa fa-user"></i>
                              </span>
                              <span class="icon is-small is-right">
                                <i class="fa fa-check"></i>
                              </span>
                          </p>
                        </div>`
    }

    if (includeLastName) {
        studentInfo += `<div class="field">
                          <p class="control has-icons-left has-icons-right">
                            <input id="student-last-name-${studentSuffix}" class="input is-success is-small" type="text" placeholder="Apellido">
                            <span class="icon is-small is-left">
                              <i class="fa fa-user"></i>
                            </span>
                            <span class="icon is-small is-right">
                              <i class="fa fa-check"></i>
                            </span>
                          </p>
                        </div>`
    }

    if (includePhone) {
        studentInfo += `<div class="field">
                          <p class="control has-icons-left has-icons-right">
                            <input id="student-phone-${studentSuffix}" class="input is-small" type="text" placeholder="Nro. Telefono">
                            <span class="icon is-small is-left">
                              <i class="fab fa-whatsapp"></i>
                            </span>
                            <span class="icon is-small is-right">
                              <i class="fa fa-check"></i>
                            </span>
                          </p>
                        </div>`
    }
    studentInfo += `</div>`
    return studentInfo
}
function transformClassRowsData(classRowsData) {
    var rows = {}
    var i = 0
    $(classRowsData).each(function(rowIndex, row) {
        rows["row"+i] = []
        $(row).each(function(cellIndex, cell) {
            var cellInfo = getCellInfo(cell)
            var cellData = {
                year_index: cellInfo[0],
                week_index: cellInfo[1],
                day_index: cellInfo[2],
                time_index: cellInfo[3]
            }
            rows["row"+i].push(cellData)
        })
        i++
    })
    return rows
}
function getCellInfo(cell) {
    if (cell === undefined) {
        var returnInfo = [0, 0, 0, 0, 0]
    } else {
        var tdList = $(cell).parent().find("td")
        var returnInfo =  [parseInt($(tdList[12]).text()), parseInt($(tdList[2]).text()), $(cell).index() - 4, parseInt($(tdList[4]).text()), $(tdList[1]).text()]
    }
    return returnInfo
}

function classRowsCreation(addedCells) {
    var rows = []
    $(addedCells).each(function(index, cell) {
        var pushed = false
        $(rows).each(function(rowIndex, row) {
            var lastRowCellInfo = getCellInfo(row[row.length - 1])
            var cellInfo = getCellInfo(cell)
            if (
                lastRowCellInfo[0] === cellInfo[0] &&
                lastRowCellInfo[1] === cellInfo[1] &&
                lastRowCellInfo[2] === cellInfo[2] &&
                lastRowCellInfo[3] === cellInfo[3] - 1
            ) {
                row.push(cell)
                pushed = true
            }
        })
        if (!pushed) {
            rows.push([cell])
        }
        if (rows.length === 0) {
            rows.push([cell])
        }
    })
    return rows
}

function renderPricesTable(tableId, subjectId, showV=true, showP=true) {
    $(`.prices-data`).each(function(index, element) {
        if ($(element).attr("id") === `price-table-${subjectId}`) {
            $(element).removeClass("is-hidden")
        } else {
            $(element).addClass("is-hidden")
        }
    })
    if (!showV) {
        $(`#${tableId}-v`).addClass("is-hidden")
    } else {
        $(`#${tableId}-v`).removeClass("is-hidden")
    }
    if (!showP) {
        $(`#${tableId}-p`).addClass("is-hidden")
    } else {
        $(`#${tableId}-p`).removeClass("is-hidden")
    }
}
// function renderPricesTable(tableId, subjectId, showV=true, showP=true) {
//     if (!showV) {
//         $(`#${tableId}-v`).addClass("is-hidden")
//     } else {
//         $(`#${tableId}-v`).removeClass("is-hidden")
//         $(`#${tableId}-v tbody tr`).each(function(rowIndex, rowElement) {
//             if ($(rowElement).data("subject_id") !== parseInt(subjectId)) {
//                 $(rowElement).addClass("is-hidden")
//             } else {
//                 $(rowElement).removeClass("is-hidden")
//             }
//         })
//     }
//     if (!showP) {
//         $(`#${tableId}-p`).addClass("is-hidden")
//     } else {
//         $(`#${tableId}-p`).removeClass("is-hidden")
//         $(`#${tableId}-p tbody tr`).each(function(rowIndex, rowElement) {
//             if ($(rowElement).data("subject_id") !== parseInt(subjectId)) {
//                 $(rowElement).addClass("is-hidden")
//             } else {
//                 $(rowElement).removeClass("is-hidden")
//             }
//         })
//     }
// }