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
    ),
)
'''

MODELOS_DE_DATOS = (
    (  #Numero de modelo 0
        CentroAcondicionamiento,
        ['nombre','direccion', 'telefono', 'ciudad', 'email', 'web', 'estado'],
        ['Nombre','Dirección', 'Teléfono', 'Ciudad', 'Email', 'Página Web', 'Estado'],
        None,
        [
            [
                "Ver CAF",
                'ver_caf',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'crear_caf',
                ['Identificación', 'id'],
                'fa-gear',
                [
                    [
                        'snd.add_centroacondicionamiento',
                    ],
                    [
                        ['estado'],
                        ['Activo'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'desactivar_caf',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.add_centroacondicionamiento',
                    ]
                ]

            ]
        ],
    ),
    #MODELO DE DATOS CAF PARA LIGAS Y FEDERACIONES
    (   #Numero de modelo 1
        CentroAcondicionamiento,
        ['nombre','direccion', 'telefono', 'ciudad', 'email', 'web', 'entidad'],
        ['Nombre','Dirección', 'Teléfono', 'Ciudad', 'Email', 'Página Web', 'Entidad'],
        None,
        [
            [
                "Ver CAF",
                'ver_caf',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
        ],
    ),
    (   #Numero de modelo 2
        Deportista,
        ["foto","nombres apellidos","ciudad_residencia","tipo_id","identificacion","estado"],
        ["Foto","Nombre","Ciudad de residencia","Tipo Identificación","Identificación","Estado"],
        None,
        [
            [
                "Ver Deportista",
                'ver_deportista',
                ['id','entidad.id','estado'],
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
                        'snd.change_deportista',
                    ],
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
                        'snd.change_deportista',
                    ],
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
                        'snd.change_deportista',
                    ],
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
                ['id'],
                'fa-exchange',
                [
                    [
                        'snd.change_deportista',
                    ],
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
                ['id'],
                'fa-times',
                [
                    [
                        'snd.change_deportista',
                    ],
                    [
                        ['estado'],
                        ['EN TRANSFERENCIA','TRANSFERIDO INTERNACIONAL'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ],

        ],
    ),
    #MODELO DE DATOS PARA DEPORTISTAS PARA EL TENANT TIPO LIGA Y FEDERACIÓN
    (   #Numero de modelo 3
        Deportista,
        ["foto","nombres apellidos","ciudad_residencia","tipo_id","identificacion","entidad"],
        ["Foto","Nombre","Ciudad de residencia","Tipo Identificación","Identificación","Entidad"],
        None,
        [
            [
                "Ver Deportista",
                'ver_deportista',
                ['id','entidad.id','estado'],
                'fa-eye',
                None
            ]
        ],
    ),
    (   #Numero de modelo 4
        PersonalApoyo,
        ['foto','nombres apellidos', 'actividad', 'identificacion', 'estado'],
        ['Foto','Nombre', 'Actividad desempeñada', 'Identificación', 'Estado'],
        None,
        [
            [
                "Ver más",
                'ver_personal_apoyo',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'edicion_personal_apoyo',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_personalapoyo',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'personal_apoyo_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_personalapoyo',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]
            ]
        ],
    ),
    #MODELO DE DATOS PARA PERSONAL DE APOYO PARA FEDERACIONES Y LIGAS
    (   #Numero de modelo 5
        PersonalApoyo,
        ['foto','nombres apellidos', 'actividad', 'identificacion', 'entidad'],
        ['Foto','Nombre', 'Actividad desempeñada', 'Identificación', 'Entidad'],
        None,
        [
            [
                "Ver más",
                'ver_personal_apoyo',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'edicion_personal_apoyo',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_personalapoyo',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'personal_apoyo_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_personalapoyo',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ]
        ],
    ),
    (   #Numero de modelo 6
        Dirigente,
        ['foto','identificacion','nombres apellidos', 'estado'],
        ['Foto','Identificación','Nombre', 'Estado'],
        None,
        [
            [
                "Ver más",
                'dirigentes_ver',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'dirigentes_edicion',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_dirigente',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'dirigentes_activar_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_dirigente',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ]
        ],
    ),
    #MODELO DE DATOS DIRIGENTE PARA LIGA Y FEDERACIÓN
    (   #Numero de modelo 7
        Dirigente,
        ['foto','identificacion','nombres apellidos', 'entidad'],
        ['Foto','Identificación','Nombre', 'Entidad'],
        None,
        [
            [
                "Ver más",
                'dirigentes_ver',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'dirigentes_edicion',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_dirigente',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'dirigentes_activar_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_dirigente',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ]
        ],
    ),
    (   #Numero de modelo 8
        Escenario,
        ['nombre','ciudad','estrato', 'estado'],
        ['Nombre','Ciudad (Departamento)','Estrato', 'Estado'],
        None,
        [
            [
                "Ver más",
                'ver_escenario',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'wizard_identificacion',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_escenario',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'desactivar_escenario',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.add_escenario',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]

            ]
        ],
    ),
    #MODELO DE DATOS PARA ESCENARIO LIGAS Y FEDERACIONES
    (   #Numero de modelo 9
        Escenario,
        ['nombre','ciudad','estrato', 'entidad'],
        ['Nombre','Ciudad (Departamento)','Estrato', 'Entidad'],
        None,
        [
            [
                "Ver más",
                'ver_escenario',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'wizard_identificacion',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_escenario',
                    ]
                ]
            ],
        ],
    ),
    (   #Numero de modelo 10
        Seleccion,
        ["nombre", "tipo", "fecha_inicial", "fecha_final", "campeonato", "tipo_campeonato"],
        ["Nombre", "Tipo de Selección", "Fecha Convocatoria", "Fecha Finaliza Convocatoria", "Nombre Campeonato", "Tipo Campeonato"],
        None,
        [
            [
                "Ver Seleccion",
                'ver_seleccion',
                ['id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'editar_seleccion',
                ['id'],
                'fa-gear',
                None
            ],
        ],
    ),
    #11
    #MODELO PARA CLUB PARALIMPICO
    (
        Deportista,
        ["foto","nombres apellidos","ciudad_residencia","tipo_id","identificacion","estado"],
        ["Foto","Nombre","Ciudad de residencia","Tipo Identificación","Identificación","Estado"],
        None,
        [
            [
                "Ver Deportista",
                'ver_deportista',
                ['id','entidad.id','estado'],
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
        ],
    ),
    #MODELO DE DATOS PARA CENTROS BIOMÉDICOS
    #Numero de modelo 12
    (
        CentroBiomedico,
        ['nombre','direccion', 'telefono_fijo', 'ciudad', 'email', 'web', 'estado'],
        ['Nombre','Dirección', 'Teléfono', 'Ciudad', 'Email', 'Página Web', 'Estado'],
        None,
        [
            [
                "Ver Centro Biomédico",
                'centro_biomedico_ver',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'centro_biomedico_crear_editar',
                ['identificacion', '1', 'id'],
                'fa-gear',
                [
                    [
                        'snd.add_centrobiomedico',
                    ]
                ]
            ],
        ],
    ),
    #MODELO DE DATOS PARA CAJAS DE COMPENSACIÓN 
    (   #Numero de modelo 13
        CajaCompensacion,
        ['foto', 'nombre', 'publico', 'clasificacion', 'region', 'estado'],
        ['Logo', 'Nombre', 'Público', 'Clasificación', 'Región', 'Estado'],
        None,
        [
            [
                "Ver más",
                'ver_ccf',
                ['id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'wizard_editar_caja',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_cajacompensacion',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'desactivar_ccf',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_cajacompensacion',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]
            ],
        ],
    ),
    #MODELO DE DATOS PARA ESCUELAS DE FORMACIÓN DEPORTIVA
    #Numero de modelo 14
    (
        EscuelaDeportiva,
        ['nombre','direccion', 'tipo_sede', 'telefono_fijo', 'ciudad', 'email', 'web', 'estado'],
        ['Nombre','Dirección', 'Tipo Sede', 'Teléfono', 'Ciudad', 'Email', 'Página Web', 'Estado'],
        None,
        [
            [
                "Ver EFD",
                'escuela_deportiva_ver',
                ['id','entidad.id'],
                'fa-eye',
                None
            ],
            [
                "Editar",
                'wizard_sede',
                ['id'],
                'fa-gear',
                [
                    [
                        'snd.add_escueladeportiva',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0])
                    ]
                ]
            ],
            [
                "A/I",
                'escuela_deportiva_desactivar',
                ['id'],
                'fa-ban',
                [
                    [
                        'snd.change_escueladeportiva',
                    ],
                    [
                        ['estado'],
                        ['ACTIVO','INACTIVO'],
                        lambda x, y: operator.eq(x[0], y[0]) or operator.eq(x[0], y[1])
                    ]
                ]
            ],
        ],
    ),
)