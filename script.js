async function findCheapest(){

    try{

        document.getElementById("results").innerHTML =
            "<p>🔍 Hledám nejlevnější nabídky...</p>";

        const response = await fetch(
            "http://127.0.0.1:5001/api/search",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    items:selectedProducts
                })
            }
        );

        if(!response.ok){

            throw new Error(
                "HTTP chyba: " + response.status
            );

        }

        const data = await response.json();

        let html = "";

        if(!data.items || data.items.length === 0){

            html = `
                <div class="result-card">
                    Nebyly nalezeny žádné výsledky.
                </div>
            `;

        }else{

            data.items.forEach(item => {

                html += `
                    <div class="result-card">

                        <strong>${item.product}</strong>

                        <br>

                        🏪 ${item.shop}

                        <br>

                        💰 ${item.price} Kč

                        <br>

                        📅 ${item.valid_until}

                    </div>
                `;

            });

            html += `
                <div class="total">
                    Celkem: ${data.total} Kč
                </div>
            `;

        }

        document.getElementById("results").innerHTML =
            html;

    }
    catch(error){

        console.error(error);

        document.getElementById("results").innerHTML = `
            <div class="result-card">
                ❌ Chyba: ${error.message}
            </div>
        `;
    }
}