﻿INSERT INTO indervalle.snd_dirigente (id, tipo_identificacion, identificacion, nombres, apellidos, genero, email, foto, perfil, entidad_id, estado, ciudad_residencia_id, telefono_fijo, telefono_celular) VALUES
  (1000, 'CC', '123456', 'PEDRO', 'BERMUDEZ CANO', 'HOMBRE', 'pedro@example.com', '', 'Descripción de Pedro', 1, 0, 1, '2222222', '2222222'),
  (1001, 'CC', '123458', 'PATRICIA', 'ARANDA NUÑEZ', 'MUJER', 'patricia@example.com', '', 'Descripción de Patricia', 1, 0, 2, '1111111', '1111111'),
  (1002, 'CE', '123457', 'MARIANA', 'PUERTA GUTIERREZ', 'MUJER', 'mariana@example.com', '', 'Descripción de Mariana', 1, 0, 3, '3333333', '3333333'),
  (1003, 'CC', '123459', 'LEONARDO', 'PIDRAHITA CANO', 'HOMBRE', 'leonardo@example.com', '', 'Descripción de Leonardo', 1, 0, 4, '5555555', '5555555'),
  (1004, 'PS', '123455', 'SEBASTIAN', 'SUAREZ RENGIFO', 'HOMBRE', 'sebastian@example.com', '', 'Descripción de Sebastian', 1, 0, 5, '8888888', '8888888');

INSERT INTO indervalle.snd_dirigente_nacionalidad (id, dirigente_id, nacionalidad_id) VALUES
  (1000, 1000, 52),
  (1001, 1001, 53),
  (1002, 1002, 51),
  (1003, 1003, 52),
  (1004, 1004, 52);

INSERT INTO indervalle.snd_dirigentecargo (id, nombre, fecha_posesion, fecha_retiro, superior_id, superior_cargo_id, dirigente_id, vigencia_inicio, vigencia_fin) VALUES
 (1000,'Presidente','01-01-2010','31-12-2010',NULL,NULL,1000,'01-01-2010','31-12-2010'),
 (1001,'Presidente','01-01-2011','31-12-2012',NULL,NULL,1000,'01-01-2011','31-12-2012'),
 (1008,'Presidente','01-01-2013','28-12-2015',NULL,NULL,1003,'01-01-2013','28-12-2015'),
 (1002,'Vicepresidente','01-01-2013','31-12-2013',1003,1008,1000,'01-01-2013','31-12-2013'),
 (1003,'Vicepresidente','01-01-2014','28-12-2015',1003,1008,1001,'01-01-2014','28-12-2015'),
 (1004,'Gerente','01-01-2014','06-08-2014',1001,1003,1002,'01-01-2014','06-08-2014'),
 (1005,'Contador','29-12-2015','03-03-2016',1001,1003,1003,'29-12-2015','03-03-2016'),
 (1006,'Vocero','01-01-2014','06-08-2014',1002,1004,1004,'01-01-2014','06-08-2014'),
 (1007,'Asistente','01-01-2016','03-03-2016',1003,1005,1004,'01-01-2016','03-03-2016');

INSERT INTO indervalle.snd_dirigentefuncion (descripcion, dirigente_id, cargo_id) VALUES
  ('Función uno', 1000,1000),
  ('Función dos', 1000,1000),
  ('Función tres', 1000,1000),
  ('Función uno', 1001,1001),
  ('Función dos', 1001,1001),
  ('Función tres', 1001,1001),
  ('Función uno', 1002,1002),
  ('Función dos', 1002,1003),
  ('Función tres', 1002,1004),
  ('Función uno', 1003,1005),
  ('Función dos', 1003,1006),
  ('Función tres', 1003,1006),
  ('Función uno', 1004,1007),
  ('Función dos', 1004,1008),
  ('Función tres', 1004,1008);