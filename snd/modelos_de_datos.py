import operator
from snd.models import *

'''
(
    (
        MODELO,
        [CAMPOS A FILTRAR/DESPLEGAR],
        [CAMPOS A DESPLEGAR],
        [['COLUMNA',[[COMPARACION, ESTILO]+]]]|None,
        [
            [
                NOMBRE A DESPLEGAR,
                URL,
                [PARAMETROS DEL URL],
                IMAGEN FA,
                [
                    [
                        [(campo)+],
                        [(valorCampo)+],
                        funcionDeEvaluacion
                    ]+
                ] | None
            ]+ | []
        ],
        False | True            -> Se consulta en todos los tenants o no
    ),
)
'''

MODELOS_DE_DATOS = (
    (
        CentroAcondicionamiento,
        ['nombre','direccion', 'telefono', 'ciudad', 'email', 'web', 'estado'],
        ['Nombre','Dirección', 'Teléfono', 'Ciudad', 'Email', 'Página Web', 'Estado'],
        None,
        [
            [
                "Ver CAF",
                'ver_caf',
                ['id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'crear_caf',
                ['Identificación', 'id'],
                'fa-gear',
                None
            ],
        ],
    ),
    (
        Deportista,
        ["foto","nombres apellidos","ciudad_residencia","tipo_id","identificacion","edad","disciplinas_deportivas","estado"],
        ["Foto","Nombre","Ciudad de residencia","Tipo Identificación","Identificación","Edad","Disciplinas","Estado"],
        None,
        [
            [
                "Ver Deportista",
                'ver_deportista',
                ['id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'edicion_deportista',
                ['id'],
                'fa-gear',
                [
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]

            ],
            [
                "CTD",
                'cambio_documento_deportista',
                ['id'],
                'fa-archive',
                [
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]

            ],
            [
                "A/I",
                'deportista_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ],
            [
                "Transferir",
                'generar_transferencia',
                ['1','1','id'],
                'fa-exchange',
                [
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]

            ],
            [
                "Cancelar Transferencia",
                'cancelar_transferencia',
                ['id','1'],
                'fa-times',
                [
                    [
                        ['estado'],
                        ['EN TRANSFERENCIA'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]

            ],

        ]
    ),
)

'''
    [
        "Activar/Desactivar",
        'desactivar_caf',
        ['id'],
        'fa-ban',
        None
    ],
'''