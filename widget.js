(function() {
    const container = document.createElement('div');
    container.style.cssText = 'position:fixed;bottom:20px;right:20px;padding:20px;background:#fff;box-shadow:0 10px 25px rgba(0,0,0,0.2);border-radius:8px;z-index:9999;font-family:sans-serif;width:250px;';

    container.innerHTML = `
        <h4 style="margin-top:0">Subscribe</h4>
        <input type="email" id="fr-email" placeholder="Email" style="width:100%;margin-bottom:10px;padding:8px;box-sizing:border-box;" />
        <!-- Honeypot Field (Invisible) -->
        <input type="text" id="fr-honeypot" style="display:none;" />
        <button id="fr-submit" style="width:100%;padding:10px;background:#000;color:#fff;border:none;border-radius:4px;cursor:pointer;">Send</button>
        <div id="fr-msg" style="display:none;color:green;margin-top:10px;font-size:12px;">Saved!</div>
    `;
    
    document.body.appendChild(container);

    document.getElementById('fr-submit').addEventListener('click', () => {
        const email = document.getElementById('fr-email').value;
        const honeypot = document.getElementById('fr-honeypot').value;
        
        // Ensure this matches your local API URL
        fetch('http://localhost:8000/api/submit/w_123', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, honeypot })
        })
        .then(res => {
            if(!res.ok) throw new Error("Validation or Spam Error");
            return res.json();
        })
        .then(() => {
            document.getElementById('fr-msg').style.display = 'block';
            document.getElementById('fr-email').value = '';
        })
        .catch(err => alert(err.message));
    });
})();
