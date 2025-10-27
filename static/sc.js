async function kuldes() {
    const nyersSzoveg = document.getElementById("rawText").value;
    const eredmeny = document.getElementById("result");

    if (!nyersSzoveg) {
        eredmeny.innerHTML = "<p style='color:red'>Kérlek, írj be valamit először!</p>";
        return;
    }

    eredmeny.innerHTML = "<p>Generálás folyamatban...</p>";

    try {
        const response = await fetch("/emailFormat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ rawText: nyersSzoveg })
        });

        if (!response.ok) {
            const errorText = await response.text();
            eredmeny.innerHTML = `<p style='color:red'>Hiba a szerver oldalon: ${errorText}</p>`;
            return;
        }

        const adat = await response.json();

        if (adat.error) {
            eredmeny.innerHTML = `<p style='color:red'>Hiba: ${adat.error}</p>`;
            return;
        }

        eredmeny.innerHTML = `
            <h3> Kész e-mail</h3>
            <p><strong>Tárgy:</strong> ${adat.subject || "—"}</p>
            <p><strong>Szöveg:</strong><br>${(adat.body || "").replace(/\n/g, "<br>")}</p>
            <p><strong>Aláírás:</strong> ${adat.signature || ""}</p>
        `;

    } catch (error) {
        eredmeny.innerHTML = `<p style='color:red'>Hálózati hiba vagy kivétel: ${error}</p>`;
    }
}
