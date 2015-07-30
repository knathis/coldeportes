/**
 * Created by daniel on 30/07/15.
 */
var grado_semestre = document.getElementById("id_grado_semestre");
var profesion = document.getElementById("id_profesion");
var fecha_finalizacion = document.getElementById("id_fecha_finalizacion");

$(document).ready(function() {
    App.init();
    FormWizard.init();
    grado_semestre.disabled=true;
    profesion.disabled=true;
    fecha_finalizacion.disabled=true;
});

document.getElementById("id_nivel").onchange=function(){
    var nivel = document.getElementById("id_nivel").value + "";
    if(nivel == "Pregrado" || nivel == "Postgrado"){
        profesion.disabled=false;
    }else{
        profesion.disabled=true;
        profesion.value='';
    }

};

document.getElementById("id_estado").onchange=function(){
    var estado = document.getElementById("id_estado").value + "";
    if(estado=="Actual"){
        //se quita fecha
        fecha_finalizacion.disabled=true;
        fecha_finalizacion.value='';
        //se pone grado
        grado_semestre.disabled=false;
    }else{
        if(estado == "Finalizado" || estado=="Incompleto") {
            //se pone fecha
            fecha_finalizacion.disabled = false;
            //se quita grado
            grado_semestre.disabled = true;
            grado_semestre.value = '';
        }else{
            //Algun otro caso
            grado_semestre.disabled=true;
            fecha_finalizacion.disabled=true;
        }
    }

};