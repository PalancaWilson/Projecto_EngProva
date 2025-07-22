document.addEventListener('DOMContentLoaded', carregarDashboard);

function carregarDashboard() {
    fetch('/api/dashboard')
        .then(res => res.json())
        .then(data => {
            document.getElementById('total-autorizados').textContent = data.autorizados;
            document.getElementById('tentativas-negadas').textContent = data.negadas;
            document.getElementById('acessos-hoje').textContent = data.acessos_hoje;

            desenharGrafico(data);
            carregarUltimosAcessos();
        })
        .catch(err => {
            console.error('Erro ao carregar dashboard:', err);
            alert('Erro ao carregar dados do dashboard');
        });
}

function desenharGrafico(data) {
    const ctx = document.getElementById('grafico-acessos').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Autorizados', 'Negados', 'Hoje'],
            datasets: [{
                data: [data.autorizados, data.negadas, data.acessos_hoje],
                backgroundColor: ['#3a5af7', '#f87171', '#22c55e']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function carregarUltimosAcessos() {
    fetch('/ultimos-acessos')
        .then(res => res.json())
        .then(acessos => {
            const tabela = document.getElementById('tabela-acessos');
            tabela.innerHTML = '';

            acessos.forEach(acesso => {
                const linha = document.createElement('tr');

                const tdHora = document.createElement('td');
                tdHora.classList.add('py-2');
                tdHora.textContent = acesso.hora;

                const tdMatricula = document.createElement('td');
                tdMatricula.textContent = acesso.matricula;

                const tdEstado = document.createElement('td');
                const spanEstado = document.createElement('span');
                spanEstado.classList.add('text-xs', 'px-2', 'py-1', 'rounded');

                if (acesso.estado === 'Autorizado') {
                    spanEstado.classList.add('bg-green-100', 'text-green-700');
                    spanEstado.textContent = 'Autorizado';
                } else {
                    spanEstado.classList.add('bg-red-100', 'text-red-700');
                    spanEstado.textContent = 'Negado';
                }

                tdEstado.appendChild(spanEstado);

                linha.appendChild(tdHora);
                linha.appendChild(tdMatricula);
                linha.appendChild(tdEstado);

                tabela.appendChild(linha);
            });
        })
        .catch(err => {
            console.error('Erro ao carregar últimos acessos:', err);
        });
}

// Botão de ver alertas
document.getElementById('ver-alertas').addEventListener('click', () => {
    alert('🔔 Nenhum alerta crítico no momento!');
});

// Botão de logout
document.getElementById('logout').addEventListener('click', () => {
    if (confirm('Deseja sair?')) {
        window.location.href = '/logout';
    }
});
