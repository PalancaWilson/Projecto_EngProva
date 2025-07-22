
import re
from flask_cors import CORS, cross_origin
from db_config import conectar
from reconhecimento import detectar_matricula
from ReconhecimentoModelo import detectar_modelo_veiculo

from reconhecimento import detectar_matricula
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

import mysql.connector

import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='template')
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True) # Aplica CORS global
CORS(app, origins=["http://127.0.0.1:5501"])


@app.route('/ping')
def ping():
    return "pong"



@app.route('/')
def home():
    return jsonify({"mensagem": "API ISPSECURITY ativa!"})




@app.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()  # <- CORS especificamente na rota
def login():
    if request.method == 'OPTIONS':
        return '', 204  # resposta ao preflight

    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')
    tipo = dados.get('tipo')

    conn =conectar()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM funcionarios WHERE email=%s AND senha=%s AND cargo=%s"
   
    cursor.execute(query, (email, senha, tipo))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario:
        return jsonify({"status": "sucesso", "usuario": usuario})
    else:
        return jsonify({"status": "erro", "mensagem": "Credenciais inválidas."}), 401
@app.route('/cadastrar-veiculo', methods=['POST'])
def cadastrar_veiculo():
    matricula = request.form.get('matricula')
    proprietario = request.form.get('proprietario')
    id_frequentador = request.form.get('id_frequentador')
    cor = request.form.get('cor')
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    estado = request.form.get('estado', 'Ativo')

    imagem = request.files.get('imagem')

    if not all([matricula, proprietario, id_frequentador]):
        return jsonify({"status": "erro", "mensagem": "Preencha todos os campos obrigatórios (matricula, proprietario, id_frequentador)."}), 400

    nome_arquivo = None
    if imagem and imagem.filename != '':
        nome_seguro = secure_filename(imagem.filename)
        caminho = os.path.join(UPLOAD_FOLDER, nome_seguro)
        imagem.save(caminho)
        nome_arquivo = nome_seguro

    try:
        conn = conectar()
        cursor = conn.cursor()

        # 1️⃣ Inserir veículo
        query_veiculo = """
            INSERT INTO veiculos_cadastrado 
            (matricula, proprietario, marca, modelo, cor, estado, imagem, id_frequentador)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_veiculo, (
            matricula, proprietario, marca, modelo, cor, estado, nome_arquivo, id_frequentador
        ))

        id_veiculo = cursor.lastrowid  # Pega o ID do veículo recém-cadastrado

        # 2️⃣ Inserir permissão de acesso padrão
        query_permissao = """
            INSERT INTO permissoes_acesso (id_veiculo, id_frequentador, validade, horario_acesso)
            VALUES (%s, %s, %s, %s)
        """
        validade_padrao = None  # ou date.today() + timedelta(days=365) se quiser 1 ano
        horario_padrao = '08:00-18:00'  # Ou deixe None se quiser acesso livre

        cursor.execute(query_permissao, (
            id_veiculo, id_frequentador, validade_padrao, horario_padrao
        ))

        conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Veículo e permissão cadastrados com sucesso!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

    finally:
        cursor.close()
        conn.close()




@app.route('/dashboard')
def dashboard():
    return render_template('dashboard_seguranca.html')

@app.route('/camera')
def camera():
    return render_template('Camera_Sec.html')

@app.route('/historico')
def historico():
    return render_template('historicoAcessoSec.html')

#rotas das paginas do Administrador
@app.route('/dashboardAdmin')
def dashboardAdmin():
    return render_template('dasbord.html')  # Confirma se o nome do arquivo está correto: dasbord.html ou dashboard.html?

@app.route('/cadastro-veiculo')
def cadastro_veiculo_page():
    return render_template('cadastroVeiculo.html')

@app.route('/historico-acesso')
def historico_acesso_page():
    return render_template('historicoAcesso.html')

@app.route('/gerenciar-veiculos')
def gerenciar_veiculos_page():
    return render_template('gerenciarUsuario.html')

@app.route('/permissoes-acesso')
def permissoes_acesso_page():
    return render_template('PermissoesAcesso.html')



# Rota da API para Segurança
@app.route('/api/dashboard', methods=['GET'])
def dados_dashboard():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM veiculos_cadastrado WHERE estado = 'Ativo'")
        autorizados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM acessos WHERE estado = 'Recusado'")
        negadas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM acessos WHERE DATE(data_acesso) = CURDATE() AND estado = 'Autorizado'; ")
        acessos_hoje = cursor.fetchone()[0]

        return jsonify({
            "autorizados": autorizados,
            "negadas": negadas,
            "acessos_hoje": acessos_hoje
        })

    except Exception as e:
        print("❌ Erro ao buscar dados do dashboard:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Rota para o dashboard do administrador
@app.route('/dashboardAdmin-data')
def dashboard_admin_data():
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM veiculos_cadastrado")
        total_veiculos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM acessos WHERE estado = 'Recusado'")
        recusados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM acessos WHERE DATE(data_acesso) = CURDATE() AND estado = 'Autorizado'; ")
        acessos_dia = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM veiculos_cadastrado WHERE estado='Inativo';")
        pendentes = cursor.fetchone()[0]

        return jsonify({
            "total_veiculos": total_veiculos,
            "recusados": recusados,
            "acessos_dia": acessos_dia,
            "pendentes": pendentes
        })
    except Exception as e:
        print("Erro ao buscar dados do dashboard Admin:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()




# rota para o gráfico de acessos por hora
@app.route("/grafico-acessos", methods=["GET"])
def grafico_acessos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT HOUR(hora_acesso) AS hora, COUNT(*) AS total
            FROM acessos
            WHERE data_acesso = CURDATE()
            GROUP BY HOUR(hora_acesso)
            ORDER BY hora
        """)
        dados = cursor.fetchall()
        return jsonify(dados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
    
        conn.close()



## Rota dos veículos que acessaram a instituição nas ultimas 24 horas
@app.route("/ultimos-acessos", methods=["GET"])
def ultimos_acessos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                TIME_FORMAT(a.hora_acesso, '%H:%i') AS hora,
                v.matricula,
                a.estado
            FROM acessos a
            JOIN veiculos_cadastrado v ON a.id_carro = v.id_veiculo
            ORDER BY a.data_acesso DESC, a.hora_acesso DESC
            LIMIT 10
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/frequentador/<int:id_frequentador>')
def obter_frequentador(id_frequentador):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT tipo FROM frequentadores WHERE id_frequentador = %s",
            (id_frequentador,)
        )
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            return jsonify({"mensagem": "Frequentador não encontrado"}), 404

        return jsonify(result), 200

    except Exception as e:
        print("Erro ao buscar frequentador:", e)
        return jsonify({"mensagem": "Erro no servidor"}), 500












