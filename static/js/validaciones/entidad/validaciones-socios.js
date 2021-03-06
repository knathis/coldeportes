/**
 * Created by diegoamt on 3/03/16.
 */

form = "#formulario-socio";
fields = {
    nombre: {
        validators: {
            notEmpty: {
                message: "El nombre no puede ser vacío"
            }
        }
    },
    apellido: {
        validators: {
            notEmpty: {
                message: "El apellido no puede ser vacío"
            }
        }
    },
    tipo_documento: {
        validators: {
            notEmpty: {
                message: "El tipo de documento no puede ser vacío"
            }
        }
    },
    numero_documento: {
        validators: {
            notEmpty: {
                message: "El número de documento no puede ser vacío"
            },
            regexp: {
                regexp: "^[0-9a-zA-Z]+$",
                message: "El número de documento solo puede contener números ó letras"
            }
        }
    },
    correo: {
        validators: {
            emailAddress: {
                message: "La dirección de correo electrónico no es válida"
            }
        }
    },
    fecha_incorporacion: {
        validators: {
            notEmpty: {
                message: "La fecha de incorporación no puede ser vacía"
            },
            date: {
                message: 'La fecha no es válida',
                format: 'YYYY-MM-DD',
                message: 'La fecha de incorporación no puede ser mayor a la fecha actual',
                max: ($.datepicker.formatDate('yy-mm-dd', new Date())).toString()
            }
        }
    }
};
$("#id_fecha_incorporacion").on('change',function(e){
   $(form).bootstrapValidator('revalidateField', 'fecha_incorporacion');
});
$.getScript(base+"js/validaciones/validations-base.js");