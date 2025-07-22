select * from veiculos_cadastrado;


CREATE TABLE permissoes_acesso (
  id_permissao INT AUTO_INCREMENT PRIMARY KEY,
  id_veiculo INT NOT NULL,
  validade DATE,
  horario_acesso VARCHAR(20),
  tipo_usuario VARCHAR(50),
  FOREIGN KEY (id_veiculo) REFERENCES veiculos_cadastrado(id_veiculo)
);


SELECT v.matricula, p.*
FROM permissoes_acesso p
JOIN veiculos_cadastrado v ON p.id_veiculo = v.id_veiculo
WHERE v.matricula = 'LD-51-15-HZ';

SELECT id_veiculo FROM veiculos_cadastrado WHERE matricula = 'LD-51-15-HZ';

INSERT INTO permissoes_acesso (id_veiculo, validade, horario_acesso, tipo_usuario) VALUES
(2, '2025-12-31', '09:00 - 18:00', 'Estudante'),
(3, '2025-12-31', '09:00 - 18:00', 'Visitante'),
(4, '2025-12-31', '09:00 - 18:00', 'Outro'),
(5, '2025-12-31', '09:00 - 18:00', 'Docente'),
(6, '2025-12-31', '09:00 - 18:00', 'Estudante'),
(7, '2025-12-31', '09:00 - 18:00', 'Outro'),
(8, '2025-12-31', '09:00 - 18:00', 'Visitante');