@app.route("/frequentadores", methods=["GET"])
def listar_frequentadores():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_frequentador, nome, tipo FROM frequentadores")
    frequentadores = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(frequentadores)


UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/historico', methods=['GET'])
def historico_acessos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        busca = request.args.get('busca', '').strip()

        query = """
   SELECT 
    a.id_acesso,
    a.data_acesso,
    a.hora_acesso,
    f.tipo AS tipo_usuario,
    v.matricula,
    a.estado
FROM acessos a
LEFT JOIN veiculos_cadastrado v ON a.id_carro = v.id_veiculo
LEFT JOIN frequentadores f ON a.id_frequentador = f.id_frequentador
ORDER BY a.data_acesso DESC, a.hora_acesso DESC;
    """

        params = []
        if busca:
            query += " WHERE v.matricula LIKE %s"
            params.append(f"%{busca}%")

        query += " ORDER BY a.data_acesso DESC, a.hora_acesso DESC"
        cursor.execute(query, params)

        acessos = cursor.fetchall()

        # Converter hora_acesso para string por segurança
        for a in acessos:
            a["hora_acesso"] = str(a["hora_acesso"])

        return jsonify(acessos)

    except Exception as e:
        print("Erro ao filtrar histórico:", e)
        return jsonify({"erro": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/api/acessos', methods=['POST'])
def inserir_acesso():
    try:
        dados = request.get_json()
        id_veiculo = dados.get('id_veiculo')
        estado = dados.get('estado', 'Pendente')  # Estado inicial
        detalhes = dados.get('detalhes', None)     # Opcional
        imagem = dados.get('imagem', None)         # Opcional (pode ser caminho da imagem ou nome do arquivo)

        if not id_veiculo:
            return jsonify({"status": "erro", "mensagem": "Campo id_veiculo é obrigatório."}), 400

        conn = conectar()
        cursor = conn.cursor()

        query = """
            INSERT INTO acessos (id_veiculo, data_acesso, hora_acesso, estado, detalhes, imagem)
            VALUES (%s, CURDATE(), CURTIME(), %s, %s, %s)
        """
        cursor.execute(query, (id_veiculo, estado, detalhes, imagem))
        conn.commit()

        return jsonify({"status": "sucesso", "mensagem": "Acesso inserido com sucesso!"})

    except Exception as e:
        print("Erro ao inserir acesso:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/acessos/<int:id_acesso>', methods=['DELETE'])
def remover_acesso(id_acesso):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        # Verifica se o acesso existe antes de deletar
        cursor.execute("SELECT * FROM acessos WHERE id_acesso = %s", (id_acesso,))
        acesso = cursor.fetchone()

        if not acesso:
            return jsonify({"status": "erro", "mensagem": "Acesso não encontrado."}), 404

        # Remove o acesso
        cursor.execute("DELETE FROM acessos WHERE id_acesso = %s", (id_acesso,))
        conn.commit()

        return jsonify({
            "status": "sucesso",
            "mensagem": "Acesso removido com sucesso!",
            "acesso_removido": acesso  # Retorna o acesso deletado (opcional)
        })

    except Exception as e:
        print("Erro ao remover acesso:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ROTAS CRUD para permissões de veículos

# Criar permissão
@app.route('/api/permissoes', methods=['POST'])
def criar_permissao():
    dados = request.get_json()
    id_veiculo = dados.get('id_veiculo')
    validade = dados.get('validade')  # formato: AAAA-MM-DD
    horario = dados.get('horario_acesso')
    id_frequentador = dados.get('id_frequentador')

    if not all([id_veiculo, validade, horario, id_frequentador]):
        return jsonify({"status": "erro", "mensagem": "Campos obrigatórios faltando."}), 400

    conn = conectar()
    cursor = conn.cursor()
    query = """
        INSERT INTO permissoes_acesso (id_veiculo, validade, horario_acesso, id_frequentador)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (id_veiculo, validade, horario, id_frequentador))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "sucesso", "mensagem": "Permissão criada com sucesso!"})


# Ler permissões
# ROTA: Listar permissões
@app.route('/api/permissoes', methods=['GET'])
def listar_permissoes():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                p.id_permissao,
                p.validade,
                p.horario_acesso,
                f.id_frequentador,
                f.nome AS nome_frequentador,
                f.tipo AS tipo_usuario,
                v.id_veiculo,
                v.matricula,
                v.proprietario
            FROM permissoes_acesso p
            JOIN veiculos_cadastrado v ON p.id_veiculo = v.id_veiculo
            JOIN frequentadores f ON p.id_frequentador = f.id_frequentador
        """)

        dados = cursor.fetchall()
        return jsonify(dados)

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# rota para atualizar permissao com sincronizacao de tabelas relacionadas
@app.route('/api/permissoes/<int:id>', methods=['PUT'])
def atualizar_permissao(id):
    dados = request.json
    validade = dados.get('validade')
    horario_acesso = dados.get('horario_acesso')
    tipo_usuario = dados.get('tipo_usuario')
    estado_veiculo = dados.get('estado_veiculo')
    id_frequentador = dados.get('id_frequentador')

    if not all([tipo_usuario, estado_veiculo, id_frequentador]):
        return jsonify({'status': 'erro', 'mensagem': 'Dados obrigatórios incompletos.'}), 400

    conn = conectar()
    cursor = conn.cursor()

    try:
        # Atualiza permissões (apenas se valor for fornecido)
        cursor.execute("""
            UPDATE permissoes_acesso
            SET validade = %s, horario_acesso = %s
            WHERE id_permissao = %s
        """, (validade, horario_acesso, id))

        # Recupera o id_veiculo da permissão
        cursor.execute("""
            SELECT id_veiculo
            FROM permissoes_acesso
            WHERE id_permissao = %s
        """, (id,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({'status': 'erro', 'mensagem': 'Permissão não encontrada.'}), 404

        id_veiculo = resultado[0]

        # Atualiza o tipo de frequentador
        cursor.execute("""
            UPDATE frequentadores
            SET tipo = %s
            WHERE id_frequentador = %s
        """, (tipo_usuario, id_frequentador))

        # Atualiza o estado do veículo
        cursor.execute("""
            UPDATE veiculos_cadastrado
            SET estado = %s
            WHERE id_veiculo = %s
        """, (estado_veiculo, id_veiculo))

        # Atualiza acessos vinculados (corrigido: usar id_frequentador)
        cursor.execute("""
            UPDATE acessos
            SET estado = 'Autorizado'
            WHERE id_carro = %s AND id_frequentador = %s
        """, (id_veiculo, id_frequentador))

        conn.commit()
        return jsonify({'status': 'sucesso', 'mensagem': 'Permissão e dados sincronizados com sucesso.'})

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'status': 'erro', 'mensagem': str(err)}), 500
    finally:
        cursor.close()
        conn.close()


        
# Remover permissão
@app.route('/api/permissoes/<int:id>', methods=['DELETE'])
def deletar_permissao(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissoes_acesso WHERE id_permissao=%s", (id,))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({"status": "erro", "mensagem": "Permissão não encontrada."}), 404

    cursor.close()
    conn.close()
    return jsonify({"status": "sucesso", "mensagem": "Permissão removida."})



UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def formatar_matricula_ao_padrao_angola(texto):
    """
    Converte 'LD1234AB' → 'LD-12-34-AB' se o formato estiver correto.
    """
    # Remove espaços, hífens, etc., só para garantir
    texto = texto.strip().replace("-", "").upper()

    # Aceita somente LD + 4 dígitos + 2 letras
    match = re.match(r'^LD(\d{4})([A-Z]{2})$', texto)
    if match:
        digitos = match.group(1)  # ex: '4817'
        letras = match.group(2)   # ex: 'HO'
        return f"LD-{digitos[:2]}-{digitos[2:]}-{letras}"
    return None  # inválido

@app.route('/api/analisar-imagem', methods=['POST'])
def analisar_imagem():
    print("➡️ Início da rota /api/analisar-imagem")

    arquivo = request.files.get("imagem")
    if not arquivo:
        return jsonify({"status": "erro", "mensagem": "Imagem não recebida"}), 400

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        caminho = os.path.join(UPLOAD_FOLDER, secure_filename(arquivo.filename))
        arquivo.save(caminho)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar imagem"}), 500

    # OCR da matrícula
    try:
        matricula_raw = detectar_matricula(caminho)
        matricula = formatar_matricula_ao_padrao_angola(matricula_raw)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": "Erro ao processar matrícula"}), 500

    if not matricula:
        return jsonify({
            "status": "erro",
            "mensagem": f"Matrícula inválida: '{matricula_raw}'"
        }), 400

    # Buscar no banco
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM veiculos_cadastrado WHERE matricula = %s AND estado = 'Ativo'",
            (matricula,)
        )
        veiculo = cursor.fetchone()
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": "Erro no banco de dados"}), 500

    # Inserir na tabela de acessos
    try:
        cursor = conn.cursor()

        if veiculo:
            id_carro = veiculo["id_veiculo"]
            id_frequentador = veiculo["id_frequentador"]
            estado = "Autorizado"
            fraude = 0
        else:
            id_carro = None
            id_frequentador = None
            estado = "Recusado"
            fraude = 0

        query = """
            INSERT INTO acessos (id_carro, id_frequentador, estado, data_acesso, hora_acesso, imagem, fraude, modelo_detectado)
            VALUES (%s, %s, %s, CURDATE(), CURTIME(), %s, %s, %s)
        """
        cursor.execute(query, (
            id_carro, id_frequentador, estado, caminho, fraude, None
        ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "erro", "mensagem": "Erro ao salvar acesso"}), 500
    finally:
        cursor.close()
        conn.close()

    # Resposta final
    if veiculo:
        return jsonify({
            "status": "permitido",
            "mensagem": "✅ Acesso Liberado",
            "matricula": matricula,
            "veiculo": veiculo
        }), 200
    else:
        return jsonify({
            "status": "negado",
            "mensagem": "❌ Acesso Negado — veículo não registrado",
            "matricula": matricula
        }), 200




if __name__ == '__main__':
    print("Arquivo correto está rodando.")
    app.run(debug=True)





