document.addEventListener('DOMContentLoaded', function() {
    const calculateBtn = document.getElementById('calculate-btn');
    const resultContainer = document.getElementById('result-container');
    const carbonResult = document.getElementById('carbon-result');
    const resultMessage = document.getElementById('result-message');
    const tipsContainer = document.getElementById('tips-container');
    
    calculateBtn.addEventListener('click', async function() {

        const energy = parseFloat(document.getElementById('energy').value) || 0;
        const transport = parseFloat(document.getElementById('transport').value) || 0;
        const meat = parseFloat(document.getElementById('meat').value) || 0;
        const waste = parseFloat(document.getElementById('waste').value) || 0;
        const flights = parseFloat(document.getElementById('flights').value) || 0;
        
        const energyFootprint = energy * 0.5 * 12; 
        const transportFootprint = transport * 0.2 * 12; 
        const meatFootprint = meat * 15 * 52; 
        const wasteFootprint = waste * 2 * 52; 
        const flightsFootprint = flights * 1000;
        
        const totalFootprint = (energyFootprint + transportFootprint + meatFootprint + wasteFootprint + flightsFootprint) / 1000;
        
        carbonResult.textContent = totalFootprint.toFixed(2) + ' toneladas de CO₂/ano';
        
        let name = '';
        try {
            const me = await fetch('/api/me').then(r=>r.json());
            if (me && me.authenticated) name = me.nome || me.username || '';
        } catch(e) {}
        if (totalFootprint < 4) {
            resultMessage.textContent = `Parabéns${name ? ', ' + name : ''}! Sua pegada de carbono está abaixo da média.`;
            resultMessage.style.backgroundColor = '#4CAF50';
            resultMessage.style.color = 'white';
        } else if (totalFootprint < 8) {
            resultMessage.textContent = `Sua pegada${name ? ', ' + name : ''} está na média. Há espaço para melhorias!`;
            resultMessage.style.backgroundColor = '#FFC107';
            resultMessage.style.color = 'black';
        } else {
            resultMessage.textContent = `Sua pegada está acima da média${name ? ', ' + name : ''}. Considere mudar alguns hábitos.`;
            resultMessage.style.backgroundColor = '#F44336';
            resultMessage.style.color = 'white';
        }
        
        resultContainer.style.display = 'block';
        tipsContainer.style.display = 'block';

        try {
            await fetch('/api/calcular-pegada', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transporte: transport, // km/mês
                    energia: energy, // kWh/mês
                    alimentacao: Math.round(meat), // refeições c/ carne por semana
                    lixo: Math.round(waste) // kg/semana
                })
            });
        } catch (e) {}
    });
});